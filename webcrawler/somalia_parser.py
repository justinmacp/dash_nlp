from urllib.request import urlopen as uReq
import json
from bs4 import BeautifulSoup
import os
from datetime import date
import pathlib

today = date.today()
dstr = today.strftime("%Y%m%d")
namespaces = {"dc": "http://purl.org/dc/elements/1.1/", "content": "http://purl.org/rss/1.0/modules/content/"}
ARTICLES = 'ARTICLES'
COUNTRY = 'SOMALIA'
NEWSSOURCE = 'HIIRAAN'


# SCRAPERS FOR HTML PAGES

def scrape_hiiraan_article_urls():
    url = 'https://www.hiiraan.com/'
    req = uReq(url)
    soup = BeautifulSoup(req.read(), "html.parser")
    req.close()
    article_links = []
    for div in soup.find_all('div', class_='featured'):
        for h1 in div.find_all('h1'):
            a = h1.find("a")
            article_links.append(a['href'])
    for div in soup.find_all('div', class_='featured-story2'):
        for h1 in div.find_all('h1'):
            a = h1.find("a")
            article_links.append(a['href'])
    return article_links


def scrape_hiiraan_article(url_list):
    url = 'https://www.hiiraan.com/'
    texts = []
    for i in range(0, len(url_list)):
        number = url_list[i][16:]
        req = uReq(url + url_list[i])
        soup = BeautifulSoup(req.read(), "html.parser")
        req.close()
        title_str = 'crayon article-titre-' + number
        title = soup.find('h1', class_=title_str).get_text()
        print(title)
        class_str = 'crayon article-texte-' + number + ' texte entry-content'
        article = soup.find('div', class_=class_str)
        article_text = ''
        for p in article.find_all('p'):
            article_text += (p.get_text() + ' ')
        texts.append({'title': title,
                      'text': article_text,
                      'url': url + url_list[i],
                      'country': 'SD',
                      'source': 'Sudan Times'})
    pathlib.Path(os.path.join(ARTICLES, COUNTRY, NEWSSOURCE)).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(ARTICLES, COUNTRY, NEWSSOURCE, 'sdt_latest_news_' + dstr + '.json'), 'w') as outfile:
        json.dump(texts, outfile)


def main():
    print("### HIIRAAN ###")
    a = scrape_hiiraan_article_urls()
    print(a)
    scrape_hiiraan_article(a)


if __name__ == "__main__":
    main()
