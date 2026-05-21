from typing import Any, Dict, Optional

from domain.property import Property
from infrastructure.llm_client import LLMClient
from prompts.facebook_post_prompt import FACEBOOK_POST_TEMPLATE
from utils.llm_utils import bool_to_str, list_to_str, parse_json

_FALLBACK: Dict[str, Any] = {
    "post": "",
    "hashtags": [],
}


class GenerateFacebookPostService:

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self._llm = llm_client or LLMClient()

    def generate(self, property: Property) -> Dict[str, Any]:
        prompt = FACEBOOK_POST_TEMPLATE.format(**_to_prompt_vars(property))
        raw = self._llm.generate(prompt)
        return parse_json(raw, _FALLBACK)


def _to_prompt_vars(p: Property) -> Dict[str, str]:
    return {
        "property_type": p.property_type or "",
        "sub_type": p.sub_type or "",
        "city": p.city or "",
        "postal_code": p.postal_code or "",
        "country": p.country or "",
        "surface": str(p.surface) if p.surface is not None else "",
        "rooms": str(p.rooms) if p.rooms is not None else "",
        "bedrooms": str(p.bedrooms) if p.bedrooms is not None else "",
        "price": str(p.price) if p.price is not None else "",
        "charges": str(p.charges) if p.charges is not None else "",
        "taxes": str(p.taxes) if p.taxes is not None else "",
        "description": p.description or "",
        "amenities": list_to_str(p.amenities),
        "balcony_count": str(p.balcony_count) if p.balcony_count is not None else "",
        "terrace_count": str(p.terrace_count) if p.terrace_count is not None else "",
        "overall_condition": p.overall_condition or "",
        "work_required": bool_to_str(p.work_required),
        "has_pool": bool_to_str(p.has_pool),
        "parking_count": str(p.parking_count) if p.parking_count is not None else "",
        "exposures": list_to_str(p.exposures),
        "co_ownership_fee": str(p.co_ownership_fee) if p.co_ownership_fee is not None else "",
        "is_prestige": bool_to_str(p.is_prestige),
    }
