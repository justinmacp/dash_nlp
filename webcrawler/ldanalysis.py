import numpy as np
import lda
import lda.datasets
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
import pandas as pd
from datetime import date
import os
import pathlib

ARTICLES = 'ARTICLES'
today = date.today()
dstr = today.strftime("%Y%m%d")


class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, articles):
        return [self.wnl.lemmatize(t) for t in word_tokenize(articles)]


def ldanalysis(X, vocab, titles, country):
    model = lda.LDA(n_topics=10, n_iter=2000, random_state=1)
    model.fit(X)
    plt.plot(model.loglikelihoods_[5:])
    plt.show()
    topic_word = model.topic_word_
    n_top_words = 8
    pandas_data = []
    for i, topic_dist in enumerate(topic_word):
        print(np.argsort(topic_dist))
        topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
        topic_words = np.append(topic_words,0)
        pandas_data.append(topic_words)
        print('Topic {}: {}'.format(i, ' '.join(topic_words)))
    doc_topic = model.doc_topic_
    
    # count number of times a topic is discussed
    for i in range(0, len(doc_topic)):
        print("{} (top topic: {})".format(titles[i], doc_topic[i].argmax()))
        count = int(pandas_data[doc_topic[i].argmax()][n_top_words])
        count += 1
        pandas_data[doc_topic[i].argmax()][n_top_words] = count
        
    # output topic frequency
    for i in range(0, len(pandas_data)):
        count = int(pandas_data[i][n_top_words])
        count /= len(doc_topic)
        pandas_data[i][n_top_words] = count
        
    df = pd.DataFrame(pandas_data)
    df.columns.name = dstr
    pathlib.Path(os.path.join(ARTICLES, country, 'LDA')).mkdir(parents=True, exist_ok=True)
    df.to_csv(os.path.join(ARTICLES, country, 'LDA', dstr + '.csv'))


def tokenize(docs):
    vec = CountVectorizer(tokenizer=LemmaTokenizer(),
                          stop_words = 'english', # works
                          max_df = 0.5) # works
    X = vec.fit_transform(docs)
    vocab = vec.get_feature_names()
    print(vocab)
    return vocab, X


if __name__ == "__main__":
    docs = ['why hello there', 'omg hello pony', 'she went there? omg']
    tokenize(docs)
