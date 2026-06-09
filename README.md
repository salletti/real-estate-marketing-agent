![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-agent-1C3C3C?logo=langchain&logoColor=white)
![LangSmith](https://img.shields.io/badge/LangSmith-observability-1C3C3C?logo=langchain&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-checkpoints-DC382D?logo=redis&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-server%20%2B%20client-6B46C1)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

# real-estate-marketing-agent

Agent IA qui génère et publie automatiquement des posts marketing immobiliers sur Facebook et Instagram — avec workflow human-in-the-loop : l'agent rédige les drafts, attend une approbation humaine, puis publie. Construit avec LangGraph + MCP + Redis pour une exécution durable et observable.

---

## Lancer le projet

```bash
# 1. Copier les variables d'environnement
cp .env.example .env

# 2. Lancer le projet
docker compose up --build
```

L'API est accessible sur **http://localhost:8000**

---

## Lancer les tests

```bash
docker compose exec backend pytest tests/ -v
```

---

## Tester /health

```bash
curl http://localhost:8000/health
```

Réponse attendue :

```json
{"status": "ok", "service": "real-estate-marketing-agent"}
```

---

## Documentation Swagger

**http://localhost:8000/docs**

---

## Structure des dossiers

```
real-estate-marketing-agent/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # Point d'entrée FastAPI
│   │   ├── api/                 # Routers FastAPI (couche transport)
│   │   ├── core/                # Configuration, settings
│   │   ├── domain/              # Entités métier et règles de gestion
│   │   ├── application/         # Cas d'usage (orchestration)
│   │   └── infrastructure/      # Adaptateurs techniques (LLM, DB, MCP client)
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── mcp-servers/
│   └── content-generation-server/   # Capability server MCP (port 8001)
│       ├── server.py                # FastMCP + SSE transport
│       ├── tools/                   # Handlers MCP
│       ├── services/                # Logique de génération
│       ├── infrastructure/          # LLM client (Groq)
│       └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Architecture V1

![Architecture simple](architecture.png)

## Architecture V2 avec MCP

![Architecture avec MCP](architecture_mcp.png)

---

## LangChain Tools

Les tools sont des fonctions Python décorées `@tool` (LangChain) qui forment la couche d'exécution atomique du workflow. Chaque tool a une responsabilité unique, reçoit un `str` JSON en entrée et retourne un `str` JSON structuré `{success, error, data}`.

```
app/application/tools/
├── generate_facebook_post_tool.py   @tool — génère un post + hashtags Facebook via LLM
├── generate_instagram_post_tool.py  @tool — génère une caption + hashtags Instagram via LLM
├── publish_facebook_tool.py         @tool — publie post + images sur Facebook (mock)
└── publish_instagram_tool.py        @tool — publie caption + images sur Instagram (mock)
```

### Contrat d'interface

```python
# Entrée : JSON string (property ou payload publication)
# Sortie : JSON string uniforme
{"success": True,  "error": None,    "data": {...}}
{"success": False, "error": "raison", "data": {...}}
```

Ce contrat uniforme permet aux nodes LangGraph de traiter succès et erreurs sans `try/except` et d'agréger les résultats dans le state de manière prévisible.

### Séparation tool / service

Le tool gère le **contrat d'interface** (parse JSON, valide l'entrée, construit la réponse structurée).
Le service (`application/services/`) gère la **logique métier** (appel LLM, construction du prompt, mappage du résultat).

```
generate_facebook_post_tool
    └─ GenerateFacebookPostService.generate(property)
            └─ LLMClient.generate(prompt)
```

---

## LangGraph — Graph et état partagé

### État partagé (`SocialMediaState`)

Le state est un `TypedDict` transmis de node en node. Chaque node lit ce dont il a besoin et retourne un dict partiel — LangGraph merge automatiquement les champs retournés dans le state global.

```python
class SocialMediaState(TypedDict):
    input: str               # instruction utilisateur ("génère Facebook et Instagram")
    property_json: str       # données du bien immobilier (JSON string)

    generate_facebook: bool  # flag d'intention — résolu par SocialMediaIntentResolver
    generate_instagram: bool

    facebook_result: dict | None   # résultat brut du generate_facebook_post_tool
    instagram_result: dict | None

    final_result: dict | None      # résultat agrégé (platforms, status, approval_status)
    approval_status: str | None    # "pending" | "approved" | "rejected"
```

Les flags `generate_facebook` / `generate_instagram` sont la **source de vérité** des routeurs conditionnels — ils ne changent jamais en cours d'exécution.

### Topologie du graph

```
START
  │
  ├─(generate_facebook=True)──► facebook_node
  │                                   │
  │              ┌────────────────────┘
  │              │  (generate_instagram=True)──► instagram_node
  │              │                                     │
  ├─(generate_instagram seul)──────────────────────────┘
  │                                                     │
  └──────────────────────────────────────────► aggregate_drafts
                                                        │
                                               wait_for_approval  ◄── interrupt() ici
                                                        │
                                          ┌─────────────┴──────────────┐
                                   (approved)                     (rejected)
                                          │                            │
                                 publish_facebook                     END
                                          │
                              (generate_instagram=True)
                                          │
                                 publish_instagram
                                          │
                                         END
```

### Interrupt / Resume

`wait_for_approval_node` appelle `interrupt()` (LangGraph) : le workflow se suspend, le checkpoint est sauvé dans Redis, et l'API retourne immédiatement avec `status: "draft"`.

```python
# Suspension
graph.invoke(state, config)          # → retourne {"__interrupt__": [...]}

# Reprise (après décision humaine)
graph.invoke(Command(resume="approved"), config)   # → reprend depuis wait_for_approval
```

Le `thread_id` dans `config` est la clé qui relie les deux appels — c'est lui qui permet à LangGraph de retrouver le bon checkpoint dans Redis et de reprendre exactement là où le workflow s'était arrêté.

---

## Runtime LangGraph durable avec Redis

### Problème résolu

Avec `MemorySaver`, les checkpoints LangGraph disparaissaient au redémarrage du backend.
Un workflow en attente d'approbation était perdu → impossible de reprendre.

### Solution

Redis est utilisé comme **runtime store** pour les checkpoints LangGraph.
PostgreSQL reste la **projection métier** (publications, statuts, payloads).

```
LangGraph Runtime             Métier
─────────────────             ──────
Redis                         PostgreSQL
checkpoints                   publications
état suspendu                 statuts / payloads
runtime recovery              API / frontend
```

### Architecture ajoutée

```
get_checkpointer_provider()   ← factory avec lazy singleton
        ↓
RedisCheckpointerProvider     ← nouveau (ou MemoryCheckpointerProvider)
        ↓
RedisSaver (officiel)         ← langgraph-checkpoint-redis
        ↓
redis/redis-stack-server      ← RedisJSON + RediSearch requis
```

Le graph ne connaît pas Redis — il appelle toujours `get_checkpointer_provider()`
sans savoir ce qu'il y a derrière.

### Durable execution — le scénario concret

```python
# graph1 : exécution initiale jusqu'à l'interrupt
graph1.invoke(state, config)         # → checkpoint sauvé dans Redis

# graph2 : nouvelle instance (simule un redémarrage process)
graph2.get_state(config)             # → retrouve "wait_for_approval" depuis Redis ✓
graph2.invoke(Command(resume=...), config)   # → workflow termine correctement ✓
```

Le `thread_id` est la clé du recovery : `graph1` et `graph2` doivent utiliser
**exactement le même** `config`. Un `thread_id` différent = nouveau workflow indépendant.

### Configuration

```bash
CHECKPOINTER_PROVIDER=memory   # défaut — zéro dépendance externe
CHECKPOINTER_PROVIDER=redis    # active la persistence durable
REDIS_URL=redis://redis:6379
```

### Lancer les tests d'intégration (Redis requis)

```bash
docker compose exec -e REDIS_URL=redis://redis:6379 backend \
  pytest tests/application/graphs/checkpointers/test_runtime_recovery.py -v -m integration
```

---

## Monitoring — LangSmith

LangSmith est un APM workflow-oriented qui trace chaque exécution LangGraph :
nodes, transitions, interrupt/resume, timings, tools.

### Activation

Renseigner dans `.env` :

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...       # smith.langchain.com → Settings → API Keys
LANGCHAIN_PROJECT=real-estate-marketing-agent
```

Sans clé ou avec `LANGCHAIN_TRACING_V2=false` : comportement normal, aucune erreur.

### Ce qu'on voit dans LangSmith

Chaque `POST /drafts/generate` produit un run traçable :

```
thread_id: abc-123                   ← correlation ID
├─ generate_facebook_node   2.3s
├─ generate_instagram_node  1.8s
├─ aggregate_drafts_node    0.1s
├─ wait_for_approval_node   → INTERRUPTED
│
│  [approbation humaine via POST /drafts/{id}/publish]
│
└─ publish_facebook_node    1.2s    ← RESUMED (même thread_id)
```

Le `thread_id` joue le rôle de **correlation ID** : toutes les spans d'un même
workflow (y compris après restart et recovery Redis) sont regroupées sous le même identifiant.

### Interface

**https://smith.langchain.com** → projet `real-estate-marketing-agent`

---

## Pourquoi cette architecture prépare les agents

L'architecture suit les principes de la **Clean Architecture** :

- `domain/` ne dépend de rien → les entités métier sont stables
- `application/` orchestre sans connaître les détails techniques → les use cases sont testables isolément
- `infrastructure/` est interchangeable → changer de LLM ou de base de données n'impacte pas la logique métier
- `agents/` appelle les use cases → l'agent reste un orchestrateur, pas un blob de code

Quand on ajoutera LangGraph ou un autre framework agentique, il s'intègrera dans `agents/`
sans toucher au domaine ni aux use cases.

---

## MCP Capability Discovery (startup FastAPI)

Les capabilities MCP ne sont pas codées en dur côté backend.
Au démarrage de FastAPI (`lifespan`), le backend découvre automatiquement les tools exposés
par les serveurs MCP configurés, puis les enregistre dans un registre mémoire (`CapabilityRegistry`).

### Pourquoi MCP

MCP (Model Context Protocol) standardise l'interface entre un orchestrateur et ses capabilities externes. Le serveur n'est pas un orchestrateur — il ne connaît pas le workflow, Redis, ni PostgreSQL. Il expose deux capabilities stateless : générer un post Facebook, générer une caption Instagram.

### Workflow de discovery

1. `main.py` exécute `lifespan` au startup.
2. `RegistryLoader.load()` lit la liste des serveurs MCP configurés via `settings` :
   - `content-generation-server`
   - `publication-server`
3. Pour chaque serveur, `MCPDiscovery.discover_server(name, url)` appelle `MCPClient.list_tools_async()`.
4. Chaque tool est converti en `Capability` puis enregistré via `CapabilityRegistry.register(...)`.
5. Les routes/services peuvent ensuite résoudre dynamiquement une capability via `find()`, `all()`, `by_server()`.

```
FastAPI startup (lifespan)
        |
        v
 get_registry() -> CapabilityRegistry (singleton)
        |
        v
 RegistryLoader.load()
        |
        +--> discover_server("content-generation-server", URL)
        |         -> MCPClient.list_tools_async()
        |         -> register(Capability...)
        |
        +--> discover_server("publication-server", URL)
                  -> MCPClient.list_tools_async()
                  -> register(Capability...)
```

### Configuration

- `MCP_CONTENT_GENERATION_SERVER_URL`
- `MCP_PUBLICATION_SERVER_URL`

### Transport MCP (SSE)

Le serveur utilise le transport **SSE (Server-Sent Events)** de FastMCP, qui tourne sur le port `8001`.

SSE, c'est du HTTP pur : le client ouvre une connexion persistante `GET /sse` et envoie ses requêtes JSON-RPC via `POST /messages/`. Pas de WebSocket, pas de protocole custom — compatible avec tous les proxies et load balancers. C'est le transport recommandé pour une première intégration MCP distante.

```
Backend (port 8000)                    MCP Server (port 8001)
────────────────────                   ──────────────────────
ContentGenerationClient
  → MCPClient.call_tool()
    → GET /sse           ──────────►  SSE stream ouvert
    ← endpoint URL       ◄──────────  {"endpoint": "/messages/?session_id=..."}
    → POST /messages/    ──────────►  {"method": "tools/call", "params": {...}}
    ← JSON-RPC response  ◄──────────  {"result": {"content": [{"type": "text", ...}]}}
```

### Propagation du thread_id

Le `thread_id` LangGraph est transmis comme argument au tool MCP. Il traverse le réseau et apparaît dans les logs du MCP server, créant un **correlation ID distribué** :

```
[backend]  {"event": "mcp_tool_call",  "thread_id": "abc-123", "tool": "generate_facebook_post"}
[mcp]      {"event": "tool_executed",  "thread_id": "abc-123", "tool": "generate_facebook_post"}
[mcp]      {"event": "llm_call_success","thread_id": "abc-123", "duration_ms": 1240}
```

### Health check

```bash
curl http://localhost:8001/health
# {"status": "ok", "server": "content-generation-server"}
```

### Lancer les tests du MCP server

```bash
docker compose exec content-generation-server pytest tests/ -v
```

---

## Pourquoi cette architecture prépare MCP

**MCP (Model Context Protocol)** standardise la façon dont un LLM découvre et appelle des outils externes.

Dans cette architecture :

- Les **tools** définis dans `agents/tools/` sont des fonctions Python avec une signature claire
- Il suffit d'un adaptateur MCP dans `infrastructure/mcp/` pour les exposer comme ressources MCP
- N'importe quel client compatible MCP (Claude Desktop, Continue, Cursor...) pourra alors appeler ces tools directement

Le backend implémente déjà un discovery runtime des tools MCP via `infrastructure/mcp/`
(`RegistryLoader`, `MCPDiscovery`, `CapabilityRegistry`), ce qui permet d'ajouter un serveur MCP
sans modifier le code des use cases.

L'isolation `domain / application / infrastructure` garantit que l'exposition MCP n'introduit
aucune logique métier parasite dans la couche de transport.
