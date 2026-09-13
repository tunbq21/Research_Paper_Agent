"""
FastAPI Server for the Research Paper Summarizer Agent.

Run with:
    uv run uvicorn api.server:app --reload --port 8000
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage
from loguru import logger
from pydantic import BaseModel

from graph.graph import app as agent_graph
from schemas.agent_state import AgentState

app = FastAPI(title="Research Paper Agent API", version="1.0.0")

# Allow CORS for React frontend (Vite default is 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    collection_name: str
    question: str
    history: list[dict[str, str]] = []  # [{"role": "user", "content": "..."}]


class ChatResponse(BaseModel):
    answer: str
    citations: list[str]
    collection_name: str
    messages: list[dict[str, Any]]


def _reconstruct_langchain_messages(history_dicts: list[dict]) -> list:
    """Converts a list of dicts from frontend into LangChain message objects."""
    messages = []
    for msg in history_dicts:
        if msg.get("role") == "user":
            messages.append(HumanMessage(content=msg.get("content", "")))
        elif msg.get("role") == "assistant":
            messages.append(AIMessage(content=msg.get("content", "")))
    return messages


def _serialize_langchain_messages(messages: list) -> list[dict]:
    """Converts LangChain message objects to dicts for frontend."""
    serialized = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            serialized.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            # Do not send back [INTERNAL] thoughts to frontend if not desired
            # But for simplicity, we send them all. The frontend can filter.
            serialized.append({"role": "assistant", "content": msg.content})
    return serialized


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint to handle PDF uploads.
    Saves the file temporarily and triggers the Ingestion Agent.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    logger.info(f"Received upload request for {file.filename}")

    # Create a temporary file to store the upload
    fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    try:
        with open(tmp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Trigger Ingestion
        ingestion_state = AgentState(
            messages=[],
            question="",
            pdf_path=tmp_path,
            is_ingested=False,
            collection_name=None,
            rewritten_query=None,
            retrieved_chunks=[],
            final_answer=None,
            citations=[],
            next_agent="",
        )

        logger.info("Invoking graph for ingestion...")
        result = agent_graph.invoke(ingestion_state)

        if not result.get("is_ingested"):
            raise HTTPException(status_code=500, detail="Ingestion pipeline failed.")

        return {
            "status": "success",
            "collection_name": result["collection_name"],
            "filename": file.filename,
        }

    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint to handle user questions.
    Triggers the Retrieval and Synthesis Agents.
    """
    logger.info(f"Received chat request for collection '{request.collection_name}'")

    langchain_history = _reconstruct_langchain_messages(request.history)

    qa_state = AgentState(
        messages=langchain_history,
        question=request.question,
        pdf_path=None,  # Not needed for retrieval
        is_ingested=True,
        collection_name=request.collection_name,
        rewritten_query=None,
        retrieved_chunks=[],
        final_answer=None,
        citations=[],
        next_agent="",
    )

    try:
        result = agent_graph.invoke(qa_state)

        answer = result.get("final_answer", "Error: No answer generated.")
        citations = result.get("citations", [])
        updated_messages = _serialize_langchain_messages(result.get("messages", []))

        return ChatResponse(
            answer=answer,
            citations=citations,
            collection_name=result["collection_name"],
            messages=updated_messages,
        )

    except Exception as e:
        logger.exception("Chat failed")
        raise HTTPException(status_code=500, detail=str(e))
