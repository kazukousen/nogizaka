import logging
import json

from scraper import get_model, storage
from scraper.nogizaka import Blog
from flask import current_app
from google.cloud import pubsub
import psq
import requests
from bs4 import BeautifulSoup


# [START get_books_queue]
publisher_client = pubsub.PublisherClient()
subscriber_client = pubsub.SubscriberClient()


def get_books_queue():
    project = current_app.config['PROJECT_ID']

    return psq.Queue(
        publisher_client, subscriber_client, project,
        'books', extra_context=current_app.app_context)
# [END get_books_queue]


# [START process_scraping]
def process_scraping_by_member(member):
    scraper = Blog(member=member)
    scraper.run_all_by_member()
# [END process_scraping]


# [START process_crawling_all]
def process_scraping_all(member):
    Blog.run_all('member_urls.txt')
# [END process_crawling_all]


# [START process_book]
def process_book(book_id):
    """
    Handles an individual Bookshelf message by looking it up in the
    model, querying the Google Books API, and updating the book in the model
    with the info found in the Books API.
    """

    model = get_model()

    book = model.read(book_id)

    if not book:
        logging.warn("Could not find book with id {}".format(book_id))
        return

    if 'title' not in book:
        logging.warn("Can't process book id {} without a title."
                     .format(book_id))
        return

    logging.info("Looking up book with title {}".format(book[
                                                        'title']))

    # If the new book data has thumbnail images and there isn't currently a
    # thumbnail for the book, then copy the image to cloud storage and update
    # the book data.
    if not book.get('imageUrl') and 'imageLinks' in new_book_data:
        new_img_src = new_book_data['imageLinks']['smallThumbnail']
        book['imageUrl'] = download_and_upload_image(
            new_img_src,
            "{}.jpg".format(book['title']))

    model.update(book, book_id)
# [END process_book]




def download_and_upload_image(src, dst_filename):
    """
    Downloads an image file and then uploads it to Google Cloud Storage,
    essentially re-hosting the image in GCS. Returns the public URL of the
    image in GCS
    """
    r = requests.get(src)

    if not r.status_code == 200:
        return

    return storage.upload_file(
        r.content,
        dst_filename,
        r.headers.get('content-type', 'image/jpeg'))
