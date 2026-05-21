# Runbook — HTTP 421 sur /sse (MCP DNS Rebinding Protection)

## Symptôme

- `POST /drafts/generate` retourne `{"success": false, "error": "no_platform_generated", "data": {"platform_errors": {"facebook": "node_execution_failed", "instagram": "node_execution_failed"}}}`
- Les logs backend montrent que `generate_facebook` et/ou `generate_instagram` échouent après 3 retries
- Les logs du MCP server montrent : `"Invalid Host header: <service-name>:<port>"`
- HTTP 421 sur `/sse`

## Diagnostic rapide (< 2 min)

```bash
# 1. Vérifier la présence du 421 dans les logs
docker compose logs content-generation-server | grep "Invalid Host"
docker compose logs publication-server | grep "Invalid Host"

# 2. Vérifier la config ALLOWED_HOSTS active dans le container
docker compose exec content-generation-server env | grep ALLOWED_HOSTS
docker compose exec publication-server env | grep ALLOWED_HOSTS

# 3. Vérifier que le log de démarrage montre les bons hosts
docker compose logs content-generation-server | grep "server_startup"
docker compose logs publication-server | grep "server_startup"

# 4. Test direct SSE sans passer par le backend
curl -v http://localhost:8001/sse 2>&1 | grep -E "HTTP/|421|200"
curl -v http://localhost:8002/sse 2>&1 | grep -E "HTTP/|421|200"
```

## Cause racine

FastMCP v1.x active automatiquement la protection DNS rebinding quand `host="127.0.0.1"` (valeur par défaut). La protection rejette tout Host header qui n'est pas `localhost:*` ou `127.0.0.1:*`.

Dans Docker Compose, le backend appelle `http://content-generation-server:8001/sse`, ce qui envoie `Host: content-generation-server:8001` — rejeté par défaut.

## Fix

### Rollback immédiat (service down)

Ajouter `ALLOWED_HOSTS=*` temporairement dans `docker-compose.yml` pour débloquer le service, puis corriger la config proprement :

```yaml
# docker-compose.yml — TEMPORAIRE, dev only
content-generation-server:
  environment:
    ALLOWED_HOSTS: "*"
```

```bash
docker compose up -d --build content-generation-server publication-server
```

### Fix durable

Vérifier que `mcp-servers/content-generation-server/config.py` contient les bons hosts dans `allowed_hosts` :

```python
allowed_hosts: list[str] = Field(
    default=["content-generation-server", "content-generation-server:8001",
             "localhost", "localhost:8001", "127.0.0.1", "127.0.0.1:8001"],
)
```

Si le DNS du service a changé (ex: renommage dans `docker-compose.yml` ou migration k8s), ajouter le nouveau hostname à la liste via la variable d'env `ALLOWED_HOSTS` dans le secrets manager ou `.env`.

```bash
# Rebuild après correction
docker compose up -d --build content-generation-server publication-server

# Vérifier
curl -f http://localhost:8001/health && echo "OK"
curl -v http://localhost:8001/sse 2>&1 | grep "HTTP/"
```

## Ce qu'il ne faut pas faire

- **Ne jamais mettre `ALLOWED_HOSTS=*` en staging ou prod** — cela désactive toute protection DNS rebinding.
- **Ne pas supprimer `TransportSecuritySettings`** — la protection est utile et doit rester active avec les bons hosts.
- **Ne pas renommer les services Docker sans mettre à jour `ALLOWED_HOSTS`** — le nom de service devient le Host header dans les appels inter-containers.

## Prévention

Le test d'intégration `backend/tests/infrastructure/mcp/test_mcp_transport.py::TestMcpTransportSse` détecte ce problème automatiquement en CI. Si la CI passe mais que le problème réapparaît en prod, vérifier que les `ALLOWED_HOSTS` de prod incluent le DNS interne du load balancer ou service mesh.
