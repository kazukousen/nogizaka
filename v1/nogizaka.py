import os
import uuid
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

class Blog():

    def __init__(self, member):
        '''
        member: 西野七瀬ならnanase.nishino
        '''
        self.member = member
        self.base_url = 'http://blog.nogizaka46.com/{}'.format(self.member)
        self.urls = [self.base_url]
        self.detail_urls = []
        self.headers = {'User-Agent': 'sample Vivaldi'}
        load_dotenv(os.path.join(os.curdir, '.env'))

    def add_detail_contents(self, detail_url):
        response = requests.get(detail_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        data = dict()
        data['url'] = detail_url
        data['title'] = soup.find(class_='entrytitle').text
        data['published'] = detail_url[-8:]
        content = soup.find(class_='entrybody')
        data['content'] = content
        data['author'] = soup.find(class_='author').text

        img_tags = content.find_all('img')
        for it in img_tags:
            img_url = ['src']
            response = requests.get(img_url, headers=self.headers)
            file_name = uuid.uuid4().hex
            file_path = self.member + '.' + file_name
            with open(os.path.join(os.curdir, os.path.join('img', '{}.jpg'.format(file_path))), 'wb') as f:
                f.write(response.content)
            try:
                query = 'INSERT INTO images (url, file_path, detail_id) \
                    VALUES (%s, %s, %s)'
                cur.execute(query, (img_url, file_path, detail_id))
                self.con.commit()
                print('inserted image {}, OK'.format(file_name))
            except MySQLdb.Error as e:
                try:
                    print("Error [{}]: didn't insert {}. {}".format(e.args[0], detail_id, e.args[1]))
                except IndexError:
                    print("Error : didn't insert {}. {}".format(detail_id, str(e)))


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
            cur.execute("INSERT INTO detail_urls(url) VALUES('{}', '{}')".format(detail_url, self.member))
        self.con.commit()

    def detail_array_from_dbs(self):
        cur = self.con.cursor()
        cur.execute("SELECT url FROM detail_urls WHERE author LIKE '{}'".format(self.member))
        rows = cur.fetchall()
        self.detail_urls = [row for row in rows]

def main():
    nanamin = Nanamin()
    nanamin.crawl_urls()
    nanamin.output_detail_urls()

if __name__=='__main__':
    main()
