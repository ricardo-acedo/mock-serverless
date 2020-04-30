import http
import logging

from flask import Blueprint, jsonify, request

from src.aws import users_dynamodb
from src.model.user import User


logger = logging.getLogger()
logger.setLevel(logging.INFO)
user_blueprint = Blueprint('users', __name__)


@user_blueprint.route("/users/<string:user_id>")
def get_user(user_id):
    logger.info(f'Getting user id {user_id}')
    resp = users_dynamodb.get_user(user_id)
    if not resp:
        logger.error(f'User with id {user_id} does not exist')
        return jsonify({'error': 'User does not exist'}), http.HTTPStatus.NOT_FOUND

    return jsonify(User.from_json(resp))


@user_blueprint.route("/users")
def get_all_users():
    logger.info('Getting all users')
    return jsonify(list(map(User.from_json, users_dynamodb.get_all_users())))


@user_blueprint.route("/users", methods=["POST"])
def create_user():
    try:
        logger.info(f'Creating user for request {request.json}')
        user = User.from_dict(request.json)
    except (KeyError, TypeError):
        logger.exception('Error creating user')
        return jsonify({'error': 'Please provide at least a valid id'}), http.HTTPStatus.BAD_REQUEST
    users_dynamodb.add_user(user)
    return jsonify(user)


@user_blueprint.route("/users/<string:user_id>", methods=["PUT"])
def update_user(user_id):
    logger.info(f'Updating user id {user_id} for request {request.json}')
    request.json['id'] = user_id
    try:
        user = User.from_dict(request.json)
    except (KeyError, TypeError):
        logger.exception('Error updating user')
        return jsonify({'error': 'Please provide at least a valid id'}), http.HTTPStatus.BAD_REQUEST
    users_dynamodb.add_user(user)
    return jsonify(user)


@user_blueprint.route("/users/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    logger.info(f'Deleting user id {user_id}')
    resp = users_dynamodb.delete_user(user_id)
    if resp:
        return '', http.HTTPStatus.NO_CONTENT
    else:
        return jsonify({'error': f'The user {user_id} does not exists'}), http.HTTPStatus.NOT_FOUND


@user_blueprint.route("/users/<string:user_id>/reset",  methods=["POST"])
def reset_user(user_id):
    logger.info(f'Resetting user id {user_id}')
    resp = users_dynamodb.get_user(user_id)
    if not resp:
        logger.error(f'User with id {user_id} does not exist')
        return jsonify({'error': 'User does not exist'}), http.HTTPStatus.NOT_FOUND

    user = User.from_json(resp)
    user.reset()
    users_dynamodb.add_user(user)
    return jsonify(user)
