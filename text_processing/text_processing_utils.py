import re
from nltk.stem import WordNetLemmatizer
import nltk
from nltk import word_tokenize, pos_tag
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords

nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

lemmatizer = WordNetLemmatizer()

stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])


def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc))
             if word not in stop_words] for doc in texts]


def convert_to_raw_text(text):
    lemmatized_text = [lemmatizer.lemmatize(i, j[0].lower()).lower() if j[0].lower() in ['a', 'n', 'v'] else lemmatizer.lemmatize(i) for i, j in pos_tag(word_tokenize(text))]
    lemmatized_text = remove_stopwords(lemmatized_text)
    lemmatized_text_without_empty_lists = [x for x in lemmatized_text if x != []]
    lemmatized_individual_word_list = [x[0] for x in lemmatized_text_without_empty_lists]
    lemmatized_text_lowercase = ' '.join(lemmatized_individual_word_list)
    print(lemmatized_text_lowercase)
    return lemmatized_text_lowercase