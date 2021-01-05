import re


def convert_to_raw_text(text):
    punctuation_free_text = re.sub('[,.!?]', '', text)
    return punctuation_free_text.lower()