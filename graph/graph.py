"""
Graph Assembly: Builds and compiles the LangGraph StateGraph for the
multi-agent Research Paper RAG system.

Agent flow:
  START
    └─► supervisor ─► ingestion_agent (if PDF not ingested)
                   ─► retrieval_agent (query rewrite → vector search)
                   ─► synthesis_agent (context build → LLM generate)
                   ─► END
"""
from langgraph.graph import END, START, StateGraph

from graph.nodes.ingestion_nodes import (
    embedder_indexer_node,
    pdf_parser_node,
    text_chunker_node,
)
from graph.nodes.retrieval_nodes import query_rewriter_node, vector_search_node
from graph.nodes.supervisor import supervisor_node
from graph.nodes.synthesis_nodes import context_builder_node, llm_generator_node
from schemas.agent_state import AgentState


def _route_from_supervisor(state: AgentState) -> str:
    """
    Conditional edge function: reads `next_agent` from state
    and returns the name of the next node to activate.
    """
    return state.get("next_agent", "FINISH")


def build_graph() -> StateGraph:
    """
    Constructs and compiles the full multi-agent StateGraph.

    Node layout:
    - supervisor           : Orchestrator / router
    - pdf_parser           : Ingestion Agent node 1
    - text_chunker         : Ingestion Agent node 2
    - embedder_indexer     : Ingestion Agent node 3
    - query_rewriter       : Retrieval Agent node 1
    - vector_search        : Retrieval Agent node 2
    - context_builder      : Synthesis Agent node 1
    - llm_generator        : Synthesis Agent node 2

    Returns:
        A compiled LangGraph app ready for invocation.
    """
    graph = StateGraph(AgentState)

    # ── Register all nodes ──────────────────────────────────────────────
    graph.add_node("supervisor", supervisor_node)

    # Ingestion Agent
    graph.add_node("pdf_parser", pdf_parser_node)
    graph.add_node("text_chunker", text_chunker_node)
    graph.add_node("embedder_indexer", embedder_indexer_node)

    # Retrieval Agent
    graph.add_node("query_rewriter", query_rewriter_node)
    graph.add_node("vector_search", vector_search_node)

    # Synthesis Agent
    graph.add_node("context_builder", context_builder_node)
    graph.add_node("llm_generator", llm_generator_node)

    # ── Entry point ─────────────────────────────────────────────────────
    graph.add_edge(START, "supervisor")

    # ── Supervisor conditional routing ──────────────────────────────────
    graph.add_conditional_edges(
        "supervisor",
        _route_from_supervisor,
        {
            "ingestion_agent": "pdf_parser",
            "retrieval_agent": "query_rewriter",
            "synthesis_agent": "context_builder",
            "FINISH": END,
        },
    )

    # ── Ingestion Agent: sequential pipeline ────────────────────────────
    graph.add_edge("pdf_parser", "text_chunker")
    graph.add_edge("text_chunker", "embedder_indexer")
    graph.add_edge("embedder_indexer", "supervisor")  # Return to supervisor

    # ── Retrieval Agent: sequential pipeline ────────────────────────────
    graph.add_edge("query_rewriter", "vector_search")
    graph.add_edge("vector_search", "supervisor")  # Return to supervisor

    # ── Synthesis Agent: sequential pipeline ────────────────────────────
    graph.add_edge("context_builder", "llm_generator")
    graph.add_edge("llm_generator", "supervisor")  # Return to supervisor

    return graph.compile()


# Compiled graph singleton — import this in main.py
app = build_graph()
