import requests
from bs4 import BeautifulSoup
import MySQLdb
import os
import uuid
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
        self.con = MySQLdb.connect(
            host=os.environ.get('MYSQL_HOST')
            , user=os.environ.get('MYSQL_USER')
            , passwd=os.environ.get('MYSQL_PASSWD')
            , db=os.environ.get('MYSQL_DB')
            , charset=os.environ.get('MYSQL_CHARSET'))

    def close(self):
        self.con.close()

    def create_tables(self):
        tables = ['detail_urls', 'detail_contents', 'images']
        cur = self.con.cursor()
        try:
            cur.execute('create table {}(id int auto_increment not null, url text, author text, index(id))'.format(tables[0]))
            self.con.commit()
            print('created {}, OK.'.format(tables[0]))
        except:
            print("error: didn't create {}.".format(tables[0]))

        try:
            cur.execute('create table {}(id int auto_increment not null, url text, title text, published datetime, \
                content text, author text, index(id))'.format(tables[1]))
            self.con.commit()
            print('created {}, OK.'.format(tables[1]))
        except:
            print("error: didn't create {}.".format(tables[1]))

        try:
            cur.execute('create table {}(id int auto_increment not null, url text, file_path text, \
                detail_id int not null, index(id), \
                foreign key (detail_id) references detail_contents (id))'.format(tables[2]))
            self.con.commit()
            print('created {}, OK.'.format(tables[2]))
        except:
            print("error: didn't create {}.".format(tables[2]))


    def add_detail_contents(self, detail_url):
        response = requests.get(detail_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find(class_='entrytitle').text
        published = detail_url[-8:]
        content = soup.find(class_='entrybody')
        author = soup.find(class_='author').text
        cur = self.con.cursor()
        query = """
        INSERT INTO detail_contents (url, title, published, content, author)
        VALUES (%s, %s, %s, %s, %s)
        """[1:-1]
        try:
            cur.execute(query, (detail_url, title, published, content, author))
            detail_id = cur.lastrowid
            self.con.commit()
            print('inserted {}, OK.'.format(published))
        except MySQLdb.Error as e:
            try:
                print("Error [{}]: didn't insert {}. {}".format(e.args[0], published, e.args[1]))
            except IndexError:
                print("Error : didn't insert {}. {}".format(published, str(e)))
        img_tags = content.find_all('img')
        for img_tag in img_tags:
            img_url = img_tag['src']
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
