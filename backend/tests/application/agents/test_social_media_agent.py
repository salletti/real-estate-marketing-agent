import json
from unittest.mock import MagicMock, patch


_SUCCESS_FINAL = {
    "success": True,
    "error": None,
    "data": {"status": "draft", "platforms": {"facebook": {"generated": True, "post": "x", "hashtags": [], "images": []}}},
}


class TestSocialMediaAgentRouting:

    def _make_agent(self, mock_graph):
        with patch("app.application.agents.social_media_agent.build_social_media_graph") as mock_build:
            mock_build.return_value = mock_graph
            from app.application.agents.social_media_agent import SocialMediaAgent
            return SocialMediaAgent()

    def test_facebook_in_input_sets_generate_facebook_true(self):
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"final_result": _SUCCESS_FINAL}
        agent = self._make_agent(mock_graph)
        agent.run("Génère un post Facebook", "{}")
        state = mock_graph.invoke.call_args[0][0]
        assert state["generate_facebook"] is True

    def test_facebook_in_input_sets_generate_instagram_false(self):
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"final_result": _SUCCESS_FINAL}
        agent = self._make_agent(mock_graph)
        agent.run("Génère un post Facebook", "{}")
        state = mock_graph.invoke.call_args[0][0]
        assert state["generate_instagram"] is False

    def test_instagram_in_input_sets_generate_instagram_true(self):
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"final_result": _SUCCESS_FINAL}
        agent = self._make_agent(mock_graph)
        agent.run("Génère un post Instagram", "{}")
        state = mock_graph.invoke.call_args[0][0]
        assert state["generate_instagram"] is True

    def test_both_platforms_in_input(self):
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"final_result": _SUCCESS_FINAL}
        agent = self._make_agent(mock_graph)
        agent.run("Génère Facebook et Instagram", "{}")
        state = mock_graph.invoke.call_args[0][0]
        assert state["generate_facebook"] is True
        assert state["generate_instagram"] is True

    def test_graph_exception_returns_graph_error(self):
        mock_graph = MagicMock()
        mock_graph.invoke.side_effect = RuntimeError("boom")
        agent = self._make_agent(mock_graph)
        result = json.loads(agent.run("Génère un post Facebook", "{}"))
        assert result["success"] is False
        assert result["error"] == "graph_error"

    def test_property_json_forwarded_to_state(self):
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"final_result": _SUCCESS_FINAL}
        agent = self._make_agent(mock_graph)
        agent.run("Génère Facebook", '{"id": 42}')
        state = mock_graph.invoke.call_args[0][0]
        assert state["property_json"] == '{"id": 42}'
