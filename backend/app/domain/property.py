from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from app.domain.property_photo import PropertyPhoto


"""Projection simplifiée d'un bien immobilier, orientée marketing."""


@dataclass
class Property:
    # Identité
    id: int
    uid: str

    # Type
    property_type: str
    sub_type: Optional[str]
    transaction_type: str

    # Localisation
    city: str
    postal_code: Optional[str]
    country: str

    # Caractéristiques principales
    surface: Optional[float]
    rooms: Optional[int]
    bedrooms: Optional[int]

    # Prix
    price: Optional[float]
    charges: Optional[float]
    taxes: Optional[float]

    # Description brute
    description: Optional[str]

    # Extérieurs
    balcony_count: Optional[int]
    terrace_count: Optional[int]

    # État
    overall_condition: Optional[str]
    work_required: Optional[bool]

    # Environnement
    has_pool: Optional[bool]
    parking_count: Optional[int]


    # Copropriété
    co_ownership_fee: Optional[float]

    # Dates
    created_at: Optional[datetime]

    # Prestige
    is_prestige: Optional[bool] = False

    # Amenities
    amenities: List[str] = field(default_factory=list)

    # Exposition
    exposures: List[str] = field(default_factory=list)

    # Photos
    photos: List[PropertyPhoto] = field(default_factory=list)
