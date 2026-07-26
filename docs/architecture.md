# Architecture

This project follows a Clean Architecture-inspired split:

- `domain/` contains business entities and rules.
- `application/` contains use cases, workflow orchestration, services, and tools.
- `infrastructure/` contains adapters for databases, LLM providers, MCP clients, and other technical concerns.
- `api/` contains FastAPI transport routes.

The goal is to keep business rules independent from frameworks and providers. LLM clients, databases, and MCP servers can change without rewriting the core workflow.

## Repository Structure

```text
real-estate-marketing-agent/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── mcp-servers/
│   ├── content-generation-server/
│   └── publication-server/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## LangChain Tools

LangChain tools are small Python functions decorated with `@tool`. They form the atomic execution layer of the workflow.

Each tool has one responsibility, receives a JSON string, and returns a structured JSON string:

```json
{"success": true, "error": null, "data": {}}
```

```json
{"success": false, "error": "reason", "data": {}}
```

This uniform contract lets LangGraph nodes handle success and error cases predictably.

## Tool And Service Separation

Tools own the interface contract:

- parse JSON input
- validate required fields
- call the relevant service
- return a normalized response

Services own the application logic:

- build prompts
- call the LLM adapter
- map provider responses into application data

```text
generate_facebook_post_tool
    -> GenerateFacebookPostService.generate(property)
        -> LLMClient.generate(prompt)
```

## Why This Supports Agents

Agents should orchestrate capabilities, not contain business logic. Keeping use cases and domain rules outside of transport and provider code makes it easier to add new agentic workflows without turning the agent layer into a large procedural script.
