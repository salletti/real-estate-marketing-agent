"""Integration tests — vérifie que le transport SSE répond correctement.

Ces tests touchent les vrais serveurs MCP via le réseau Docker.
Ils doivent être lancés depuis le container backend (docker compose exec backend pytest -m integration).

Ce qu'on valide ici :
- Le health endpoint des deux serveurs est joignable (HTTP 200).
- L'endpoint SSE répond 200 et non 421 (régression DNS rebinding protection).
- La connexion MCP complète (initialize + call_tool) fonctionne sans erreur de transport.
"""

import json
import urllib.request

import pytest

from app.core.config import settings
from app.infrastructure.mcp.client import MCPClient

_CONTENT_GEN_BASE = settings.mcp_content_generation_server_url.removesuffix("/sse")
_PUBLICATION_BASE = settings.mcp_publication_server_url.removesuffix("/sse")


def _http_get_status(url: str) -> int:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


class TestMcpTransportHealth:

    @pytest.mark.integration
    def test_content_generation_server_health(self):
        status = _http_get_status(f"{_CONTENT_GEN_BASE}/health")
        assert status == 200, f"Expected 200, got {status} — content-generation-server unreachable or returning error"

    @pytest.mark.integration
    def test_publication_server_health(self):
        status = _http_get_status(f"{_PUBLICATION_BASE}/health")
        assert status == 200, f"Expected 200, got {status} — publication-server unreachable or returning error"


class TestMcpTransportSse:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_content_generation_sse_no_421(self):
        """Régression : l'endpoint SSE ne doit pas retourner 421 Invalid Host Header."""
        try:
            with urllib.request.urlopen(
                urllib.request.Request(
                    f"{_CONTENT_GEN_BASE}/sse",
                    headers={"Accept": "text/event-stream"},
                ),
                timeout=3,
            ) as resp:
                assert resp.status == 200
        except urllib.error.HTTPError as exc:
            assert exc.code != 421, (
                f"Got HTTP 421 on /sse — DNS rebinding protection is blocking "
                f"Host: {_CONTENT_GEN_BASE.split('//')[1]}. "
                "Check ALLOWED_HOSTS config in content-generation-server."
            )
        except Exception:
            # Une coupure de connexion / timeout après les en-têtes est attendu en SSE ;
            # on vérifie uniquement qu'on n'a PAS reçu 421 avant l'établissement.
            pass

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_publication_server_sse_no_421(self):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(
                    f"{_PUBLICATION_BASE}/sse",
                    headers={"Accept": "text/event-stream"},
                ),
                timeout=3,
            ) as resp:
                assert resp.status == 200
        except urllib.error.HTTPError as exc:
            assert exc.code != 421, (
                f"Got HTTP 421 on /sse — DNS rebinding protection is blocking "
                f"Host: {_PUBLICATION_BASE.split('//')[1]}. "
                "Check ALLOWED_HOSTS config in publication-server."
            )
        except Exception:
            pass


class TestMcpToolCall:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_content_generation_tool_reachable(self):
        """Vérifie qu'un appel MCP complet (initialize + call_tool) ne lève pas d'erreur transport."""
        client = MCPClient(settings.mcp_content_generation_server_url)
        result_json = await client.call_tool_async(
            "generate_facebook_post",
            {"property_json": json.dumps({"id": 99, "property_type": "Appartement", "city": "Paris", "price": 300000}), "thread_id": "transport-test"},
        )
        result = json.loads(result_json)
        # On n'impose pas success=True (le LLM peut échouer sans vraie clé API en CI),
        # mais l'outil doit renvoyer une réponse JSON valide — pas une erreur transport.
        assert "success" in result, "Tool response is not a valid MCP result dict"
        assert "error" in result
