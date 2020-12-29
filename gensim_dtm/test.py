"""Word, sentence, and paragraph tokenizers for the General Debate corpus."""
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import PunktSentenceTokenizer, RegexpTokenizer


class SentenceTokenizer(PunktSentenceTokenizer):
    pass


class ParagraphTokenizer(object):
    """A simple paragraph tokenizer that creates a paragraph break whenever
    the newline character appears between two sentences."""

    sentence_tokenizer = SentenceTokenizer()

    def span_tokenize(self, text):
        """Returns a list of paragraph spans."""
        sentence_spans = list(self.sentence_tokenizer.span_tokenize(text))
        breaks = []
        for i in range(len(sentence_spans) - 1):
            sentence_divider = text[sentence_spans[i][1]:sentence_spans[i + 1][0]]
            if '\n' in sentence_divider:
                breaks.append(i)
        paragraph_spans = []
        start = 0
        for break_idx in breaks:
            paragraph_spans.append((start, sentence_spans[break_idx][1]))
            start = sentence_spans[break_idx + 1][0]
        paragraph_spans.append((start, sentence_spans[-1][1]))
        return paragraph_spans


class WordTokenizer(RegexpTokenizer):
    """A word tokenizer that lowercases and lemmatizes words."""

    lemmatizer = WordNetLemmatizer()
    stopwords = set(stopwords.words('english'))

    def __init__(self, pattern=r'\w+'):
        super().__init__(pattern)

    def tokenize(self, text):
        """Returns a list of lowercased and lemmatized words."""

        # Paragraphs often have numbered sections, e.g. "35.\tThe utilization
        # of the United Nations...", so remove that text to prevent these
        # numbers from entering the vocabulary.
        cleaned_text = re.sub(r'^[0-9]+\.', '', text)

        words = super().tokenize(cleaned_text)
        words = [self.lemmatizer.lemmatize(word.lower()) for word in words
                 if word.lower() not in self.stopwords]
        return words
