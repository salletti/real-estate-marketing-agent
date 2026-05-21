from pydantic import BaseModel


class LinkResponse(BaseModel):
    method: str
    href: str
