import os
import codecs
import requests
from bs4 import BeautifulSoup

def main():
    fin = codecs.open(os.path.join(os.curdir, 'member_urls.txt'), mode='r', encoding='utf-8')
    rows = fin.readlines()
    fin.close()
    for row in rows:
        crawl(row[:-1])

def crawl(row):
    url_list = [row]
    while url_list:
        url = url_list.pop()
        res = requests.get(url, headers={'User-Agent': 'Chrome'})
        if res.status_code != 200:
            return
        soup = BeautifulSoup(res.text, 'lxml')
        processing(soup)
        prev_month = soup.find(attrs={'class': 'prev'})
        if prev_month:
            url_list.append(prev_month.get('href'))

def processing(soup):
    days = [a.get('href') for a in reversed(soup
                                            .find(attrs={'id': 'daytable'})
                                            .findAll('a'))]
    print([day for day in days])

if __name__ == '__main__':
    main()
