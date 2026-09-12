"""
Synthesis Agent Nodes: Generates the final cited answer from retrieved chunks.
Nodes: context_builder → llm_generator
"""
import re

from langchain_core.messages import AIMessage, HumanMessage
from loguru import logger

from core.llm import get_llm
from prompts.synthesis_prompt import synthesis_prompt
from schemas.agent_state import AgentState


def _format_chat_history(messages: list) -> str:
    """Formats message list for the synthesis prompt."""
    history_lines = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            history_lines.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage) and not msg.content.startswith("[INTERNAL]"):
            history_lines.append(f"Assistant: {msg.content}")
    return "\n".join(history_lines[-6:])  # last 3 exchanges


def context_builder_node(state: AgentState) -> dict:
    """
    Assembles the context string from retrieved chunks for the LLM prompt.
    Performs a light pre-check to ensure chunks are available.
    """
    logger.info("--- SYNTHESIS AGENT: [1/2] Building Context ---")
    chunks = state.get("retrieved_chunks", [])
    if not chunks:
        logger.warning("No retrieved chunks available for synthesis.")
        return {"_context": "No relevant context was found in the document."}

    context = "\n\n---\n\n".join(chunks)
    logger.info(f"Context assembled from {len(chunks)} chunks ({len(context)} chars).")
    return {"_context": context}


def llm_generator_node(state: AgentState) -> dict:
    """
    Calls the LLM with the synthesis prompt to generate a grounded,
    cited answer from the retrieved document context.
    """
    logger.info("--- SYNTHESIS AGENT: [2/2] Generating Answer ---")
    context = state.get("_context", "No context available.")
    question = state.get("question", "")
    chat_history = _format_chat_history(state.get("messages", []))

    llm = get_llm()
    chain = synthesis_prompt | llm
    response = chain.invoke(
        {
            "context": context,
            "question": question,
            "chat_history": chat_history,
        }
    )

    answer = response.content.strip()

    # Extract citation references like [Chunk 1], [Chunk 3], etc.
    citations = re.findall(r"\[Chunk \d+\]", answer)
    citations = list(dict.fromkeys(citations))  # deduplicate while preserving order

    logger.success(f"Answer generated. Length: {len(answer)} chars. Citations: {citations}")

    return {
        "final_answer": answer,
        "citations": citations,
        # Reset retrieval state so next question starts fresh
        "retrieved_chunks": [],
        "rewritten_query": None,
        "_context": None,
        "messages": [
            HumanMessage(content=question),
            AIMessage(content=answer),
        ],
    }
