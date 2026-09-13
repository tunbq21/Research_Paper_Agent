"""
Query Rewriter prompt: instructs the Retrieval agent to rewrite the
user's question to maximize vector search precision.
"""
from langchain_core.prompts import ChatPromptTemplate

QUERY_REWRITER_SYSTEM = """You are an expert at reformulating user questions to maximize the effectiveness of semantic vector search over academic research papers.

Given the user's original question and the conversation history, your task is to:
1. Expand any abbreviations or informal terms into precise academic language.
2. Incorporate relevant context from the conversation history to make the query self-contained.
3. Add synonyms or related concepts that would help retrieve relevant passages.
4. Keep the rewritten query concise (1-3 sentences).

Output ONLY the rewritten query. No explanation, no preamble.
"""

query_rewriter_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", QUERY_REWRITER_SYSTEM),
        (
            "human",
            "Conversation history:\n{chat_history}\n\n"
            "User's current question: {question}\n\n"
            "Rewritten query for vector search:",
        ),
    ]
)
