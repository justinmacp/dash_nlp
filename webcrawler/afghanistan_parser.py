from urllib.request import urlopen as uReq
import json
from bs4 import BeautifulSoup
import os
from datetime import date
import pathlib
from urllib.error import HTTPError

today = date.today()
dstr = today.strftime("%Y%m%d")
ARTICLES = 'ARTICLES'
AFGHANISTAN = 'AFGHANISTAN'
AT = 'AT'


def scrape_at_category_urls():
    url = 'http://www.afghanistantimes.af/'
    try:
        req = uReq(url)
    except HTTPError as e:
        print('Error: ', e.code)
        return []
    else:
        soup = BeautifulSoup(req.read(), "html.parser")
        req.close()
        category_links = []
        for content in soup.find_all('div', class_='content'):
            for titles in content.find_all('div', class_='cat-box-title'):
                for h2 in titles.find_all('h2'):
                    a = h2.find("a")
                    category_links.append(a['href'])
        return category_links


def scrape_at_category_article_urls(category_links):
    article_links = []
    for i in range(0, len(category_links)):
        try:
            req = uReq(category_links[i])
        except HTTPError as e:
            print("Error: ", e.code)
        else:
            soup = BeautifulSoup(req.read(), "html.parser")
            req.close()
            for content in soup.find_all('div', class_='content'):
                for titles in content.find_all('article', class_='item-list'):
                    for h2 in titles.find_all('h2'):
                        a = h2.find("a")
                        article_links.append(a['href'])
    return article_links


def scrape_at_article(url_list):
    texts = []
    for i in range(0, len(url_list)):
        try:
            req = uReq(url_list[i])
        except HTTPError as e:
            print("Error: ", e.code)
        else:
            soup = BeautifulSoup(req.read(), "html.parser")
            req.close()
            title = soup.find('h1', class_='name post-title entry-title').get_text()
            article = soup.find('div', class_='entry')
            article_text = ''
            for p in article.find_all('p'):
                article_text += (p.get_text() + ' ')
            texts.append({'title': title,
                          'text': article_text,
                          'url': url_list[i],
                          'country': 'AFG',
                          'source': 'Afghanistan Times'})
    pathlib.Path(os.path.join(ARTICLES, AFGHANISTAN, AT)).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(ARTICLES, AFGHANISTAN, AT, 'at_latest_news_' + dstr + '.json'), 'w') as outfile:
        json.dump(texts, outfile)


def main():
    c = scrape_at_category_urls()
    a = scrape_at_category_article_urls(c)
    scrape_at_article(a)


if __name__ == '__main__':
    main()
