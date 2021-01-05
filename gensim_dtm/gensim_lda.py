# Importing modules
from pprint import pprint
import os
from wordcloud import WordCloud
import gensim
import nltk

import gensim.corpora as corpora
import pyLDAvis.gensim
import pickle
import pyLDAvis
from database.sqlalchemy_utils import *

os.chdir('..')
# Read data into papers
conn = create_connection('localhost', 'root', 'Ju5Ky1M@', 'news')
papers = pd.read_sql("SELECT * FROM collection", conn)
# Print head
print(papers.head())


def sent_to_words(sentences):
    for sentence in sentences:
        yield gensim.utils.simple_preprocess(str(sentence), deacc=True)


def perform_lda(news_dataframe, num_topics=5):
    news_dataframe['paper_text_processed'] = news_dataframe['title'] + ' ' + news_dataframe['article_text']
    data = news_dataframe.paper_text_processed.values.tolist()
    data_words = list(sent_to_words(data))

    # Create Dictionary
    id2word = corpora.Dictionary(data_words)
    # Create Corpus
    texts = data_words
    # Term Document Frequency
    corpus = [id2word.doc2bow(text) for text in texts]
    tfidf = gensim.models.TfidfModel(corpus, id2word)
    low_value = 0.25
    for i in range(0, len(corpus)):
        bow = corpus[i]
        tfidf_ids = [id for id, value in tfidf[bow]]
        bow_ids = [id for id, value in bow]
        low_value_words = [id for id, value in tfidf[bow] if value < low_value]
        words_missing_in_tfidf = [id for id in bow_ids if id not in tfidf_ids]
        new_bow = [b for b in bow if b[0] not in low_value_words and b[0] not in words_missing_in_tfidf]
        corpus[i] = new_bow
    lda_model = gensim.models.LdaMulticore(corpus=corpus, id2word=id2word, num_topics=num_topics)
    return lda_model


if __name__ == '__main__':
    model = perform_lda()
