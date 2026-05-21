"""Tests multi-plateformes — step 12 (LangGraph).

Vérifie la séparation entre l'agent (routing) et les nodes (génération).
Tous les tests sont rapides et déterministes : aucun appel LLM réel.
"""
import app.application.graphs.nodes.generate_facebook_node as fb_node_module
import app.application.graphs.nodes.generate_instagram_node as ig_node_module
from tests.utils.response_utils import (
    build_platform_result,
    is_valid_multi_platform_data,
    is_valid_platform_result,
)


# ---------------------------------------------------------------------------
# Nœuds — tools importés au bon endroit
# ---------------------------------------------------------------------------

class TestNodeToolImports:

    def test_facebook_node_uses_capability_registry(self):
        assert hasattr(fb_node_module, "get_registry")

    def test_instagram_node_uses_capability_registry(self):
        assert hasattr(ig_node_module, "get_registry")

    def test_facebook_node_uses_capability_executor(self):
        assert hasattr(fb_node_module, "get_executor")

    def test_instagram_node_uses_capability_executor(self):
        assert hasattr(ig_node_module, "get_executor")


# ---------------------------------------------------------------------------
# response_utils — construire_un_résultat_plateforme
# ---------------------------------------------------------------------------

class TestBuildPlatformResult:

    def test_facebook_result_contains_post(self):
        result = build_platform_result(generated=True, post="Belle villa")
        assert result["post"] == "Belle villa"

    def test_instagram_result_contains_caption(self):
        result = build_platform_result(generated=True, caption="☀️ Rêve")
        assert result["caption"] == "☀️ Rêve"

    def test_generated_flag_is_preserved(self):
        result = build_platform_result(generated=True)
        assert result["generated"] is True

    def test_images_defaults_to_empty_list(self):
        result = build_platform_result(generated=True)
        assert result["images"] == []

    def test_hashtags_defaults_to_empty_list(self):
        result = build_platform_result(generated=True)
        assert result["hashtags"] == []

    def test_custom_images_are_preserved(self):
        result = build_platform_result(generated=True, images=["url1"])
        assert result["images"] == ["url1"]

    def test_no_post_key_when_not_provided(self):
        result = build_platform_result(generated=True, caption="cap")
        assert "post" not in result

    def test_no_caption_key_when_not_provided(self):
        result = build_platform_result(generated=True, post="post")
        assert "caption" not in result


# ---------------------------------------------------------------------------
# response_utils — est_un_résultat_plateforme_valide
# ---------------------------------------------------------------------------

class TestIsValidPlatformResult:

    def test_valid_minimal_result(self):
        assert is_valid_platform_result({"generated": True, "images": []})

    def test_missing_generated_fails(self):
        assert not is_valid_platform_result({"images": []})

    def test_missing_images_fails(self):
        assert not is_valid_platform_result({"generated": True})

    def test_non_dict_fails(self):
        assert not is_valid_platform_result("not a dict")

    def test_empty_dict_fails(self):
        assert not is_valid_platform_result({})


# ---------------------------------------------------------------------------
# response_utils — est_une_donnée_multi_plateforme_valide
# ---------------------------------------------------------------------------

class TestIsValidMultiPlatformData:

    def test_facebook_only_data_is_valid(self):
        data = {
            "facebook": {"generated": True, "images": []}
        }
        assert is_valid_multi_platform_data(data, ["facebook"])

    def test_instagram_only_data_is_valid(self):
        data = {
            "instagram": {"generated": True, "images": []}
        }
        assert is_valid_multi_platform_data(data, ["instagram"])

    def test_both_platforms_data_is_valid(self):
        data = {
            "facebook": {"generated": True, "images": []},
            "instagram": {"generated": True, "images": []},
        }
        assert is_valid_multi_platform_data(data, ["facebook", "instagram"])

    def test_missing_instagram_fails_when_required(self):
        data = {"facebook": {"generated": True, "images": []}}
        assert not is_valid_multi_platform_data(data, ["facebook", "instagram"])

    def test_missing_facebook_fails_when_required(self):
        data = {"instagram": {"generated": True, "images": []}}
        assert not is_valid_multi_platform_data(data, ["facebook", "instagram"])

    def test_non_dict_data_fails(self):
        assert not is_valid_multi_platform_data("not a dict", ["facebook"])

    def test_invalid_platform_result_fails_validation(self):
        data = {"facebook": {"post": "text"}}
        assert not is_valid_multi_platform_data(data, ["facebook"])
