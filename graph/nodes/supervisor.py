"""
Supervisor Node: Determines which agent to activate next by
analyzing the current AgentState and applying routing rules.
"""
from langchain_core.messages import HumanMessage
from loguru import logger

from core.llm import get_llm
from prompts.supervisor_prompt import supervisor_prompt
from schemas.agent_state import AgentState

# Valid routing destinations
VALID_ROUTES = {"ingestion_agent", "retrieval_agent", "synthesis_agent", "FINISH"}


def supervisor_node(state: AgentState) -> dict:
    """
    The Supervisor node: reads state and decides which agent runs next.

    Uses an LLM call with a strictly structured prompt to determine routing.
    Falls back to deterministic rule-based routing if the LLM response is
    not one of the expected agent names.

    Args:
        state: The current shared AgentState.

    Returns:
        A dict with `next_agent` key indicating the next node to activate.
    """
    logger.info("--- SUPERVISOR: Evaluating state and routing ---")

    # Deterministic fast-path routing (no LLM call needed for clear cases)
    if not state.get("is_ingested") and state.get("pdf_path"):
        logger.info("Supervisor → ingestion_agent (PDF not yet ingested)")
        return {"next_agent": "ingestion_agent"}

    if not state.get("retrieved_chunks") and not state.get("final_answer"):
        logger.info("Supervisor → retrieval_agent (no chunks retrieved yet)")
        return {"next_agent": "retrieval_agent"}

    if state.get("retrieved_chunks") and not state.get("final_answer"):
        logger.info("Supervisor → synthesis_agent (chunks ready, no answer yet)")
        return {"next_agent": "synthesis_agent"}

    if state.get("final_answer"):
        logger.info("Supervisor → FINISH (final answer is ready)")
        return {"next_agent": "FINISH"}

    # Fallback: LLM-based routing for complex edge cases
    logger.warning("Supervisor: falling back to LLM-based routing")
    llm = get_llm()
    chain = supervisor_prompt | llm

    response = chain.invoke(
        {
            "is_ingested": state.get("is_ingested", False),
            "pdf_path": state.get("pdf_path"),
            "question": state.get("question", ""),
            "retrieved_chunks_count": len(state.get("retrieved_chunks", [])),
            "final_answer": state.get("final_answer"),
        }
    )

    route = response.content.strip()
    if route not in VALID_ROUTES:
        logger.error(f"Supervisor received invalid route '{route}', defaulting to FINISH")
        route = "FINISH"

    logger.info(f"Supervisor (LLM) → {route}")
    return {"next_agent": route}
