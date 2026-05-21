import asyncio
import concurrent.futures
import json
import logging
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)


class MCPClient:
    """Client MCP générique — se connecte à un serveur de capacités distant via SSE.

    Pourquoi SSE ?
    SSE (Server-Sent Events) repose sur HTTP standard. Le serveur pousse les
    messages sur une connexion persistante GET /sse ; le client envoie les
    requêtes JSON-RPC via POST. Pas d'upgrade WebSocket, pas de protocole
    spécifique — compatible avec tous les proxys et load balancers. FastMCP
    utilise SSE comme transport HTTP par défaut.

    Pourquoi un ThreadPoolExecutor dans call_tool() ?
    Le SDK Python MCP est nativement asynchrone (anyio). Appeler asyncio.run()
    directement depuis une route FastAPI asynchrone déclenche l'erreur
    "cannot run new event loop while another is running". Un thread dédié
    possède sa propre boucle d'événements — sûr depuis tous les contextes
    d'appel (nœud LangGraph synchrone, route FastAPI asynchrone, tests).
    C'est volontairement transitoire : quand le graphe migrera vers ainvoke()
    et des nœuds asynchrones, on pourra supprimer ce wrapper et await
    call_tool_async() directement.
    """

    def __init__(self, server_url: str) -> None:
        self._server_url = server_url

    async def call_tool_async(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Appelle un outil MCP distant et retourne son contenu texte en JSON."""
        async with sse_client(self._server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                if result.content and result.content[0].type == "text":
                    return result.content[0].text
                return json.dumps({
                    "success": False,
                    "error": "empty_mcp_response",
                    "data": {},
                })

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Wrapper synchrone thread-safe autour de call_tool_async."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, self.call_tool_async(tool_name, arguments))
            return future.result()

    async def list_tools_async(self) -> list:
        """Interroge le serveur MCP et retourne la liste des tools disponibles."""
        async with sse_client(self._server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return result.tools

    def list_tools(self) -> list:
        """Wrapper synchrone thread-safe autour de list_tools_async."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, self.list_tools_async())
            return future.result()
