import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_VALID_PAYLOAD = {
    "input": "Génère un post Facebook",
    "property": {
        "id": 1,
        "property_type": "Appartement",
        "city": "Nice",
        "price": 350000,
    },
}

_SUCCESS_AGENT_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {
        "status": "draft",
        "platforms": {
            "facebook": {
                "generated": True,
                "post": "Belle villa à Nice...",
                "hashtags": [],
                "images": [],
            }
        },
    },
})

_FAILURE_AGENT_RESPONSE = json.dumps({
    "success": False,
    "error": "generation_failed",
    "data": {},
})


class TestExecuteSuccess:

    def test_returns_200(self):
        with patch("app.api.social_media.SocialMediaAgent") as MockAgent:
            MockAgent.return_value.run.return_value = _SUCCESS_AGENT_RESPONSE
            response = client.post("/social-media/execute", json=_VALID_PAYLOAD)
        assert response.status_code == 200

    def test_success_flag_is_true(self):
        with patch("app.api.social_media.SocialMediaAgent") as MockAgent:
            MockAgent.return_value.run.return_value = _SUCCESS_AGENT_RESPONSE
            response = client.post("/social-media/execute", json=_VALID_PAYLOAD)
        body = response.json()
        assert body["success"] is True
        assert body["error"] is None

    def test_data_is_forwarded(self):
        with patch("app.api.social_media.SocialMediaAgent") as MockAgent:
            MockAgent.return_value.run.return_value = _SUCCESS_AGENT_RESPONSE
            response = client.post("/social-media/execute", json=_VALID_PAYLOAD)
        data = response.json()["data"]
        assert data["status"] == "draft"
        assert "platforms" in data


class TestExecuteInvalidPayload:

    def test_missing_input_returns_422(self):
        response = client.post("/social-media/execute", json={"property": {}})
        assert response.status_code == 422

    def test_missing_property_returns_422(self):
        response = client.post("/social-media/execute", json={"input": "test"})
        assert response.status_code == 422

    def test_empty_body_returns_422(self):
        response = client.post("/social-media/execute", json={})
        assert response.status_code == 422


class TestExecuteAgentError:

    def test_agent_exception_returns_200_with_failure(self):
        with patch("app.api.social_media.SocialMediaAgent") as MockAgent:
            MockAgent.return_value.run.side_effect = RuntimeError("LLM unavailable")
            response = client.post("/social-media/execute", json=_VALID_PAYLOAD)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["error"] == "agent_error"
        assert body["data"] == {}

    def test_agent_failure_code_is_forwarded(self):
        with patch("app.api.social_media.SocialMediaAgent") as MockAgent:
            MockAgent.return_value.run.return_value = _FAILURE_AGENT_RESPONSE
            response = client.post("/social-media/execute", json=_VALID_PAYLOAD)
        body = response.json()
        assert body["success"] is False
        assert body["error"] == "generation_failed"

    def test_agent_non_json_response_returns_parse_error(self):
        with patch("app.api.social_media.SocialMediaAgent") as MockAgent:
            MockAgent.return_value.run.return_value = "not valid json"
            response = client.post("/social-media/execute", json=_VALID_PAYLOAD)
        body = response.json()
        assert body["success"] is False
        assert body["error"] == "agent_response_parse_error"


class TestUniformContract:

    def test_success_response_has_three_keys(self):
        with patch("app.api.social_media.SocialMediaAgent") as MockAgent:
            MockAgent.return_value.run.return_value = _SUCCESS_AGENT_RESPONSE
            response = client.post("/social-media/execute", json=_VALID_PAYLOAD)
        assert set(response.json().keys()) == {"success", "error", "data"}

    def test_error_response_has_three_keys(self):
        with patch("app.api.social_media.SocialMediaAgent") as MockAgent:
            MockAgent.return_value.run.side_effect = RuntimeError("boom")
            response = client.post("/social-media/execute", json=_VALID_PAYLOAD)
        assert set(response.json().keys()) == {"success", "error", "data"}

    def test_no_stacktrace_in_error_response(self):
        with patch("app.api.social_media.SocialMediaAgent") as MockAgent:
            MockAgent.return_value.run.side_effect = RuntimeError("boom")
            response = client.post("/social-media/execute", json=_VALID_PAYLOAD)
        assert "Traceback" not in response.text
        assert "RuntimeError" not in response.text
