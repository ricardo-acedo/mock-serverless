from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class MockRequest:
    userId: str
    path: str
    httpStatus: int = None
    queryParams: dict = field(default_factory=dict)
    body: str = None
