import re
import requests
from bs4 import BeautifulSoup

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/102.0.0.0 Safari/537.36'}
independent_tag = '#main'
cnbc_tag = '#RegularArticle-ArticleBody-5'
bbc_tag = '#main-content > div.ssrcss-1ocoo3l-Wrap.e42f8511 > div > div.ssrcss-rgov1k-MainColumn.e1sbfw0p0 > article'
cnn_tag = 'body > div.pg-right-rail-tall.pg-wrapper > article > div.l-container > div.pg-rail-tall__wrapper'
jazeera_tag = '#main-content-area'
nbc_tag = '#content > div:nth-child(7) > div > div > article > div > ' \
          'div.article-body__section.layout-grid-container.article-body__last-section > ' \
          'div.article-body.layout-grid-item.layout-grid-item--with-gutter-s-only.grid-col-10-m.grid-col-push-1-m' \
          '.grid-col-6-xl.grid-col-push-2-xl.article-body--custom-column > div.article-body__content '
forbes_tag = '#article-stream-0 > div:nth-child(2) > div.middleRightRail > div.body-container'
reuters_tag = '#main-content > article > div > div > div >div.article-body__content__17Yit.paywall-article'
cbssports_tag = '#Article-body > div.Article-bodyContent'

extract_tag_en = {
    'The Independent': independent_tag,
    'CNBC': cnbc_tag,
    'BBC': bbc_tag,
    'CNN': cnn_tag,
    'Al Jazeera': jazeera_tag,
    'NBC News': nbc_tag,
    'Forbes': forbes_tag,
    'Reuters': reuters_tag
}


def extract_content(title, url, site, language):
    if language == 'ko':
        return extract_korean_news(title, url, site)
    elif language == 'en':
        return extract_english_news(title, url, site)
    print()


def extract_korean_news(title, url, site):
    try:
        get_url = requests.get(url=url, headers=header)
    except:
        return
    bs = BeautifulSoup(get_url.text, 'lxml')
    content = bs.find('div', id='dic_area')
    if content is None:
        return
    unexpectes = [content.find('strong')] + content.find_all('span', {'class': 'end_photo_org'})
    for exception in unexpectes:
        if exception is not None:
            exception.extract()
    content = content.text
    for i in range(2):
        content = re.sub('  ', ' ', content)
    content = re.sub('\n|\t|\xa0', ' ', content)
    return {'site': site, 'title': title, 'content': content}


def extract_english_news(title, url, site):
    try:
        get_url = requests.get(url=url, headers=header)
    except:
        return
    bs = BeautifulSoup(get_url.text, 'lxml')
    extract_tag = extract_tag_en[site]
    selects = bs.select(extract_tag)
    content = []
    if len(selects) > 0:
        for select in selects:
            sentences = select.find_all('p')
            if site == 'cnn':
                sentences += select.find_all('div')
            for sentence in sentences:
                content.append(sentence.text)
        content = ' '.join(content)
        return {'site': site, 'title': title, 'content': content}
    return

