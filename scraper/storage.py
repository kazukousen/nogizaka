from __future__ import absolute_import

import os

# from flask import current_app
from google.cloud import storage
import six
from werkzeug.exceptions import BadRequest


def _get_storage_client():
    return storage.Client(
        # project=current_app.config['PROJECT_ID'])
        project=os.environ.get('PROJECT_ID')
    )


def _check_extension(filename, allowed_extensions):
    if ('.' not in filename or
            filename.split('.').pop().lower() not in allowed_extensions):
        raise BadRequest(
            "{0} has an invalid name or extension".format(filename))


def upload_file(file_stream, filename, content_type):
    # _check_extension(filename, current_app.config['ALLOWED_EXTENSIONS'])

    blob = _get_blob(filename)

    blob.upload_from_string(
        file_stream,
        content_type=content_type)

    url = blob.public_url

    if isinstance(url, six.binary_type):
        url = url.decode('utf-8')

    return url


def download_string(filename):
    # _check_extension(filename, current_app.config['ALLOWED_EXTENSIONS'])

    blob = _get_blob(filename)
    source = blob.download_as_string().decode()
    return source


def is_exists_file(filename):
    blob = _get_blob(filename)

    return blob.exists()


def _get_blob(filename):
    client = _get_storage_client()
    # bucket = client.bucket(current_app.config['CLOUD_STORAGE_BUCKET'])
    bucket = client.bucket(os.environ.get('CLOUD_STORAGE_BUCKET'))
    blob = bucket.blob(filename)

    if blob is None:
        from google.cloud.storage import Blob
        blob = Blob(filename, bucket)

    return blob


def read_lines(path):
    """
    ストレージからダウンロードしたファイルを行ごとにの要素で配列にする
    """
    source = download_string(path)
    rows = source.split('\n')
    return rows
