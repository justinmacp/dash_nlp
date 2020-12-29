import ldanalysis
import webcrawler.sudan_parser
import webcrawler.afghanistan_parser
import json
from datetime import date
import os


today = date.today()
dstr = today.strftime("%Y%m%d")
ARTICLES = 'ARTICLES'
SUDAN = 'SUDAN'
SDT = 'SDT'
SUNA = 'SUNA'
AFGHANISTAN = 'AFGHANISTAN'
AT = 'AT'


def sudan_main():
    sudan_parser.main()
    with open(os.path.join(ARTICLES, SUDAN, SDT, 'sdt_latest_news_' + dstr + '.json'), 'r') as infile:
        body = json.load(infile)
    content = [d['text'] for d in body]
    titles = [d['title'] for d in body]
    with open(os.path.join(ARTICLES, SUDAN, SUNA, 'suna_latest_news_' + dstr + '.json'), 'r') as infile:
        body = json.load(infile)
    content.extend([d['text'] for d in body])
    titles.extend([d['title'] for d in body])
    # text preprocessing: tokenization
    vocab, X = ldanalysis.tokenize(content)
    ldanalysis.ldanalysis(X, vocab, titles, SUDAN)


def afghanistan_main():
    print('here0')
    webcrawler.afghanistan_parser.main()
    print('here1')
    with open(os.path.join(ARTICLES, AFGHANISTAN, AT, 'at_latest_news_' + dstr + '.json'), 'r') as infile:
        body = json.load(infile)
    content = [d['text'] for d in body]
    titles = [d['title'] for d in body]
    # text preprocessing: tokenization
    vocab, X = ldanalysis.tokenize(content)
    ldanalysis.ldanalysis(X, vocab, titles, AFGHANISTAN)


if __name__ == "__main__":
    print('here1')
    afghanistan_main()
