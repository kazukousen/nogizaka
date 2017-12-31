import scraper
import config

app = scraper.create_app(config)


# [START books_queue]
with app.app_context():
    books_queue = scraper.tasks.get_books_queue()
# [END books_queue]


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
