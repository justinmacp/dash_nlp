"""Dynamic Topic Modelling
This file exposes a class that wraps gensim's `DtmModel` to add utils for
exploring topics, and it can be run as a script to train and persist a DTM.
"""
import argparse
import datetime
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from collections import defaultdict
from gensim.corpora.dictionary import Dictionary
from gensim.models.wrappers import DtmModel
from gensim.matutils import corpus2csc
from scipy.spatial.distance import cosine
from scipy.sparse import save_npz, load_npz
from scipy.stats import linregress

from src import HOME_DIR
from src.utils.corpus import Corpus
from src.utils.wiki2vec import wiki2vec


class Dtm(DtmModel):

    @classmethod
    def load(cls, fname):
        model_path = os.path.join(HOME_DIR, 'models', fname, 'dtm.gensim')
        obj = super().load(model_path)
        obj.term_counts = load_npz(
            os.path.join(HOME_DIR, 'models', fname, 'term_counts.npz')
        ).todense()
        obj.normalized_term_counts = \
            (obj.term_counts + 1) / \
            (obj.term_counts.sum(axis=0) + obj.term_counts.shape[0])
        obj._assign_corpus()
        obj.topic_assignments = np.apply_along_axis(np.argmax, 1, obj.gamma_)
        return obj

    def _assign_corpus(self):
        """Assign corpus object to the model"""
        self.original_corpus = Corpus()
        assert self.original_corpus.debates.shape[0] == self.gamma_.shape[0]
        self.time_slice_labels = self.original_corpus.debates.year.unique()

    def show_topic(self, topic, time, topn=10, use_relevance_score=True,
                   lambda_=.6, **kwargs):
        """Show top terms from topic
        This override `show_topic` to account for lambda normalizing as
        described in "LDAvis: A method for visualizing and interpreting topics":
        https://nlp.stanford.edu/events/illvi2014/papers/sievert-illvi2014.pdf
        The score returned is computed as
            lambda_ * log(phi_kw) + (1 - lambda_) * log(phi_kw / pw)
        where
            phi_kw : Conditional probability of term `w` in topic `k`.
            pw : Marginal probability of term `w`.
        Parameters
        ----------
        topic : int
        time : int
            Time slice specified as index, e.g. 0, 1, ...
        topn : int
        use_relevance_score : bool
            If True, apply the lambda_ based relevance scoring. Else, fall back
            to the default `show_topic` behavior.
        lambda_ : float
            The lambda constant to use in relevance scoring. Must be in the
            range [0,1].
        Returns
        -------
        list of (float, str)
        """
        if not use_relevance_score:
            return super().show_topic(topic, time=time, topn=topn, **kwargs)
        conditional = super().show_topic(topic, time, topn=None, **kwargs)
        marginal = {
            self.id2word[term_id]: marg[0]
            for term_id, marg in enumerate(
                self.normalized_term_counts[:, time].tolist())}
        weighted = [
            (lambda_ * np.log(cond) + \
             (1 - lambda_) * np.log(cond / marginal[term]), term)
            for cond, term in conditional
        ]
        return sorted(weighted, reverse=True)[:topn]

    def term_distribution(self, term, topic):
        """Extracts the probability over each time slice of a term/topic
        pair."""
        word_index = self.id2word.token2id[term]
        topic_slice = np.exp(self.lambda_[topic])
        topic_slice = topic_slice / topic_slice.sum(axis=0)
        return topic_slice[word_index]

    def term_variance(self, topic):
        """Finds variance of probability over time for terms for a given topic.
        High variance terms are more likely to be interesting than low variance
        terms."""
        p = np.exp(self.lambda_[topic]) / \
            np.exp(self.lambda_[topic]).sum(axis=0)
        variances = np.var(p, axis=1)
        order = np.argsort(variances)[::-1]
        terms = np.array([term for term, _
                          in sorted(self.id2word.token2id.items(),
                                    key=lambda x: x[1])])[order]
        variances = variances[order]
        return list(zip(terms, variances))

    def term_slope(self, topic):
        """Finds slope of probability over time for terms for a given topic.
        This is useful for roughly identifying terms that are rising or
        declining in popularity over time."""
        p = np.exp(self.lambda_[topic]) / \
            np.exp(self.lambda_[topic]).sum(axis=0)
        slopes = np.apply_along_axis(
            lambda y: linregress(x=range(len(y)), y=y).slope, axis=1, arr=p)
        order = np.argsort(slopes)
        terms = np.array([term for term, _
                          in sorted(self.id2word.token2id.items(),
                                    key=lambda x: x[1])])[order]
        slopes = slopes[order]
        return list(zip(terms, slopes))

    def plot_terms(self, topic, terms, title=None, name=None, hide_y=True):
        """Creates a plot of term probabilities over time in a given topic."""
        fig, ax = plt.subplots()
        plt.style.use('fivethirtyeight')
        for term in terms:
            ax.plot(
                self.time_slice_labels, self.term_distribution(term, topic),
                label=term)
        leg = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        if hide_y:
            ax.set_yticklabels([])
        ax.set_ylabel('Probability')
        if title:
            ax.set_title(title)
        if name:
            fig.savefig(
                name, dpi=300, bbox_extra_artists=(leg,), bbox_inches='tight')
        return fig, ax

    def top_term_table(self, topic, slices, topn=10):
        """Returns a dataframe with the top n terms in the topic for each of
        the given time slices."""
        data = {}
        for time_slice in slices:
            time = np.where(self.time_slice_labels == time_slice)[0][0]
            data[time_slice] = [
                term for p, term
                in self.show_topic(topic, time=time, topn=topn)
            ]
        return pd.DataFrame(data)

    def top_label_table(self, topic, slices, topn=10):
        """Returns a dataframe with the top n labels in the topic for each of
        the given time slices."""
        data = {}
        for time_slice in slices:
            data[time_slice] = [
                x[0] for x
                in self.label_topic(topic, time_slice, topn)
            ]
        return pd.DataFrame(data)

    def summary(self, slices, topn=10):
        """Prints a summary of all the topics"""
        for topic in range(self.num_topics):
            print('Topic %d' % topic)
            print(self.top_term_table(topic, slices, topn))
            print()

    def topic_summary(self, topic, n=20):
        """Prints the top N terms by variance, increasing slope, and decreasing
        slope."""
        print('Variance\n---------')
        for row in self.term_variance(topic)[:n]:
            print(row)
        slopes = self.term_slope(topic)
        print('\nSlope (positive)\n----------')
        for row in slopes[-n:][::-1]:
            print(row)
        print('\nSlope (negative)\n----------')
        for row in slopes[:n]:
            print(row)

    def top_entities(self, i, time_slice=None, n=10):
        """Gets the top entities among documents for the given topic
        Documents are "assigned" to a topic based on the most probable topic
        learned by the model. Entities are counted in these documents as well
        as the complement set of docs not assigned to this topic, and top
        entities are sorted according to the differential between the percentage
        of mentions in docs in the positive and complement set of docs.
        Parameters
        ----------
        i : int
            Topic index
        time_slice : int, optional
            Time slice specified as absolute year.
        n : int
            Number of top entities to return
        Returns
        -------
        list of tuples
            Tuples of the form:
                (entity, positive count, negative count, count differential)
        """
        document_entity_matrix, entity_dictionary = \
            self.original_corpus.corpus_entity_matrix()
        condition = (self.topic_assignments == i)
        negative_condition = (self.topic_assignments != i)
        if time_slice is not None:
            condition = condition & \
                        (self.original_corpus.debates.year == time_slice)
            negative_condition = negative_condition & \
                                 (self.original_corpus.debates.year == time_slice)
        indices = condition.nonzero()[0]
        negative_indices = negative_condition.nonzero()[0]
        counts = (document_entity_matrix[:, indices] > 0).sum(axis=1)
        negative_counts = \
            (document_entity_matrix[:, negative_indices] > 0).sum(axis=1)
        count_diff = counts / indices.shape[0] - \
                     negative_counts / negative_indices.shape[0]
        topn = np.argsort(-count_diff.flatten()).tolist()[0][:n]
        return [(entity_dictionary[i], counts[i, 0], negative_counts[i, 0],
                 count_diff[i, 0]) for i in topn]

    def label_topic(self, i, time_slice=None, n=10, condense=None):
        """Assign label to a topic
        Parameters
        ----------
        i : int
            Topic index
        time_slice: int, optional
            Absolute time slice. If not specified, return a time agnostic label
            for the topic.
        n : int
        condense : int, optional
            Return a condense string version of the name with this many
            entities in it.
        Returns
        -------
        list or str
        """
        top_entities = self.top_entities(i, time_slice, n)
        if time_slice is not None:
            top_terms = self.show_topic(
                i, np.where(self.time_slice_labels == time_slice)[0][0], n)
        else:
            # In the case where no time slice is specified, aggregate scores
            # across the top n in each time slice to come up with a top term
            # list across all time slices. This could probably be improved.
            scores = defaultdict(float)
            for t in range(len(self.time_slices)):
                top_terms = self.show_topic(i, t, n)
                # Need to adjust scores up based on the min score, so that
                # terms aren't rewarded for not being in the top n list.
                min_score = min(s for s, _ in top_terms)
                for score, term in top_terms:
                    scores[term] += (score - min_score)
            top_terms = [
                (score, term) for term, score in sorted(
                    scores.items(), key=lambda x: -x[1])[:n]]

        final_candidates = []
        for candidate in top_entities:
            scores = np.array([
                1 - cosine(
                    wiki2vec.get_entity_vector(candidate[0]),
                    wiki2vec.get_word_vector(term))
                for _, term in top_terms if wiki2vec.get_word(term)
            ])
            final_candidates.append((candidate[0], scores.mean()))
        final_candidates = sorted(final_candidates, key=lambda x: -x[1])
        if condense:
            return '; '.join(
                [title for title, _ in final_candidates[:condense]])
        else:
            return final_candidates


