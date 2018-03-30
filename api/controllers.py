import logging
from functools import wraps

from flask import Blueprint, request, jsonify, Response

from api.api_except import MyException
from helpers import *

api = Blueprint('api', __name__, url_prefix="")

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def validate_input(view_function):
    @wraps(view_function)
    def func(*args, **kwargs):
        try:
            input_data = request.get_json(silent=True, force=True)
            if not input_data:
                raise MyException('No input data')
            query = input_data.get("query")
            if query is None:
                raise MyException("'query' is a required property")
            # one of: exp, elk, bio
            scenario = str(input_data.get("scenario"))
            if scenario is None:
                raise MyException("'scenario' is a required property")
            if scenario not in [con.ELK, con.EXPANDED, con.BIOASQ]:
                raise MyException("choose from '{}', '{}', '{}' for 'scenario'".format(con.ELK, con.EXPANDED, con.BIOASQ))
            response = view_function(query, scenario)
            return response
        except MyException as e:
            return Response(json.dumps({'error': e.error_msg}), status=400, mimetype='application/json')
    return func


@api.route('/search', methods=['POST'])
@validate_input
def read_query(*args):
    query = args[0]
    scenario = args[1]
    res = query_search(query, scenario)
    return jsonify(res)

'''
@api.route('/search-elk', methods=['POST'])
def search_elk():
    input_data = request.get_json(silent=True, force=True)
    # queries = input_data.get("query")
    if not input_data:
        res = {'error': 'No input data'}
        return jsonify(res)
    query = input_data.get("query")

    docs, meta = query_search(query)
    res = dict()
    res['docs'] = docs
    res['meta'] = meta
    return jsonify(res)


@api.route('/search-bio', methods=['POST'])
def search_elk():
    input_data = request.get_json(silent=True, force=True)
    # queries = input_data.get("query")
    if not input_data:
        res = {'error': 'No input data'}
        return jsonify(res)
    query = input_data.get("query")

    docs, meta = query_search(query)
    res = dict()
    res['docs'] = docs
    res['meta'] = meta
    return jsonify(res)
'''