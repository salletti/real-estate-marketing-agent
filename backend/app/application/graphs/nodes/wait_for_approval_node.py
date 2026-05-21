from langgraph.types import interrupt

from app.application.graphs.state import SocialMediaState


def wait_for_approval_node(state: SocialMediaState) -> dict:
    # 1) Premier passage: interrupt() met le workflow en pause (checkpoint + sortie avec __interrupt__).
    # 2) Reprise: invoke(Command(resume="approved" | "rejected"), config) revient ici.
    # 3) À la reprise, interrupt() "retourne" la valeur de resume, affectée à decision.
    # C'est une pause métier temporaire, pas une fin de workflow.
    decision = interrupt("Waiting for human approval")
    return {"approval_status": decision}
