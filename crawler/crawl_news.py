import requests
import re
from queue import Queue
from urllib.error import HTTPError, URLError
import json
import threading
from bs4 import BeautifulSoup
import time

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/100.0.4896.127 Safari/537.36'}


class Frontier:
    def __init__(self):
        self.naver_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}&start={}'
        self.google_url = 'https://www.google.com/search?q={}&tbm=nws&start={}&hl=en-US'
        self.permission_site = ['', 'BBC', 'Reuters', 'The Independent', 'CNBC', 'Forbes', 'NBC News', 'Al Jazeera',
                                'CNN', 'Forbes']

    def getNewsLink_en(self, keyword, number, queue):
        keyword = re.sub(' ', '%20', keyword)
        count = 0
        flag = False
        for add in self.permission_site:
            if flag:
                break
            if add != '':
                keyword += '%20' + add
            for i in range(3):
                if flag:
                    break
                url = self.google_url.format(keyword, i)
                try:
                    get_url = requests.get(url=url, headers=header)
                except HTTPError or URLError:
                    break
                bs = BeautifulSoup(get_url.text, 'lxml')
                articles = bs.find('div', id='search').find_all('div', {'class': 'xuvV6b BGxR7d'})
                for article in articles:
                    site = article.find('div', {'class': 'CEMjEf NUnG9d'}).text
                    if site in self.permission_site:
                        url = article.find('a', {'class': 'WlydOe'}).attrs['href']
                        title = article.find('div', {'class': 'mCBkyc y355M ynAwRc MBeuO nDgy9d'}).text
                        parameters = {
                            'title': title,
                            'site': site,
                            'url': url,
                            'lan': 'en',
                        }
                        print('extract link: {}'.format(url))
                        queue.put(parameters)
                        count += 1
                        if count >= number:
                            flag = True
        return

    def getNewsLink_ko(self, keyword, number, queue):
        keyword = re.sub(' ', '%20', keyword)
        count = 0
        for i in range(1000):
            url = self.naver_url.format(keyword, (i * 10 + 1))
            try:
                get_url = requests.get(url=url, headers=header)
            except HTTPError or URLError:
                break
            bs = BeautifulSoup(get_url.text, 'lxml')
            main_newses = bs.find_all('div', {'class': 'news_area'})
            sub_newses = bs.find_all('span', {'class': 'sub_wrap'})
            for main_news in main_newses:
                info = main_news.find('div', {'class': 'info_group'})
                site = info.find('a').text
                site = re.sub('언론사 선정', '', site)
                naver_link = info.find('a', {'cru': re.compile('https\:\/\/news\.naver\.com\/')})
                if naver_link is not None:
                    print(naver_link)
                    naver_link = naver_link.attrs['cru']
                else:
                    continue
                main_link = main_news.find('a', {'class': 'news_tit'})
                title = main_link.attrs['title']
                main_link = main_link.attrs['href']
                # 어떤 식으로 링크를 추가할지 생각, 작업큐를 사용하거나 이것도 쿠버네티스를 사용하여 배포하거나
                parameters = {
                    'title': title,
                    'site': 'naver',
                    'url': naver_link,
                    'lan': 'ko',
                    'source-link': main_link
                }
                print('extract link: {}'.format(naver_link))
                queue.put(parameters)
                count += 1
            for sub_news in sub_newses:
                link = sub_news.find('a', {'class': 'elss sub_tit'})
                title = link.attrs['title']
                main_link = link.attrs['href']
                naver_link = sub_news.find('a', href=re.compile('https\:\/\/n\.news\.naver\.com\/'))
                if naver_link is not None:
                    naver_link = naver_link.attrs['href']
                else:
                    continue
                parameters = {
                    'title': title,
                    'site': 'naver',
                    'url': naver_link,
                    'lan': 'ko',
                    'source-link': main_link
                }
                queue.put(parameters)
                count += 1
            if count >= number:
                return


class handler:
    def __init__(self):
        self.results = []
        self.url_queue = Queue()
        self.crawl_server = ['http://192.168.1.13:9000/crawl',
                             'http://192.168.1.14:9000/crawl',
                             'http://192.168.1.15:9000/crawl',
                             'http://192.168.1.16:9000/crawl',
                             'http://192.168.1.11:9000/crawl']

    def startCrawl(self, role, keyword, number=1):
        start = time.time()
        frontier = Frontier()
        if role == 'news ko':
            t = threading.Thread(target=frontier.getNewsLink_ko, args=(keyword, number, self.url_queue,))
            t.start()
        elif role == 'news en':
            t = threading.Thread(target=frontier.getNewsLink_en, args=(keyword, number, self.url_queue,))
            t.start()
        count = 0
        threads = []
        while True:
            if not self.url_queue.empty():
                count += 1
                parameters = self.url_queue.get()
                less = count % len(self.crawl_server)
                crawl_server = self.crawl_server[less]
                t = threading.Thread(target=self.postCrawlServer, args=(crawl_server, parameters,))
                t.start()
                threads.append(t)
            if (time.time() - start) > (number * 0.3 + 1) or count >= number:
                break
            time.sleep(0.0005)

        for thread in threads:
            thread.join()
        return self.results

    def postCrawlServer(self, crawl_server, parameters):
        # print('post crawl server: {}, {}'.format(crawl_server, parameters))
        res = requests.post(crawl_server, data=json.dumps(parameters))
        j = json.loads(res.text)
        if j['success']:
            result = j['result']
            self.results.append(result)
