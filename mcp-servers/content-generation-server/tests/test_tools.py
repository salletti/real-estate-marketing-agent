import json
from unittest.mock import patch

import pytest

from tools.generate_facebook_post_tool import handle_generate_facebook_post
from tools.generate_instagram_post_tool import handle_generate_instagram_post

_PROPERTY = json.dumps({
    "id": 1,
    "uid": "test-uid",
    "property_type": "Appartement",
    "transaction_type": "Vente",
    "location": {"city": "Paris", "country": "France", "postalCode": "75001"},
    "living_area": {"surfaceArea": 75, "roomsCount": 3, "numberOfBedrooms": 2},
    "mandate_price": 450000,
})

_LLM_FB = '{"post": "Superbe 3 pièces à Paris!", "hashtags": ["#immobilier", "#paris"]}'
_LLM_IG = '{"caption": "✨ Paris life awaits...", "hashtags": ["#immobilier", "#paris", "#appartement"]}'


class TestGenerateFacebookPostTool:

    def test_valid_input_returns_success(self):
        with patch("infrastructure.llm_client.LLMClient.generate", return_value=_LLM_FB):
            result = json.loads(handle_generate_facebook_post(_PROPERTY, "t-001"))

        assert result["success"] is True
        assert result["error"] is None
        assert "post" in result["data"]
        assert isinstance(result["data"]["hashtags"], list)

    def test_thread_id_does_not_affect_output(self):
        with patch("infrastructure.llm_client.LLMClient.generate", return_value=_LLM_FB):
            r1 = json.loads(handle_generate_facebook_post(_PROPERTY, "thread-aaa"))
            r2 = json.loads(handle_generate_facebook_post(_PROPERTY, "thread-bbb"))

        assert r1["data"]["post"] == r2["data"]["post"]

    def test_invalid_json_input_returns_error(self):
        result = json.loads(handle_generate_facebook_post("not valid json", "t-001"))
        assert result["success"] is False
        assert result["error"] == "invalid_input_json"
        assert result["data"]["post"] == ""

    def test_empty_input_returns_error(self):
        result = json.loads(handle_generate_facebook_post("", "t-001"))
        assert result["success"] is False

    def test_llm_failure_returns_error(self):
        with patch("infrastructure.llm_client.LLMClient.generate", side_effect=Exception("timeout")):
            result = json.loads(handle_generate_facebook_post(_PROPERTY, "t-001"))
        assert result["success"] is False
        assert result["error"] == "llm_generation_failed"

    def test_llm_invalid_json_response_returns_error(self):
        with patch("infrastructure.llm_client.LLMClient.generate", return_value="not json at all"):
            result = json.loads(handle_generate_facebook_post(_PROPERTY, "t-001"))
        assert result["success"] is False
        assert result["error"] == "incomplete_llm_response"


class TestGenerateInstagramPostTool:

    def test_valid_input_returns_success(self):
        with patch("infrastructure.llm_client.LLMClient.generate", return_value=_LLM_IG):
            result = json.loads(handle_generate_instagram_post(_PROPERTY, "t-001"))

        assert result["success"] is True
        assert "caption" in result["data"]
        assert isinstance(result["data"]["hashtags"], list)

    def test_hashtags_normalized_with_hash_prefix(self):
        raw = '{"caption": "Belle vue!", "hashtags": ["immobilier", "#paris", "luxe"]}'
        with patch("infrastructure.llm_client.LLMClient.generate", return_value=raw):
            result = json.loads(handle_generate_instagram_post(_PROPERTY, "t-001"))

        for tag in result["data"]["hashtags"]:
            assert tag.startswith("#"), f"Tag sans # : {tag}"

    def test_hashtags_capped_at_12(self):
        tags = [f"tag{i}" for i in range(20)]
        raw = json.dumps({"caption": "ok", "hashtags": tags})
        with patch("infrastructure.llm_client.LLMClient.generate", return_value=raw):
            result = json.loads(handle_generate_instagram_post(_PROPERTY, "t-001"))

        assert len(result["data"]["hashtags"]) <= 12

    def test_caption_truncated_at_500_chars(self):
        long_caption = "A" * 600
        raw = json.dumps({"caption": long_caption, "hashtags": ["#test"]})
        with patch("infrastructure.llm_client.LLMClient.generate", return_value=raw):
            result = json.loads(handle_generate_instagram_post(_PROPERTY, "t-001"))

        assert len(result["data"]["caption"]) <= 500

    def test_invalid_json_input_returns_error(self):
        result = json.loads(handle_generate_instagram_post("{bad json", "t-001"))
        assert result["success"] is False
        assert result["error"] == "invalid_input_json"
