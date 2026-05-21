"""Test d'intégration — Durable Execution avec Redis Checkpointer.

Démontre la durable execution : un workflow interrompu peut être repris
par une nouvelle instance de graph qui lit les checkpoints depuis Redis.

Concept pédagogique :
- graph1 exécute le workflow jusqu'à l'interrupt
- graph2 est une NOUVELLE instance (simule un redémarrage process)
- Grâce à Redis, graph2 retrouve exactement l'état où graph1 s'est arrêté
- Le MÊME thread_id est la clé du recovery — c'est lui qui lie les deux instances

Ce test utilise un vrai Redis (service Docker).
Il se skip automatiquement si Redis n'est pas disponible.

Marquer comme test d'intégration : pytest -m integration
"""
import os
from typing import TypedDict

import pytest
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# thread_id fixe et partagé entre graph1 et graph2 —
# c'est la clé primaire de tous les checkpoints Redis pour ce workflow.
THREAD_ID = "test-durable-execution-recovery"
CONFIG = {"configurable": {"thread_id": THREAD_ID}}


# ---------------------------------------------------------------------------
# Graphe minimal autonome — pas de LLM, pas de tools externes
# ---------------------------------------------------------------------------

class MinimalState(TypedDict):
    step: str
    result: str | None


def _step_one(state: MinimalState) -> dict:
    return {"step": "step_one_done"}


def _wait_node(state: MinimalState) -> dict:
    decision = interrupt("En attente de décision humaine")
    return {"step": "resumed", "result": decision}


def _final_node(state: MinimalState) -> dict:
    return {"step": "completed"}


def _build_minimal_graph(checkpointer) -> object:
    """Construit le graphe minimal avec le checkpointer fourni.

    Ce helper est appelé DEUX FOIS dans le test de recovery :
    une fois pour graph1 (exécution initiale),
    une fois pour graph2 (simulation de redémarrage).
    """
    workflow = StateGraph(MinimalState)
    workflow.add_node("step_one", _step_one)
    workflow.add_node("wait_node", _wait_node)
    workflow.add_node("final_node", _final_node)
    workflow.add_edge(START, "step_one")
    workflow.add_edge("step_one", "wait_node")
    workflow.add_edge("wait_node", "final_node")
    workflow.add_edge("final_node", END)
    return workflow.compile(checkpointer=checkpointer)


# ---------------------------------------------------------------------------
# Jeux de données de test
# ---------------------------------------------------------------------------

@pytest.fixture
def redis_saver():
    """Crée un RedisSaver connecté au Redis réel et nettoie après le test.

    Skip automatique si Redis n'est pas disponible — le test d'intégration
    ne doit pas faire échouer la suite unitaire en CI sans Redis.
    """
    try:
        client = Redis.from_url(REDIS_URL, socket_connect_timeout=2)
        client.ping()
    except (RedisConnectionError, Exception):
        pytest.skip(f"Redis non disponible sur {REDIS_URL} — test d'intégration ignoré")

    saver = RedisSaver(redis_client=client)
    saver.setup()

    yield saver

    # Nettoyage : supprime les données du thread de test pour éviter les effets de bord
    client.flushdb()
    client.close()


# ---------------------------------------------------------------------------
# Test de durable execution
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestDurableExecutionRecovery:
    """Démontre qu'un workflow interrompu survit à un redémarrage de process.

    L'architecture ici est exactement celle des vrais workflow engines :
    - Temporal, Conductor, Prefect stockent aussi les checkpoints d'exécution
    - Le process peut redémarrer, crasher, être redéployé
    - Le workflow reprend depuis le dernier checkpoint
    """

    def test_checkpoint_persiste_dans_redis_apres_interrupt(self, redis_saver):
        """Après interrupt, le checkpoint existe réellement dans Redis.

        C'est la preuve que Redis joue le rôle de runtime store :
        l'état du workflow est sérialisé et persisté, pas seulement en mémoire.
        """
        graph1 = _build_minimal_graph(redis_saver)
        result = graph1.invoke(
            {"step": "start", "result": None},
            config=CONFIG,
        )

        assert result.get("__interrupt__"), "Le workflow doit être suspendu à wait_node"

        # Lecture directe dans Redis : le checkpoint existe
        checkpoint = redis_saver.get(CONFIG)
        assert checkpoint is not None, "Redis doit contenir le snapshot du workflow"

    def test_nouveau_graph_recupere_etat_depuis_redis(self, redis_saver):
        """Après redémarrage simulé, le nouveau graph retrouve l'état suspendu.

        graph2 est une NOUVELLE instance — elle n'a aucun état en mémoire.
        Grâce au même thread_id et au même RedisSaver, get_state() retrouve
        exactement le node courant et le state sauvegardé par graph1.

        Sans Redis durable, get_state() retournerait un état vide.
        """
        # graph1 : exécution initiale jusqu'à l'interrupt
        graph1 = _build_minimal_graph(redis_saver)
        graph1.invoke({"step": "start", "result": None}, config=CONFIG)

        # graph2 : nouvelle instance — simule un redémarrage process
        graph2 = _build_minimal_graph(redis_saver)

        # MÊME CONFIG (même thread_id) — c'est la clé du recovery
        snap = graph2.get_state(CONFIG)

        assert snap is not None, "graph2 doit trouver le state dans Redis"
        assert "wait_node" in snap.next, (
            f"graph2 doit savoir que le workflow attend à wait_node, got: {snap.next}"
        )

    def test_resume_depuis_nouveau_graph_termine_workflow(self, redis_saver):
        """Le workflow reprend et se termine correctement depuis une nouvelle instance.

        C'est la démonstration complète de la durable execution :
        1. graph1 lance et s'interrompt
        2. graph2 (nouvelle instance) reprend depuis le checkpoint Redis
        3. Le résultat final contient la décision transmise au Command(resume=...)

        Si thread_id était différent, graph2 démarrerait un nouveau workflow
        indépendant et l'assert final échouerait.
        """
        # Étape 1 : graph1 exécute jusqu'à l'interrupt
        graph1 = _build_minimal_graph(redis_saver)
        result1 = graph1.invoke({"step": "start", "result": None}, config=CONFIG)
        assert result1.get("__interrupt__")

        # Étape 2 : graph2 simule le redémarrage
        graph2 = _build_minimal_graph(redis_saver)

        # Vérification intermédiaire : l'état a survécu
        snap = graph2.get_state(CONFIG)
        assert "wait_node" in snap.next

        # Étape 3 : resume depuis graph2 avec la décision humaine
        # MÊME CONFIG que graph1 — sans ça, pas de recovery
        final = graph2.invoke(Command(resume="approved"), config=CONFIG)

        assert not final.get("__interrupt__"), "Le workflow doit être terminé"
        assert final["result"] == "approved", (
            "La décision humaine doit être transmise correctement à travers le checkpoint"
        )
        assert final["step"] == "completed"
