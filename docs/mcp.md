# MCP Integration

MCP servers expose external capabilities used by the backend workflow. The backend remains the orchestrator; MCP servers are stateless capability providers.

## Servers

```text
mcp-servers/
├── content-generation-server/
└── publication-server/
```

The content generation server exposes tools for generating social media content. The publication server exposes tools for publishing or mocking social publication.

## Capability Discovery

Capabilities are not hard-coded in the backend. During FastAPI startup, the backend discovers the tools exposed by configured MCP servers and registers them in memory.

```text
FastAPI lifespan
  |
  v
RegistryLoader.load()
  |
  +-- discover content-generation-server
  |
  +-- discover publication-server
  |
  v
CapabilityRegistry
```

Configuration:

```bash
MCP_CONTENT_GENERATION_SERVER_URL=http://content-generation-server:8001/sse
MCP_PUBLICATION_SERVER_URL=http://publication-server:8002/sse
```

## SSE Transport

The MCP servers use FastMCP over SSE.

```text
Backend
  -> GET /sse
  <- endpoint URL
  -> POST /messages/
  <- JSON-RPC response
```

SSE keeps the transport HTTP-based and compatible with common proxies and load balancers.

## Thread Correlation

The LangGraph `thread_id` is sent as an argument to MCP tools. This makes it possible to correlate logs across the backend and MCP servers.

```text
[backend] thread_id=abc-123 tool=generate_facebook_post
[mcp]     thread_id=abc-123 tool=generate_facebook_post
[mcp]     thread_id=abc-123 event=llm_call_success
```

## Health Checks

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## Tests

```bash
docker compose exec content-generation-server pytest tests/ -v
docker compose exec publication-server pytest tests/ -v
```
