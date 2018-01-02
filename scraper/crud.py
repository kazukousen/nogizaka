from scraper import get_model, tasks, storage
from flask import Blueprint, current_app, request, Response, jsonify


crud = Blueprint('crud', __name__)


@crud.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    members, next_page_token = get_model().list(cursor=token)

    json = jsonify(members)
    return Response(json, status=200, mimetype='application/json')



@crud.route('/<id>')
def view(id):
    member = get_model().read(id)
    json = jsonify(member)
    return Response(json, status=200, mimetype='application/json')


@crud.route('/all', method=['GET'])
def all():
    members = storage.read_lines('members.txt')
    q = tasks.get_scraper_queue()
    [q.enqueue(tasks.process_scraping_by_member, member) for member in members]

    return Response(status=200, mimetype='application/json')


@crud.route('/<id>/update', method=['GET'])
def update(id):
    member = get_model().read(id)

    q = tasks.get_scraper_queue()
    q.enqueue(tasks.process_scraping_by_member, member['value'])
    json = jsonify(member)
    return Response(json, status=200, mimetype='application/json')
