"""
GenVendorAI Chat Routes
FastAPI endpoints for conversational AI chatbot and procurement copilot.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ai.chatbot import get_chatbot

router = APIRouter(prefix="/api/chat", tags=["Vendor Intelligence Chatbot"])


class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="User query / prompt")
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="Previous conversation turns")


class ChatMessageResponse(BaseModel):
    reply: str
    sources: List[str]
    suggested_actions: List[str]


@router.post("/message", response_model=ChatMessageResponse)
def handle_chat_message(request: ChatMessageRequest):
    """
    Processes a natural-language query over the vendor master registry and AI risk engine.
    Returns structured markdown reply, referenced sources, and follow-up chips.
    """
    try:
        bot = get_chatbot()
        result = bot.process_message(request.message, history=request.history)
        return ChatMessageResponse(
            reply=result["reply"],
            sources=result.get("sources", []),
            suggested_actions=result.get("suggested_actions", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/suggestions")
def get_chat_suggestions():
    """Returns contextual quick-prompt suggestion chips for the chat interface."""
    return {
        "suggestions": [
            "Give me an overview of all master vendors",
            "Which vendors are on the high-risk watchlist?",
            "Tell me about Zenith Cloud Technologies",
            "Find civil construction suppliers in Maharashtra",
            "How is statutory compliance and risk calculated?",
            "What are the banking details of BuildCraft Infrastructure?"
        ]
    }
