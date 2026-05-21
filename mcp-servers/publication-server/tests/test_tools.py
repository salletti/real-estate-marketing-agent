import json
from unittest.mock import patch

from tools.publish_facebook_tool import handle_publish_facebook
from tools.publish_instagram_tool import handle_publish_instagram


class TestPublishFacebookTool:

    def test_valid_input_returns_success(self):
        result = json.loads(handle_publish_facebook("Superbe villa!", ["https://img.com/1.jpg"], "t-001"))
        assert result["success"] is True
        assert result["error"] is None
        assert result["data"]["platform"] == "facebook"
        assert result["data"]["status"] == "published"
        assert "post_preview" in result["data"]

    def test_post_preview_is_truncated_at_100_chars(self):
        long_post = "A" * 200
        result = json.loads(handle_publish_facebook(long_post, [], "t-001"))
        assert result["success"] is True
        assert len(result["data"]["post_preview"]) <= 100

    def test_empty_images_list_is_valid(self):
        result = json.loads(handle_publish_facebook("Short post", [], "t-001"))
        assert result["success"] is True

    def test_empty_post_returns_error(self):
        result = json.loads(handle_publish_facebook("", [], "t-001"))
        assert result["success"] is False
        assert result["error"] == "missing_or_invalid_post"

    def test_invalid_images_format_returns_error(self):
        result = json.loads(handle_publish_facebook("Valid post", [1, 2, 3], "t-001"))
        assert result["success"] is False
        assert result["error"] == "invalid_images_format"

    def test_service_exception_returns_publish_failed(self):
        with patch(
            "tools.publish_facebook_tool._service.publish",
            side_effect=Exception("network error"),
        ):
            result = json.loads(handle_publish_facebook("Valid post", [], "t-001"))
        assert result["success"] is False
        assert result["error"] == "publish_failed"

    def test_thread_id_does_not_affect_output(self):
        r1 = json.loads(handle_publish_facebook("Post", [], "thread-aaa"))
        r2 = json.loads(handle_publish_facebook("Post", [], "thread-bbb"))
        assert r1["data"]["post_preview"] == r2["data"]["post_preview"]


class TestPublishInstagramTool:

    def test_valid_input_returns_success(self):
        result = json.loads(handle_publish_instagram("Belle vue!", ["https://img.com/1.jpg"], "t-001"))
        assert result["success"] is True
        assert result["error"] is None
        assert result["data"]["platform"] == "instagram"
        assert result["data"]["status"] == "published"
        assert "caption_preview" in result["data"]

    def test_caption_preview_is_truncated_at_100_chars(self):
        long_caption = "C" * 200
        result = json.loads(handle_publish_instagram(long_caption, [], "t-001"))
        assert result["success"] is True
        assert len(result["data"]["caption_preview"]) <= 100

    def test_empty_images_list_is_valid(self):
        result = json.loads(handle_publish_instagram("Short caption", [], "t-001"))
        assert result["success"] is True

    def test_empty_caption_returns_error(self):
        result = json.loads(handle_publish_instagram("", [], "t-001"))
        assert result["success"] is False
        assert result["error"] == "missing_or_invalid_caption"

    def test_invalid_images_format_returns_error(self):
        result = json.loads(handle_publish_instagram("Valid caption", [1, 2, 3], "t-001"))
        assert result["success"] is False
        assert result["error"] == "invalid_images_format"

    def test_service_exception_returns_publish_failed(self):
        with patch(
            "tools.publish_instagram_tool._service.publish",
            side_effect=Exception("api down"),
        ):
            result = json.loads(handle_publish_instagram("Valid caption", [], "t-001"))
        assert result["success"] is False
        assert result["error"] == "publish_failed"

    def test_thread_id_does_not_affect_output(self):
        r1 = json.loads(handle_publish_instagram("Caption", [], "thread-aaa"))
        r2 = json.loads(handle_publish_instagram("Caption", [], "thread-bbb"))
        assert r1["data"]["caption_preview"] == r2["data"]["caption_preview"]
