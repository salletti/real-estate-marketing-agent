import pytest
from datetime import datetime
from app.application.mappers.property_mapper import PropertyMapper
from app.domain.property_photo import PropertyPhoto


# ---------------------------------------------------------------------------
# Jeux de données de test
# ---------------------------------------------------------------------------

@pytest.fixture
def full_raw():
    return {
        "id": 42,
        "uid": "abc-123",
        "property_type": "appartement",
        "sub_type": "duplex",
        "transaction_type": "vente",
        "location": {
            "city": "Paris",
            "postalCode": "75008",
            "country": "France",
        },
        "living_area": {
            "surfaceArea": 85.0,
            "roomsCount": 4,
            "numberOfBedrooms": 2,
        },
        "mandate_price": 750000.0,
        "charges": 200.0,
        "taxes": 1500.0,
        "amenities": {
            "comfort": ["fiber", "digicode"],
            "security": ["gardien"],
        },
        "balcony_count": 1,
        "terrace_count": 0,
        "overall_condition": "bon",
        "work_required": False,
        "environment": {
            "hasPool": False,
            "numberOfParkings": 1,
        },
        "co_ownership": {"fee": 350.0},
        "exposures": ["sud", "est"],
        "description": "Bel appartement lumineux.",
        "created_at": "2024-01-15T10:00:00",
        "is_prestige": True,
    }


# ---------------------------------------------------------------------------
# Cas nominal
# ---------------------------------------------------------------------------

