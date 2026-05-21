from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from domain.property_photo import PropertyPhoto


@dataclass
class Property:
    id: int
    uid: str

    property_type: str
    sub_type: Optional[str]
    transaction_type: str

    city: str
    postal_code: Optional[str]
    country: str

    surface: Optional[float]
    rooms: Optional[int]
    bedrooms: Optional[int]

    price: Optional[float]
    charges: Optional[float]
    taxes: Optional[float]

    description: Optional[str]

    balcony_count: Optional[int]
    terrace_count: Optional[int]

    overall_condition: Optional[str]
    work_required: Optional[bool]

    has_pool: Optional[bool]
    parking_count: Optional[int]

    co_ownership_fee: Optional[float]

    created_at: Optional[datetime]

    is_prestige: Optional[bool] = False

    amenities: List[str] = field(default_factory=list)
    exposures: List[str] = field(default_factory=list)
    photos: List[PropertyPhoto] = field(default_factory=list)
