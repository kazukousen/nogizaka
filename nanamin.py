import requests
from bs4 import BeautifulSoup
import MySQLdb
import os
from dotenv import load_dotenv

class Nanamin():

    def __init__(self):
        self.base_url = 'http://blog.nogizaka46.com/nanami.hashimoto/?d=201702'
        self.urls = [self.base_url]
        self.detail_urls = []
        self.headers = {'User-Agent': 'sample Vivaldi'}
        load_dotenv(os.path.join(os.curdir, '.env'))
        self.con = MySQLdb.connect(os.environ.get('MYSQL_HOST'),
            os.environ.get('MYSQL_USER'),
            os.environ.get('MYSQL_PASSWD'),
            os.environ.get('MYSQL_DB'))

    def crawl_urls(self):
        while self.urls:
            url = self.urls.pop()
            self._add_detail_link(url)
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'lxml')
            prev_month = soup.find(class_='prev')
            if prev_month:
                prev_month_url = prev_month.get('href')
                self.urls.append(prev_month_url)
            else:
                break

    def _add_detail_link(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        day_table = soup.find(id='daytable')
        self.detail_urls.extend([detail_link.get('href') for detail_link in reversed(day_table.find_all('a'))])

    def output_detail_urls(self):
        for detail_url in self.detail_urls:
            print(detail_url)

    def insert_detail_urls(self):
        cur = self.con.cursor()
        for detail_url in self.detail_urls:
            cur.execute("INSERT INTO detail_urls(url) VALUES('{}')".format(detail_url))
        self.con.commit()

    def show_detail_dbs(self):
        cur = self.con.cursor()
        cur.execute('select * from detail_urls')
        rows = cur.fetchall()
        for row in rows:
            print(row)

def main():
    nanamin = Nanamin()
    nanamin.crawl_urls()
    nanamin.output_detail_urls()

if __name__=='__main__':
    main()
