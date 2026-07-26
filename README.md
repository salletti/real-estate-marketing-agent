![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-agent-1C3C3C?logo=langchain&logoColor=white)
![LangSmith](https://img.shields.io/badge/LangSmith-observability-1C3C3C?logo=langchain&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-checkpoints-DC382D?logo=redis&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-server%20%2B%20client-6B46C1)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

# Real Estate Marketing Agent

AI-powered marketing assistant for real estate listings. The project generates social media drafts from property data, keeps a human approval step before publication, and exposes the workflow through a FastAPI backend and a React frontend.

## Features

- Generate Facebook posts from real estate listing data.
- Generate Instagram captions and hashtags.
- Keep generated drafts pending until human approval.
- Resume interrupted workflows with LangGraph checkpoints.
- Expose content and publication capabilities through MCP servers.
- Store business state in PostgreSQL and workflow state in Redis.
- Optionally trace workflow execution with LangSmith.

## Tech Stack

- **Frontend:** React, TypeScript, Vite
- **Backend:** FastAPI, LangGraph, LangChain
- **Data:** PostgreSQL, Redis
- **Capabilities:** FastMCP servers
- **LLM provider:** Groq-compatible LLM client
- **Observability:** LangSmith, optional

## Architecture

The application is split into a frontend, a backend orchestrator, and dedicated MCP capability servers.

```text
Frontend
   |
   v
FastAPI backend
   |
   +-- PostgreSQL: publications, statuses, payloads
   +-- Redis: durable LangGraph checkpoints
   |
   +-- MCP content-generation server
   +-- MCP publication server
```

Architecture diagrams are available in:

- `architecture.png`
- `architecture_mcp.png`

Detailed documentation:

- [Architecture](docs/architecture.md)
- [LangGraph runtime](docs/langgraph-runtime.md)
- [MCP integration](docs/mcp.md)
- [LangSmith monitoring](docs/langsmith.md)
- [Development guide](docs/development.md)

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- A Groq API key if you want real LLM generation

### Setup

```bash
cp .env.example .env
```

Then edit `.env` and set at least:

```bash
GROQ_API_KEY=your_api_key
```

Start the full stack:

```bash
docker compose up --build
```

## Services

Once Docker Compose is running:

- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Backend health check: http://localhost:8000/health
- Content generation MCP health check: http://localhost:8001/health
- Publication MCP health check: http://localhost:8002/health

Expected backend health response:

```json
{"status": "ok", "service": "real-estate-marketing-agent"}
```

## Frontend

The frontend lives in `frontend/`.

```bash
cd frontend
npm install
npm run dev
```

By default, Vite serves the frontend on http://localhost:5173.

## Tests

Run backend tests:

```bash
docker compose exec backend pytest tests/ -v
```

Run MCP server tests:

```bash
docker compose exec content-generation-server pytest tests/ -v
docker compose exec publication-server pytest tests/ -v
```

Run frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

## Environment

The root `.env.example` contains the variables used by Docker Compose:

- `GROQ_API_KEY`
- `LLM_MODEL`
- `DATABASE_URL`
- `CHECKPOINTER_PROVIDER`
- `REDIS_URL`
- `MCP_CONTENT_GENERATION_SERVER_URL`
- `MCP_PUBLICATION_SERVER_URL`
- `CORS_ORIGINS`
- `LANGCHAIN_TRACING_V2`
- `LANGCHAIN_API_KEY`
- `LANGCHAIN_PROJECT`
- `BUFFER_API_KEY`

See [Development guide](docs/development.md) for local development notes.

## Project Status

This project is under active development. Publication adapters may be mocked depending on the configured server and environment variables.

## License

No license has been added yet. Add one before publishing the repository publicly.
