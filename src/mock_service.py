import json
import re


def parse_template_parameters(json_file):
    return re.findall(r'{{(\w+-?\w+?)}}', json.dumps(json_file))

