import http
import logging

from flask import Blueprint, jsonify, request

from src.aws import users_dynamodb
from src.model.user import User


log = logging.getLogger()
user_blueprint = Blueprint('users', __name__)


@user_blueprint.route("/users/<string:user_id>")
def get_user(user_id):
    resp = users_dynamodb.get_user(user_id)
    if not resp:
        log.error('User with id ' + user_id + ' does not exist')
        return jsonify({'error': 'User does not exist'}), http.HTTPStatus.NOT_FOUND

    return jsonify(User.from_json(resp))


@user_blueprint.route("/users")
def get_all_users():
    return jsonify(list(map(User.from_json, users_dynamodb.get_all_users())))


@user_blueprint.route("/users", methods=["POST"])
def create_user():
    try:
        user = User.from_dict(request.json)
        print(user)
    except (KeyError, TypeError) as e:
        log.error('Error creating user', e)
        return jsonify({'error': 'Please provide at least a valid id'}), http.HTTPStatus.BAD_REQUEST
    users_dynamodb.add_user(user)
    return jsonify(user)


@user_blueprint.route("/users/<string:user_id>", methods=["PUT"])
def update_user(user_id):
    request.json['id'] = user_id
    try:
        user = User.from_dict(request.json)
    except (KeyError, TypeError) as e:
        log.error('Error creating user', e)
        return jsonify({'error': 'Please provide at least a valid id'}), http.HTTPStatus.BAD_REQUEST
    users_dynamodb.add_user(user)
    return jsonify(user)


@user_blueprint.route("/users/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    resp = users_dynamodb.delete_user(user_id)
    if resp:
        return '', http.HTTPStatus.NO_CONTENT
    else:
        return jsonify({'error': 'The user does not exists'}), http.HTTPStatus.NOT_FOUND


@user_blueprint.route("/users/<string:user_id>/reset",  methods=["POST"])
def reset_user(user_id):
    resp = users_dynamodb.get_user(user_id)
    if not resp:
        log.error('User with id ' + user_id + ' does not exist')
        return jsonify({'error': 'User does not exist'}), http.HTTPStatus.NOT_FOUND

    user = User.from_json(resp)
    user.reset()
    users_dynamodb.add_user(user)
    return jsonify(user)
