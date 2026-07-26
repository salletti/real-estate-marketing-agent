# Development Guide

## Start The Stack

```bash
cp .env.example .env
docker compose up --build
```

The backend runs with hot reload through the bind mounts configured in `docker-compose.yml`.

## Services

- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Content generation MCP server: http://localhost:8001
- Publication MCP server: http://localhost:8002

## Environment Files

The root `.env` file is used by Docker Compose.

There are also service-specific examples:

- `backend/.env.example`
- `frontend/.env.example`

Keep secrets in local `.env` files only.

## Backend Tests

```bash
docker compose exec backend pytest tests/ -v
```

## MCP Tests

```bash
docker compose exec content-generation-server pytest tests/ -v
docker compose exec publication-server pytest tests/ -v
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Checks:

```bash
npm run lint
npm run build
```

## API Checks

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```
