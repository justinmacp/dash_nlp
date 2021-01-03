# Importing modules
from pprint import pprint
import os
import re
from wordcloud import WordCloud
import gensim
from gensim.utils import simple_preprocess
import nltk
from nltk.corpus import stopwords
import gensim.corpora as corpora
import pyLDAvis.gensim
import pickle
import pyLDAvis
from database.sqlalchemy_utils import *
import matplotlib.pyplot as plt

nltk.download('stopwords')

os.chdir('..')
# Read data into papers
conn = create_connection('localhost', 'root', 'Ju5Ky1M@', 'news')
papers = pd.read_sql("SELECT * FROM collection", conn)
# Print head
print(papers.head())


def convert_to_raw_text(text):
    punctuation_free_text = text.map(lambda x: re.sub('[,.!?]', '', x))
    return punctuation_free_text.map(lambda x: x.lower())


papers['paper_text_processed'] = convert_to_raw_text(papers['article_text'])
# Print out the first rows of papers
print(papers['paper_text_processed'].head())
print(papers['paper_text_processed'].shape)

# Join the different processed titles together.
long_string = ','.join(list(papers['paper_text_processed'].values))
# Create a WordCloud object
wordcloud = WordCloud(background_color="white", max_words=5000, contour_width=3, contour_color='steelblue')
# Generate a word cloud
wordcloud.generate(long_string)
# Visualize the word cloud
wordcloud.to_image()
plt.show()

stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'sudan', 'sudanese', 'said', 'al'])


def sent_to_words(sentences):
    for sentence in sentences:
        # deacc=True removes punctuations
        yield gensim.utils.simple_preprocess(str(sentence), deacc=True)


def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc))
             if word not in stop_words] for doc in texts]


data = papers.paper_text_processed.values.tolist()
data_words = list(sent_to_words(data))
# remove stop words
data_words = remove_stopwords(data_words)
print(data_words[:1][0][:30])

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
    low_value_words = []  # reinitialize to be safe. You can skip this.
    tfidf_ids = [id for id, value in tfidf[bow]]
    bow_ids = [id for id, value in bow]
    low_value_words = [id for id, value in tfidf[bow] if value < low_value]
    words_missing_in_tfidf = [id for id in bow_ids if
                              id not in tfidf_ids]  # The words with tf-idf socre 0 will be missing

    new_bow = [b for b in bow if b[0] not in low_value_words and b[0] not in words_missing_in_tfidf]
# View
print(corpus[:1][0][:30])

# number of topics
num_topics = 4
# Build LDA model
lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                       id2word=id2word,
                                       num_topics=num_topics)
# Print the Keyword in the 10 topics
pprint(lda_model.print_topics())
doc_lda = lda_model[corpus]

# Visualize the topics
LDAvis_data_filepath = os.path.join('./results/ldavis_prepared_' + str(num_topics))
# # this is a bit time consuming - make the if statement True
# # if you want to execute visualization prep yourself
LDAvis_prepared = pyLDAvis.gensim.prepare(lda_model, corpus, id2word)
with open(LDAvis_data_filepath, 'wb') as f:
    pickle.dump(LDAvis_prepared, f)
# load the pre-prepared pyLDAvis data from disk
with open(LDAvis_data_filepath, 'rb') as f:
    LDAvis_prepared = pickle.load(f)
pyLDAvis.save_html(LDAvis_prepared, './results/ldavis_prepared_' + str(num_topics) + '.html')
pyLDAvis.show(LDAvis_prepared)
LDAvis_prepared
