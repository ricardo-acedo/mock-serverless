import http
import logging
from uuid import uuid4

from flask import Blueprint, jsonify, request

from src import mock_service
from src.aws import templates_dynamodb, templates_s3
from src.model.template import Template

logger = logging.getLogger()
logger.setLevel(logging.INFO)

template_blueprint = Blueprint('templates', __name__)


@template_blueprint.route("/templates/<string:template_id>")
def get_template(template_id):
    logger.info(f'Getting template for template id {template_id}')
    resp = templates_dynamodb.get_template(template_id)
    if not resp:
        logger.error(f'Template with id {template_id} does not exist')
        return jsonify({'error': 'Template does not exist'}), http.HTTPStatus.NOT_FOUND

    return jsonify(Template.from_json(resp))


@template_blueprint.route("/templates")
def get_all_templates():
    logger.info('Getting all templates')
    return jsonify(list(map(Template.from_json, templates_dynamodb.get_all_templates())))


@template_blueprint.route("/templates", methods=["POST"])
def create_template():
    try:
        logger.info(f'Creating a new template for request {request.json}')
        request.json['id'] = str(uuid4())[:8]
        template = Template.from_dict(request.json)
    except (KeyError, TypeError):
        logger.exception('Error creating template')
        return jsonify({'error': 'Please provide at least a valid id'}), http.HTTPStatus.BAD_REQUEST
    if templates_dynamodb.add_template(template) is None:
        return jsonify({'error': 'The template path already exists'}), http.HTTPStatus.BAD_REQUEST
    return jsonify(template)


@template_blueprint.route("/templates/<string:template_id>", methods=["PUT"])
def update_template(template_id):
    logger.info(f'Updating template id {template_id} with {request.json}')
    resp = templates_dynamodb.get_template(template_id)
    if not resp:
        logger.error(f'Template with id {template_id} does not exist')
        return jsonify({'error': 'Template does not exist'}), http.HTTPStatus.NOT_FOUND

    template = Template.from_json(resp)
    default_parameters = request.json['defaultParameters']
    if not default_parameters or not isinstance(default_parameters, dict):
        logger.error(f'Bad request to update template with id {template_id}')
        return jsonify({'error': 'To update template defaultParameters are required'}), http.HTTPStatus.BAD_REQUEST

    template.defaultParameters = default_parameters
    templates_dynamodb.update_template(template)
    return jsonify(template)


@template_blueprint.route("/templates/<string:template_id>", methods=["DELETE"])
def delete_template(template_id):
    logger.info(f'Deleting template id {template_id}')
    resp = templates_dynamodb.delete_template(template_id)
    if resp:
        templates_s3.delete_file(Template.from_dict(resp))
        return '', http.HTTPStatus.NO_CONTENT
    else:
        return jsonify({'error': 'The template does not exists'}), http.HTTPStatus.NOT_FOUND


@template_blueprint.route("/templates/<string:template_id>/file",  methods=["POST"])
def save_template_file(template_id):
    logger.info(f'Adding template file to s3 for template id {template_id}')
    resp = templates_dynamodb.get_template(template_id)
    if not resp:
        logger.error(f'Template with id {template_id} does not exist')
        return jsonify({'error': 'Template does not exist'}), http.HTTPStatus.NOT_FOUND

    template = Template.from_json(resp)
    templates_s3.save_file(template, request.json)
    template.parameters = mock_service.parse_template_parameters(request.json)
    templates_dynamodb.update_template(template)
    return jsonify(template)


@template_blueprint.route("/templates/<string:template_id>/file")
def get_template_file(template_id):
    logger.info(f'Getting template file from s3 for template id {template_id}')
    resp = templates_dynamodb.get_template(template_id)
    if not resp:
        logger.error(f'Template with id {template_id} does not exist')
        return jsonify({'error': 'Template does not exist'}), http.HTTPStatus.NOT_FOUND

    file = templates_s3.get_file(Template.from_json(resp))
    if not file:
        logger.error(f'There is no file loaded for template_id {template_id}')
        return jsonify({'error': 'File does not exist'}), http.HTTPStatus.NOT_FOUND
    return jsonify(file)


@template_blueprint.route("/templates/<string:template_id>/file", methods=["DELETE"])
def delete_template_file(template_id):
    logger.info(f'Deleting template file from s3 for template id {template_id}')
    resp = templates_dynamodb.get_template(template_id)
    if not resp:
        logger.error(f'Template with id {template_id} does not exist')
        return jsonify({'error': 'Template does not exist'}), http.HTTPStatus.NOT_FOUND

    templates_s3.delete_file(Template.from_json(resp))
    return '', http.HTTPStatus.NO_CONTENT
