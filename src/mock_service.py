import json
import re

from src.aws import templates_dynamodb

templates_reduced = templates_dynamodb.get_all_templates_path_index()


def parse_template_parameters(json_file):
    return re.findall(r'{{(\w+-?\w+?)}}', json.dumps(json_file))


def match_template(template, mock_request):
    template_path_replaced = '^' + re.sub(r'{{\w+}}', '(\\\w+)', template['path']) + '$'
    return re.match(template_path_replaced, mock_request.path) and template['httpStatus'] == mock_request.httpStatus


def search_template(mock_request):
    global templates_reduced
    result = next((t for t in templates_reduced if match_template(t, mock_request)), None)
    if not result:
        templates_reduced = templates_dynamodb.get_all_templates_path_index()
    return next((t for t in templates_reduced if match_template(t, mock_request)), None)





