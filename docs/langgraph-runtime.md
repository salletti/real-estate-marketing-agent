# LangGraph Runtime

The social media workflow is orchestrated with LangGraph. The graph generates draft content, aggregates results, interrupts for human approval, and resumes publication after approval.

## Shared State

`SocialMediaState` is a `TypedDict` passed from node to node. Each node reads the fields it needs and returns a partial state update.

```python
class SocialMediaState(TypedDict):
    input: str
    property_json: str

    generate_facebook: bool
    generate_instagram: bool

    facebook_result: dict | None
    instagram_result: dict | None

    final_result: dict | None
    approval_status: str | None
```

The `generate_facebook` and `generate_instagram` flags are resolved once and then used as the source of truth for conditional routing.

## Workflow

```text
START
  |
  +-- generate_facebook=True ----> facebook_node
  |                                  |
  |                                  v
  |                           instagram_node, when needed
  |
  +-- generate_instagram=True ---> instagram_node
  |
  v
aggregate_drafts
  |
  v
wait_for_approval
  |
  +-- approved --> publish_facebook --> publish_instagram, when needed --> END
  |
  +-- rejected ---------------------------------------------------------> END
```

## Interrupt And Resume

`wait_for_approval_node` calls LangGraph `interrupt()`. The workflow is suspended, its checkpoint is saved, and the API returns a draft response.

```python
graph.invoke(state, config)
```

Resume uses the same `thread_id` through the same LangGraph config:

```python
graph.invoke(Command(resume="approved"), config)
```

The `thread_id` is the correlation key. A different `thread_id` creates a separate workflow.

## Durable Checkpoints With Redis

`MemorySaver` is useful for local experiments, but checkpoints disappear after a backend restart. Redis is used for durable workflow state.

```text
LangGraph runtime             Business projection
-----------------             -------------------
Redis                         PostgreSQL
checkpoints                   publications
suspended state               statuses and payloads
runtime recovery              API and frontend data
```

Configuration:

```bash
CHECKPOINTER_PROVIDER=memory
CHECKPOINTER_PROVIDER=redis
REDIS_URL=redis://redis:6379
```

Redis uses `redis/redis-stack-server` because RedisJSON and RediSearch are required by the checkpoint implementation.

## Recovery Scenario

```python
graph1.invoke(state, config)
graph2.get_state(config)
graph2.invoke(Command(resume="approved"), config)
```

`graph1` and `graph2` must use the exact same `thread_id`.

## Integration Test

```bash
docker compose exec -e REDIS_URL=redis://redis:6379 backend \
  pytest tests/application/graphs/checkpointers/test_runtime_recovery.py -v -m integration
```
