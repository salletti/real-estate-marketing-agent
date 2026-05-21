from typing import List

from app.domain.property_photo import PropertyPhoto


def extract_photo_urls(photos: List[PropertyPhoto]) -> List[str]:
    seen = set()
    result = []
    for p in photos:
        if p.url and p.url not in seen:
            seen.add(p.url)
            result.append(p.url)
        if len(result) == 3:
            break
    return result
