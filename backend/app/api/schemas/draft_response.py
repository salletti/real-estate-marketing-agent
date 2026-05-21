from pydantic import BaseModel, ConfigDict, Field

from app.api.links.models.link_response import LinkResponse


class DraftResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    thread_id: str
    status: str
    approval_status: str | None
    content: dict
    links: dict[str, LinkResponse] = Field(default_factory=dict, alias="_links")
