from typing import Any, Dict, List

from observability.logger import log_tool_success


class PublishInstagramService:

    def publish(self, caption: str, images: List[str], thread_id: str = "") -> Dict[str, Any]:
        log_tool_success("instagram", thread_id)
        return {
            "platform": "instagram",
            "status": "published",
            "caption_preview": caption[:100],
        }
