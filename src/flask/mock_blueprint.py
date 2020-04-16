import http
import logging

from flask import Blueprint, request, jsonify

from src import mock_service
from src.aws import users_dynamodb, templates_dynamodb, templates_s3
from src.model.mock_request import MockRequest
from src.model.template import Template
from src.model.user import User

mock_blueprint = Blueprint('mock', __name__)
log = logging.getLogger()


@mock_blueprint.route("/mock", methods=["POST"])
def mock():
    try:
        mock_request = MockRequest.from_dict(request.json)
    except (KeyError, TypeError) as e:
        log.error('Error creating mock request', e)
        return jsonify({'error': 'Invalid request'}), http.HTTPStatus.BAD_REQUEST

    user_json = users_dynamodb.get_user(mock_request.userId)
    if not user_json:
        log.error(f'User id not found for request {mock_request.userId}')
        return jsonify({'error': f'User {mock_request.userId} not found'}), http.HTTPStatus.NOT_FOUND

    user = User.from_json(user_json)
    if not user.isMock:
        log.warning(f'User {mock_request.userId} is not mock available')
        return '', http.HTTPStatus.NO_CONTENT

    if not mock_request.httpStatus:
        mock_request.httpStatus = user.defaultResponse

    template_reduced = mock_service.search_template(mock_request)
    if not template_reduced:
        log.error(f'Template id not found for path {mock_request.path} and http status response '
                  f'{mock_request.httpStatus}')
        return jsonify({'error': 'Template id not found'}), http.HTTPStatus.NOT_FOUND

    template = Template.from_json(templates_dynamodb.get_template(template_reduced['id']))
    file = templates_s3.get_file(template)
    if not file:
        log.error(f"File not found for path {mock_request.path} and template id {template_reduced['id']}")
        return jsonify({'error': 'File not found'}), http.HTTPStatus.NOT_FOUND

    if template.responseType == 'json':
        return jsonify(mock_service.parse_file(mock_request, file, template, user.parameters))

    return '', http.HTTPStatus.NO_CONTENT
