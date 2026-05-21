from app.application.common.photo_utils import extract_photo_urls
from app.domain.property_photo import PropertyPhoto


def _photos(*urls: str) -> list:
    return [PropertyPhoto(url=u) for u in urls]


class TestExtractPhotoUrls:

    def test_empty_list_returns_empty(self):
        assert extract_photo_urls([]) == []

    def test_returns_urls_in_order(self):
        result = extract_photo_urls(_photos("https://a.com/1.jpg", "https://a.com/2.jpg"))
        assert result == ["https://a.com/1.jpg", "https://a.com/2.jpg"]

    def test_limits_to_3_urls(self):
        photos = _photos(
            "https://a.com/1.jpg",
            "https://a.com/2.jpg",
            "https://a.com/3.jpg",
            "https://a.com/4.jpg",
        )
        assert len(extract_photo_urls(photos)) == 3

    def test_deduplicates_urls(self):
        photos = _photos("https://a.com/1.jpg", "https://a.com/1.jpg", "https://a.com/2.jpg")
        result = extract_photo_urls(photos)
        assert result == ["https://a.com/1.jpg", "https://a.com/2.jpg"]

    def test_ignores_empty_urls(self):
        photos = _photos("", "https://a.com/1.jpg", "")
        assert extract_photo_urls(photos) == ["https://a.com/1.jpg"]

    def test_all_empty_returns_empty(self):
        assert extract_photo_urls(_photos("", "")) == []
