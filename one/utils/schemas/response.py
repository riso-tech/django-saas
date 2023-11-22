import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Pagination:
    """
    paging = Pagination(page=1, limit=10, total_pages=5, total_items=50)
    print(paging.to_dict())
    """

    page: int
    limit: int
    total_pages: int
    total_items: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DefaultResponse:
    """
    response = DefaultResponse(
        data={"key": "value"},
        pagination=Pagination(page=1, limit=10, total_pages=5, total_items=50)
    )

    print(response.to_json())
    """

    data: Any = None
    success: bool = True
    status_code: int = 200
    message: str = ""
    message_code: str = ""
    validation_errors: dict[str, str] = field(default_factory=dict)
    pagination: Pagination | None = None

    def data_validator(self):
        if self.data and "serializer" in self.data.__dict__:
            self.data = json.loads(json.dumps(self.data))

    def to_dict(self) -> dict[str, Any]:
        self.data_validator()
        response_dict = asdict(self)
        if self.pagination:
            response_dict["pagination"] = self.pagination.to_dict()
        return response_dict

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