def train(args, output_dir):
    """Build the corpus, trains the DTM, and saves the model to the output
    dir."""
    corpus = Corpus()

    # Create the dictionary.
    dictionary = Dictionary(corpus.debates.bag_of_words)
    dictionary.filter_extremes(no_below=100)

    # Save empirical term distribution within each time step.
    term_counts = corpus2csc(
        corpus.debates.groupby('year')
            .agg({'bag_of_words': 'sum'})
            .bag_of_words
            .apply(dictionary.doc2bow))
    save_npz(
        os.path.join(output_dir, 'term_counts.npz'), term_counts)

    # Train and save dtm.
    time_slices = corpus.debates.groupby('year').size()
    dtm_corpus = corpus.debates.bag_of_words.apply(dictionary.doc2bow)
    model = Dtm(
        args.executable, corpus=dtm_corpus, id2word=dictionary,
        num_topics=args.num_topics,
        time_slices=time_slices.values, rng_seed=args.random_seed
    )
    model.save(os.path.join(output_dir, 'dtm.gensim'))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o', '--output',
        help='The name of the directory to output the model to (must not ' +
             'already exist). This will become a subdirectory under ' +
             '`models/`.',
        type=str,
        default=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'))
    parser.add_argument(
        '-n', '--num-topics',
        help='The number of topics.',
        type=int,
        default=15)
    parser.add_argument(
        '-e', '--executable',
        help='The path to the DTM executable.',
        type=str,
        default='/home/lukelefebure/dtm/dtm/dtm')
    parser.add_argument(
        '-r', '--random-seed',
        help='Random seed.',
        type=int,
        default=5278)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    output_dir = os.path.join(HOME_DIR, 'models', args.output)
    os.mkdir(output_dir)
    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s',
        level=logging.INFO,
        filename=os.path.join(output_dir, 'log'))
    train(args, output_dir)