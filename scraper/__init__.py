import json
import logging
import os

from flask import current_app, Flask, redirect, request, session, url_for, jsonify, Response

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

    @app.route("/")
    def index():
        return redirect(url_for('crud.list'))

    @app.errorhandler(404)
    def server_error(error=None):
        message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
        }
        json = jsonify(message)
        return Response(json, status=404, mimetype='application/json')

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
