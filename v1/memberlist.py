import os
import codecs
import requests
from bs4 import BeautifulSoup

def main():
    base_url = 'http://blog.nogizaka46.com/'
    headers = {'User-Agent': 'sample Vivaldi'}

    # parse
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # write URL of each member's top page to the file
    member_urls = [base_url + a.get('href')[2:] for a in soup
                   .find(attrs={'id': 'sidemember'})
                   .find(attrs={'class': 'clearfix'})
                   .findAll('a')]

    fout = codecs.open(os.path.join(os.curdir, 'member_urls.txt'), mode='w', encoding='utf-8')
    for row in member_urls:
        fout.write(row + '\n')
    fout.close()

if __name__ == '__main__':
    main()
