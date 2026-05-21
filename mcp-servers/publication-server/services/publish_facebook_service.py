from typing import Any, Dict, List

from observability.logger import log_tool_success


class PublishFacebookService:

    def publish(self, post: str, images: List[str], thread_id: str = "") -> Dict[str, Any]:
        log_tool_success("facebook", thread_id)
        return {
            "platform": "facebook",
            "status": "published",
            "post_preview": post[:100],
        }
