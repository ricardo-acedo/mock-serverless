from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class User:
    id: str
    alias: str = 'Mock User'
    parameters: dict = field(default_factory=dict)
    isMock: bool = True
    defaultResponse: int = 200

    def reset(self):
        self.isMock = False
        self.defaultResponse = 200
        self.parameters = {}
