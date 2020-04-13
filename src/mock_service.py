import json
import re

#re.search(r'{{(\w+)-?(\w+)?}}', json.dumps('json_file'));


def parse_template_parameters(json_file):
    return re.findall(r'{{(\w+-?\w+?)}}', json.dumps(json_file))

