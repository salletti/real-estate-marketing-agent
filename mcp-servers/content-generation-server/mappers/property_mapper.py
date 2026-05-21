from datetime import datetime
from typing import Any, Dict, List, Optional

from domain.property import Property
from domain.property_photo import PropertyPhoto


class PropertyMapper:

    @staticmethod
    def from_raw(data: Dict[str, Any]) -> Property:
        return Property(
            id=int(data.get("id", 0) or 0),
            uid=data.get("uid", "") or "",
            **_extract_type(data),
            **_extract_location(data),
            **_extract_living_area(data),
            **_extract_price(data),
            **_extract_exterior(data),
            **_extract_condition(data),
            **_extract_environment(data),
            **_extract_co_ownership(data),
            description=data.get("description"),
            amenities=_extract_amenities(data),
            exposures=data.get("exposures") or [],
            photos=_extract_photos(data),
            created_at=_parse_datetime(data.get("created_at")),
            is_prestige=data.get("is_prestige") or False,
        )


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _extract_type(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "property_type": data.get("property_type", ""),
        "sub_type": data.get("sub_type"),
        "transaction_type": data.get("transaction_type", ""),
    }


def _extract_location(data: Dict[str, Any]) -> Dict[str, Any]:
    loc = data.get("location") or {}
    return {
        "city": loc.get("city", ""),
        "postal_code": loc.get("postalCode"),
        "country": loc.get("country", ""),
    }


def _extract_living_area(data: Dict[str, Any]) -> Dict[str, Any]:
    area = data.get("living_area") or {}
    return {
        "surface": area.get("surfaceArea"),
        "rooms": area.get("roomsCount"),
        "bedrooms": area.get("numberOfBedrooms"),
    }


def _extract_price(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "price": data.get("mandate_price"),
        "charges": data.get("charges"),
        "taxes": data.get("taxes"),
    }


def _extract_exterior(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "balcony_count": data.get("balcony_count"),
        "terrace_count": data.get("terrace_count"),
    }


def _extract_condition(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "overall_condition": data.get("overall_condition"),
        "work_required": data.get("work_required"),
    }


def _extract_environment(data: Dict[str, Any]) -> Dict[str, Any]:
    env = data.get("environment") or {}
    return {
        "has_pool": env.get("hasPool"),
        "parking_count": env.get("numberOfParkings"),
    }


def _extract_co_ownership(data: Dict[str, Any]) -> Dict[str, Any]:
    co = data.get("co_ownership") or {}
    return {
        "co_ownership_fee": co.get("fee"),
    }


def _extract_photos(data: Dict[str, Any]) -> List[PropertyPhoto]:
    raw = data.get("photos") or []
    result = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        url = item.get("url") or ""
        if url:
            result.append(PropertyPhoto(url=url))
    return result


def _extract_amenities(data: Dict[str, Any]) -> List[str]:
    amenities = data.get("amenities") or {}
    comfort = amenities.get("comfort") or []
    security = amenities.get("security") or []
    seen = set()
    result = []
    for item in comfort + security:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
