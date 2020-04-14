from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Template:
    id: str
    path: str
    context: str
    name: str
    responseType: str
    httpStatus: int = 200
    defaultParameters: dict = field(default_factory=dict)
    parameters: List[str] = field(default_factory=list)

    def get_s3_location(self):
        return f'{self.context}/{self.name}/{str(self.httpStatus)}/{self.id}.{self.responseType}'
