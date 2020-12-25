from urllib.request import urlopen as uReq
import json
from bs4 import BeautifulSoup
import os
from datetime import date
import pathlib
import re


today = date.today()
dstr = today.strftime("%Y%m%d")
namespaces = {"dc": "http://purl.org/dc/elements/1.1/", "content": "http://purl.org/rss/1.0/modules/content/"}
ARTICLES = 'ARTICLES'
SUDAN = 'SUDAN'
SDT = 'SDT'
SUNA = 'SUNA'


# SCRAPERS FOR HTML PAGES


def scrape_st_article_urls():
    url = 'https://www.sudantribune.com/'
    req = uReq(url)
    soup = BeautifulSoup(req.read(), "html.parser")
    req.close()
    article_links = []
    for div in soup.find_all('div', class_='latest_news'):
        for h1 in div.find_all('h1'):
            a = h1.find("a")
            article_links.append(a['href'])
    return article_links


def scrape_st_article(url_list):
    url = 'https://www.sudantribune.com/'
    texts = []
    for i in range(0, len(url_list)):
        month = None
        day = None
        year = None
        city = None
        number = url_list[i][16:]
        req = uReq(url + url_list[i])
        soup = BeautifulSoup(req.read(), "html.parser")
        req.close()
        title_str = 'crayon article-titre-' + number
        title = soup.find('h1', class_=title_str).get_text()
        class_str = 'crayon article-texte-' + number + ' texte entry-content'
        article = soup.find('div', class_=class_str)
        article_text = ''
        no_paragraphs = 0
        for p in article.find_all('p'):
            paragraph = p.get_text()
            paragraph = paragraph.replace('\n', '')
            if no_paragraphs == 0:
                if paragraph is not None:
                    match = re.match(r"(?P<month>[A-Za-z]+) (?P<day>[0-9]{1,2}),? (?P<year>[0-9]{4}) \((?P<city>.+)\)", paragraph)
                    if match:
                        month = match.group('month')
                        day = match.group('day')
                        year = match.group('year')
                        city = match.group('city')
                    no_paragraphs += 1
            article_text += (paragraph + '\n')
        texts.append({'title': title,
                      'text': article_text,
                      'url': url + url_list[i],
                      'country': 'SD',
                      'source': 'Sudan Times',
                      'month': month,
                      'day': day,
                      'year': year,
                      'city': city})
    pathlib.Path(os.path.join(ARTICLES, SUDAN, SDT)).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(ARTICLES, SUDAN, SDT, 'sdt_latest_news_' + dstr + '.json'), 'w') as outfile:
        json.dump(texts, outfile)


def scrape_suna_article_urls():
    url = 'https://suna-sd.net/en'
    req = uReq(url)
    soup = BeautifulSoup(req.read(), "html.parser")
    req.close()
    article_links = []
    # find the link to the article on the top right
    tr = soup.find('div', class_='content_top_right')
    a = tr.find('a')
    article_links.append(a['href'])
    # find the rest of the article links
    bl = soup.find('div', class_='content_bottom_left')
    for link in bl.find_all('li'):
        a = link.find('a')
        article_links.append(a['href'])
    return article_links


def scrape_suna_article(url_list):
    url = 'https://suna-sd.net'
    texts = []
    for i in range(0, len(url_list)):
        month = None
        day = None
        year = None
        city = None
        req = uReq(url + url_list[i])
        soup = BeautifulSoup(req.read(), "html.parser")
        req.close()
        title = soup.find('h2', class_='post_titile').get_text()
        content = soup.find('div', class_='single_page_content')
        article_text = ''
        no_paragraphs = 0
        # the text starts with the headline in the first paragraph. We don't need this
        for p in content.find_all('p'):
            paragraph = p.get_text()
            paragraph = paragraph.replace('\n', '')
            if no_paragraphs == 1:
                print(paragraph)
                if paragraph is not None:
                    match = re.match("", paragraph)
                    if match:
                        print('hello')
            if not no_paragraphs == 0:
                article_text += (paragraph + '\n')
            no_paragraphs += 1
        texts.append({'title': title,
                      'text': article_text,
                      'url': url + url_list[i],
                      'country': 'SD',
                      'source': 'SUNA',
                      'month': month,
                      'day': day,
                      'year': year,
                      'city': city})
    pathlib.Path(os.path.join(ARTICLES, SUDAN, SUNA)).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(ARTICLES, SUDAN, SUNA, 'suna_latest_news_' + dstr + '.json'), 'w') as outfile:
        json.dump(texts, outfile)


def main():
    # print("### SUDAN TRIBUNE ###")
    # a = scrape_st_article_urls()
    # scrape_st_article(a)
    print("### SUNA-SD ###")
    b = scrape_suna_article_urls()
    scrape_suna_article(b)


if __name__ == "__main__":
    main()
