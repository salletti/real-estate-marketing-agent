from typing import Any, Dict, List, Optional


def build_platform_result(
    *,
    generated: bool,
    post: Optional[str] = None,
    caption: Optional[str] = None,
    hashtags: Optional[List[str]] = None,
    images: Optional[List[str]] = None,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "generated": generated,
        "hashtags": hashtags or [],
        "images": images or [],
    }
    if post is not None:
        result["post"] = post
    if caption is not None:
        result["caption"] = caption
    return result


def is_valid_platform_result(result: Any) -> bool:
    if not isinstance(result, dict):
        return False
    return {"generated", "images"}.issubset(result.keys())


def is_valid_multi_platform_data(data: Any, platforms: List[str]) -> bool:
    if not isinstance(data, dict):
        return False
    return all(
        platform in data and is_valid_platform_result(data[platform])
        for platform in platforms
    )
