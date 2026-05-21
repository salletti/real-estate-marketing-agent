from typing import TypedDict


class SocialMediaState(TypedDict):
    thread_id: str  # correlation ID — propagé dans tous les nodes pour le structured logging
    input: str
    property_json: str

    generate_facebook: bool
    generate_instagram: bool

    facebook_result: dict | None
    instagram_result: dict | None

    final_result: dict | None
    approval_status: str | None
