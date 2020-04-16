import json
import logging
import re

from src.aws import templates_dynamodb
from src.model.dot_map import DotMap

log = logging.getLogger()
templates_reduced = templates_dynamodb.get_all_templates_path_index()


def parse_template_parameters(json_file):
    return re.findall(r'{{(\w+-?[\w,\.,\[,\]]+)}}', json.dumps(json_file))


def match_template(template, mock_request):
    template_path_replaced = '^' + re.sub(r'{{\w+}}', '(\\\w+)', template['path']) + '$'
    return re.match(template_path_replaced, mock_request.path) and template['httpStatus'] == mock_request.httpStatus


def search_template(mock_request):
    global templates_reduced
    result = next((t for t in templates_reduced if match_template(t, mock_request)), None)
    if not result:
        templates_reduced = templates_dynamodb.get_all_templates_path_index()
    return next((t for t in templates_reduced if match_template(t, mock_request)), None)


def parse_file(mock_request, json_file, template, user_parameters):
    str_file = json.dumps(json_file)
    for parameter in template.parameters:
        if parameter.startswith('query'):
            str_file = parse_query_parameter(parameter, str_file, mock_request.queryParams, user_parameters,
                                             template.defaultParameters)
        elif parameter.startswith('path'):
            str_file = parse_path_parameter(parameter, str_file, mock_request.path, template, user_parameters)
        elif parameter.startswith('body'):
            str_file = parse_body_parameter(parameter, str_file, mock_request.body, user_parameters,
                                            template.defaultParameters)
        else:
            str_file = parse_parameter(parameter, str_file, user_parameters, template.defaultParameters)

    return json.loads(str_file)


def parse_parameter(parameter, str_file, user_parameters, template_default_parameters):
    replacement = None

    if parameter in user_parameters:
        replacement = user_parameters[parameter]
    elif parameter in template_default_parameters:
        replacement = template_default_parameters[parameter]

    if replacement:
        str_file = str_file.replace('{{' + parameter + '}}', replacement)
    return str_file


def parse_query_parameter(parameter, str_file, query_parameters, user_parameters, template_default_parameters):
    parameter_key = parameter[6:]
    replacement = None

    if parameter_key in query_parameters:
        replacement = query_parameters[parameter_key][0]
    elif parameter in user_parameters:
        replacement = user_parameters[parameter]
    elif parameter in template_default_parameters:
        replacement = template_default_parameters[parameter]

    if replacement:
        str_file = str_file.replace('{{' + parameter + '}}', replacement)
    return str_file


def parse_path_parameter(parameter, str_file, path, template, user_parameters):
    parameter_key = '{{' + parameter[5:] + '}}'
    replacement = None
    template_path_list = template.path.split('/')
    path_list = path.split('/')
    if parameter_key in template_path_list:
        replacement = path_list[template_path_list.index(parameter_key)]
    elif parameter in user_parameters:
        replacement = user_parameters[parameter]
    elif parameter in template.defaultParameters:
        replacement = template.defaultParameters[parameter]

    if replacement:
        str_file = str_file.replace('{{' + parameter + '}}', replacement)
    return str_file


def parse_body_parameter(parameter, str_file, body, user_parameters, template_default_parameters):
    replacement = None
    if body:
        replacement = get_parameter_from_body(parameter[5:], body)

    if not replacement and parameter in user_parameters:
        replacement = user_parameters[parameter]
    elif not replacement and parameter in template_default_parameters:
        replacement = template_default_parameters[parameter]

    if replacement:
        str_file = str_file.replace('{{' + parameter + '}}', replacement)
    return str_file


def get_parameter_from_body(parameter_key, body):
    value = DotMap(json.loads(body))
    for key in parameter_key.split('.'):
        try:
            if key.endswith(']'):
                matcher = re.match(f'({key[:key.index("[")]})\\[(\\d+)]', key)
                value = getattr(value, matcher.group(1)).__getitem__(int(matcher.group(2)))
            else:
                value = getattr(value, key)
        except Exception as e:
            log.error(f'Parsed parameter {parameter_key} not found in body', e)
            value = None
            break

    return value if value and isinstance(value, str) else None
