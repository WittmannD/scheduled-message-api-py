import json
from http import HTTPStatus
from base64 import b64decode
from functools import wraps
from flask import make_response, jsonify, request
from flask_restful import abort


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        try:
            if 'X-API-Key' in request.headers:
                token = request.headers['X-API-Key']

            current_user = b64decode(token)
            current_user = json.loads(current_user)

            if not current_user:
                raise AssertionError()

        except (ValueError, AssertionError, json.JSONDecodeError) as err:
            return abort(HTTPStatus.UNAUTHORIZED)

        return f(*args, current_user, **kwargs)

    return decorator
