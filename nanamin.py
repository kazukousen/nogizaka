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

    def create_tables(self):
        tables = ['detail_urls', 'detail_contents', 'images']
        cur = self.con.cursor()
        try:
            cur.execute('create table {}(id int auto_increment not null, url text, index(id))'.format(tables[0]))
            self.con.commit()
            print('created {}, OK.'.format(tables[0]))
        except:
            print("error: didn't create {}.".format(tables[0]))

        try:
            cur.execute('create table {}(id int auto_increment not null, url text, title text, published datetime, \
                content text, index(id))'.format(tables[1]))
            self.con.commit()
            print('created {}, OK.'.format(tables[1]))
        except:
            print("error: didn't create {}.".format(tables[1]))

    def add_detail_contents(self, detail_url):
        response = requests.get(detail_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find(class_='entrytitle').text
        published = detail_url[-8:]
        content = soup.find(class_='entrybody').text
        cur = self.con.cursor()
        try:
            cur.execute("INSERT INTO detail_contents (url, title, published, content)\
                VALUES ('{url}', '{title}', '{published}', '{content}')".format(
                    url=detail_url, title=title, published=published, content=content))
            self.con.commit()
            print('inserted {}, OK.'.format(published))
        except:
            print("Error: didn't insert {}.".format(published))

    def add_all_details(self):
        for detail_url in self.detail_urls:
            self.add_detail_contents(detail_url)
        print('Done all.')

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

    def detail_array_from_dbs(self):
        cur = self.con.cursor()
        cur.execute('select * from detail_urls')
        rows = cur.fetchall()
        self.detail_urls = [row[1] for row in rows]

def main():
    nanamin = Nanamin()
    nanamin.crawl_urls()
    nanamin.output_detail_urls()

if __name__=='__main__':
    main()
