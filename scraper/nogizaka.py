import json

import requests
from bs4 import BeautifulSoup

from scraper import storage


class Blog(object):
    """
    乃木坂公式ブログをスクレイピングする
    """


    URL_PREFIX = 'http://blog.nogizaka46.com/'
    HEADERS = {
        'User-Agent': 'Chrome',
    }


    def __init__(self, base_url=None, member=None, replace=False):
        if base_url is None and member is not None:
            self.member = member
            self.base_url = Blog.URL_PREFIX + self.member
        elif base_url is not None and member is None:
            self.base_url = base_url
            self.member = self.base_url.rsplit('/', 1)[1]
        elif base_url is None and member is None:
            print('error')
            return
        else:
            self.base_url = base_url
            self.member = member
        self.replace = replace
        self.headers = Blog.HEADERS
        self.detail_urls = []
        self.detail_list_url = 'member/' + self.member + '/detail_urls.txt'
        res = requests.get(self.base_url, headers=self.headers)
        if res.status_code != 200:
            raise Exception()


    @staticmethod
    def create_members_list(path=None):
        """
        全メンバー情報を更新し, 全記事に対してスクレイピングを行い結果をストレージに保存する
        """
        if path is None:
            path = 'members.txt'

        res = requests.get(Blog.URL_PREFIX, headers=Blog.HEADERS)
        if res.status_code != 200:
            return
        soup = BeautifulSoup(res.text, 'lxml')
        unit_tags = soup.find(attrs={'id': 'sidemember'}).findAll(attrs={'class': 'unit'})
        members = [unit_tag.find('a').get('href').rsplit('/', 1)[1] for unit_tag in unit_tags]
        raw = '\n'.join(members)
        return storage.upload_file(raw, path, 'text/plain')


    @staticmethod
    def run_all(path=None, replace=False):
        """
        全メンバーの全記事のURL情報を更新し, 全記事に対してスクレイピングを行い結果をストレージに保存する
        """
        if path is None:
            path = 'members.txt'

        members = storage.read_lines(path)
        for member in members:
            blog = Blog(member=member, replace=replace)
            blog.run_all_by_member()


    def run_all_by_member(self):
        """
        メンバーの全記事のURL情報を更新し, 全記事に対してスクレイピングを行い結果をストレージに保存する
        """
        self.run_crawling_urls_by_member()
        self.run_scraping()


    @staticmethod
    def run_crawling_urls_all(path=None, replace=False):
        """
        全メンバーの全記事のURL情報を更新しストレージに保存する
        """
        if path is None:
            path = 'members.txt'

        members = storage.read_lines(path)
        for member in members:
            blog = Blog(member=member, replace=replace)
            blog.run_crawling_urls_by_member()


    def run_crawling_urls_by_member(self):
        """
        メンバーの全記事のURL情報を更新しストレージに保存する
        """
        self.crawl_urls()
        return self.upload_detail_urls(self.detail_list_url)


    def run_scraping(self):
        """
        メンバーブログの全記事に対してスクレイピングを行い結果をストレージに保存する
        """
        if not storage.is_exists_file(self.detail_list_url):
            self.run_crawling_urls_by_member()

        detail_urls = storage.read_lines(self.detail_list_url)
        for detail_url in detail_urls:
            file_name = 'member/' + self.member + '/post/' + detail_url.rsplit('/', 1)[1]
            self.upload_post_detail(detail_url, file_name)


    def upload_post_detail(self, url, dst_filename):
        """
        author, title, contentをJson形式でストレージに格納する
        """

        if self.replace is False:
            if storage.is_exists_file(dst_filename):
                return

        res = requests.get(url, headers=self.headers)
        if res.status_code != 200:
            return

        soup = BeautifulSoup(res.text, 'lxml')
        author = soup.find(class_='author').text
        title = soup.find(class_='entrytitle').text
        content = soup.find(class_='entrybody')
        output = json.dumps({
            'postUrl': url,
            'author': author,
            'title': title,
            'content': content.prettify(),
        }, ensure_ascii=False)

        return storage.upload_file(
            output,
            dst_filename,
            'application/json',
        )


    def crawl_urls(self):
        """
        全記事のURLをdetail_urlsに格納する
        """
        month_urls = self._get_month_urls(self.base_url)
        for month in month_urls:
            self._add_detail_link(month)


    def _get_month_urls(self, base_url):
        res = requests.get(base_url, headers=self.headers)
        if res.status_code != 200:
            return
        soup = BeautifulSoup(res.text, 'lxml')
        month_tags = soup.find(attrs={'id': 'sidearchives'}).find('select').findAll('option')
        month_urls = [option['value'] for option in month_tags[1:]]
        return month_urls


    def _add_detail_link(self, url):
        res = requests.get(url, headers=self.headers)
        if res.status_code != 200:
            return
        soup = BeautifulSoup(res.text, 'lxml')
        day_table = soup.find(id='daytable')
        detail_urls = [detail_link.get('href') for detail_link in day_table.find_all('a')]
        self.detail_urls.extend(detail_urls)


    def upload_detail_urls(self, dst_filename):
        """
        detail_urls情報をストレージに保存する
        """
        raw = '\n'.join(self.detail_urls)
        return storage.upload_file(raw, dst_filename, 'text/plain')
