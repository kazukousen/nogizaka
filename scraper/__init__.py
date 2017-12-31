import json
import logging
import os

from flask import current_app, Flask, redirect, request, session, url_for

from dotenv import load_dotenv


load_dotenv(os.path.join(os.curdir, '.env'))


def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Setup the data model.
    with app.app_context():
        model = get_model()
        model.init_app(app)

    # Register the Bookshelf CRUD blueprint.
    from .crud import crud
    app.register_blueprint(crud, url_prefix='/books')

    # Add a default root route.
    @app.route("/")
    def index():
        return redirect(url_for('crud.list'))

    # Add an error handler that reports exceptions to Stackdriver Error
    # Reporting. Note that this error handler is only used when debug
    # is False
    @app.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred.
        """, 500

    return app


def get_model():
    model_backend = current_app.config['DATA_BACKEND']
    if model_backend == 'datastore':
        from . import model_datastore
        model = model_datastore
    else:
        raise ValueError(
            "No appropriate databackend configured. "
            "Please specify datastore, cloudsql, or mongodb")

    return model