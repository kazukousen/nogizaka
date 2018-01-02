import logging
import json

from scraper import get_model, storage
from scraper.nogizaka import Blog
from flask import current_app
from google.cloud import pubsub
import psq
import requests
from bs4 import BeautifulSoup


publisher_client = pubsub.PublisherClient()
subscriber_client = pubsub.SubscriberClient()


def get_scraper_queue():
    project = current_app.config['PROJECT_ID']

    return psq.Queue(
        publisher_client, subscriber_client, project,
        'nogizaka_scraper', extra_context=current_app.app_context)


def process_scraping_by_member(member):
    scraper = Blog(member=member)
    scraper.run_all_by_member()