class TestPropertyMapperFullData:

    def test_identity(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.id == 42
        assert p.uid == "abc-123"

    def test_type(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.property_type == "appartement"
        assert p.sub_type == "duplex"
        assert p.transaction_type == "vente"

    def test_location(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.city == "Paris"
        assert p.postal_code == "75008"
        assert p.country == "France"

    def test_living_area(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.surface == 85.0
        assert p.rooms == 4
        assert p.bedrooms == 2

    def test_price(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.price == 750000.0
        assert p.charges == 200.0
        assert p.taxes == 1500.0

    def test_amenities_flattened(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.amenities == ["fiber", "digicode", "gardien"]

    def test_exterior(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.balcony_count == 1
        assert p.terrace_count == 0

    def test_condition(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.overall_condition == "bon"
        assert p.work_required is False

    def test_environment(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.has_pool is False
        assert p.parking_count == 1

    def test_co_ownership(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.co_ownership_fee == 350.0

    def test_exposures(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.exposures == ["sud", "est"]

    def test_description(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.description == "Bel appartement lumineux."

    def test_prestige(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.is_prestige is True

    def test_created_at_parsed_as_datetime(self, full_raw):
        p = PropertyMapper.from_raw(full_raw)
        assert p.created_at == datetime(2024, 1, 15, 10, 0, 0)
        assert isinstance(p.created_at, datetime)


# ---------------------------------------------------------------------------
# Données manquantes — ne doit jamais planter
# ---------------------------------------------------------------------------

class TestPropertyMapperMissingData:

    def test_empty_dict_does_not_raise(self):
        p = PropertyMapper.from_raw({})
        assert p is not None

    def test_empty_dict_defaults(self):
        p = PropertyMapper.from_raw({})
        assert p.id == 0
        assert p.uid == ""
        assert p.city == ""
        assert p.country == ""
        assert p.property_type == ""
        assert p.transaction_type == ""
        assert p.amenities == []
        assert p.exposures == []
        assert p.is_prestige is False

    def test_empty_dict_optionals_are_none(self):
        p = PropertyMapper.from_raw({})
        assert p.surface is None
        assert p.rooms is None
        assert p.bedrooms is None
        assert p.price is None
        assert p.charges is None
        assert p.taxes is None
        assert p.description is None
        assert p.has_pool is None
        assert p.parking_count is None
        assert p.co_ownership_fee is None
        assert p.created_at is None

    def test_missing_location_block(self):
        p = PropertyMapper.from_raw({"id": 1, "uid": "x"})
        assert p.city == ""
        assert p.postal_code is None
        assert p.country == ""

    def test_missing_living_area_block(self):
        p = PropertyMapper.from_raw({})
        assert p.surface is None
        assert p.rooms is None
        assert p.bedrooms is None

    def test_missing_environment_block(self):
        p = PropertyMapper.from_raw({})
        assert p.has_pool is None
        assert p.parking_count is None

    def test_missing_co_ownership_block(self):
        p = PropertyMapper.from_raw({})
        assert p.co_ownership_fee is None

    def test_null_amenities_block(self):
        p = PropertyMapper.from_raw({"amenities": None})
        assert p.amenities == []

    def test_empty_amenities_lists(self):
        p = PropertyMapper.from_raw({"amenities": {"comfort": [], "security": []}})
        assert p.amenities == []

    def test_amenities_only_comfort(self):
        p = PropertyMapper.from_raw({"amenities": {"comfort": ["fiber"]}})
        assert p.amenities == ["fiber"]

    def test_amenities_only_security(self):
        p = PropertyMapper.from_raw({"amenities": {"security": ["digicode"]}})
        assert p.amenities == ["digicode"]

    def test_null_exposures(self):
        p = PropertyMapper.from_raw({"exposures": None})
        assert p.exposures == []

    def test_is_prestige_absent_defaults_false(self):
        p = PropertyMapper.from_raw({})
        assert p.is_prestige is False

    def test_is_prestige_null_defaults_false(self):
        p = PropertyMapper.from_raw({"is_prestige": None})
        assert p.is_prestige is False


# ---------------------------------------------------------------------------
# Robustesse — améliorations ciblées
# ---------------------------------------------------------------------------

class TestPropertyMapperRobustness:

    def test_id_as_string_is_cast_to_int(self):
        p = PropertyMapper.from_raw({"id": "99"})
        assert p.id == 99
        assert isinstance(p.id, int)

    def test_id_none_defaults_to_zero(self):
        p = PropertyMapper.from_raw({"id": None})
        assert p.id == 0

    def test_uid_none_defaults_to_empty_string(self):
        p = PropertyMapper.from_raw({"uid": None})
        assert p.uid == ""

    def test_created_at_valid_iso(self):
        p = PropertyMapper.from_raw({"created_at": "2024-06-01T08:30:00"})
        assert p.created_at == datetime(2024, 6, 1, 8, 30, 0)

    def test_created_at_invalid_string_returns_none(self):
        p = PropertyMapper.from_raw({"created_at": "not-a-date"})
        assert p.created_at is None

    def test_created_at_none_returns_none(self):
        p = PropertyMapper.from_raw({"created_at": None})
        assert p.created_at is None

    def test_amenities_deduplication(self):
        p = PropertyMapper.from_raw({
            "amenities": {
                "comfort": ["fiber", "digicode"],
                "security": ["digicode", "gardien"],
            }
        })
        assert "digicode" in p.amenities
        assert p.amenities.count("digicode") == 1

    def test_amenities_deduplication_preserves_order(self):
        p = PropertyMapper.from_raw({
            "amenities": {
                "comfort": ["fiber", "digicode"],
                "security": ["digicode", "gardien"],
            }
        })
        assert p.amenities == ["fiber", "digicode", "gardien"]


# ---------------------------------------------------------------------------
# Photos
# ---------------------------------------------------------------------------

class TestPropertyMapperPhotos:

    def test_photos_mapped_correctly(self):
        p = PropertyMapper.from_raw({
            "photos": [
                {"url": "https://cdn.example.com/1.jpg"},
                {"url": "https://cdn.example.com/2.jpg"},
            ]
        })
        assert p.photos == [
            PropertyPhoto(url="https://cdn.example.com/1.jpg"),
            PropertyPhoto(url="https://cdn.example.com/2.jpg"),
        ]

    def test_photos_absent_defaults_empty(self):
        p = PropertyMapper.from_raw({})
        assert p.photos == []

    def test_photos_null_defaults_empty(self):
        p = PropertyMapper.from_raw({"photos": None})
        assert p.photos == []

    def test_photos_invalid_item_ignored(self):
        p = PropertyMapper.from_raw({"photos": ["not_a_dict", 42]})
        assert p.photos == []

    def test_photos_empty_url_ignored(self):
        p = PropertyMapper.from_raw({"photos": [{"url": ""}]})
        assert p.photos == []

    def test_photos_missing_url_key_ignored(self):
        p = PropertyMapper.from_raw({"photos": [{}]})
        assert p.photos == []
