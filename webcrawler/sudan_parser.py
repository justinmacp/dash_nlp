from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup
from datetime import date
import re
from text_processing.text_processing_utils import convert_to_raw_text

today = date.today()
dstr = today.strftime("%Y%m%d")
namespaces = {"dc": "http://purl.org/dc/elements/1.1/", "content": "http://purl.org/rss/1.0/modules/content/"}
ARTICLES = 'ARTICLES'
SUDAN = 'SUDAN'
SDT = 'SDT'
SUNA = 'SUNA'

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
          'December']


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
                    match = re.match(r"(?P<month>[A-Za-z]+) (?P<day>[0-9]{1,2}),? (?P<year>[0-9]{4}) \((?P<city>["
                                     r"A-Z]+)\)",
                                     paragraph)
                    paragraph = re.sub(r"(?P<month>[A-Za-z]+) (?P<day>[0-9]{1,2}),? (?P<year>[0-9]{4}) \((?P<city>["
                                       r"A-Z]+)\) -", '', paragraph)
                    if match:
                        month = match.group('month')
                        day = match.group('day')
                        year = match.group('year')
                        city = match.group('city')
                    no_paragraphs += 1
            article_text += (paragraph + '\n')
        if year is not None and month is not None and day is not None:
            clean_text = convert_to_raw_text(article_text)
            clean_title = convert_to_raw_text(title)
            texts.append({'title': clean_title,
                          'article_text': clean_text,
                          'url': url + url_list[i],
                          'country': 'SD',
                          'newspaper': 'Sudan Times',
                          'publication_date': date(year=int(year), month=months.index(month) + 1, day=int(day)),
                          'city': city})
    return texts


def main():
    a = scrape_st_article_urls()
    texts = scrape_st_article(a)


if __name__ == "__main__":
    main()
