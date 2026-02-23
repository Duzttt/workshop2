"""
Backend chat service skeleton

This module provides a lightweight service-layer API to support the
monolithic Django chat_api. The goal is to expose small, testable
functions that can be composed by the Django view layer without
re-implementing heavy logic in views.

NOTE: This is a minimal, skeleton implementation suitable for an MVP
refactor. It deliberately avoids tight coupling to the NLP/KB/LLM stack
to keep tests fast and predictable. Real routing/NLP logic can be
wired in progressively.
"""

from __future__ import annotations

import uuid

from typing import Any, Dict, Optional, Tuple

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from django_app.models import UserSession, Conversation


def load_and_validate_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """Basic validation of the incoming payload.

    Returns a tuple of (payload, error). If error is not None, payload
    is the original data.
    """
    if not isinstance(data, dict):
        return data, "Invalid payload: expected a JSON object"

    message = data.get("message")
    if message is None:
        return data, "Missing required field: message"
    if not isinstance(message, str):
        return data, "Invalid type for field: message"
    # Basic length guard can live here as a first-class validation point
    return data, None


def get_session_and_conversation(session_id: Optional[str], user_id: Optional[str]) -> Tuple[UserSession, Conversation]:
    """Get or create a session and a recent active conversation for a user.

    This mirrors the lightweight behavior used in the view layer but
    keeps the logic isolated for easier testing.
    """
    session: UserSession
    if session_id:
        try:
            session = UserSession.objects.get(session_id=session_id, is_active=True)
        except ObjectDoesNotExist:
            session = UserSession.objects.create(session_id=session_id, user_id=user_id or None)
    else:
        session = UserSession.objects.create(session_id=str(uuid.uuid4()), user_id=user_id or None)

    # Find or create a recent active conversation for this session
    conversation = Conversation.objects.filter(session=session, is_active=True).order_by('-created_at').first()
    if not conversation:
        conversation = Conversation.objects.create(session=session, user_id=user_id or None, title="New Conversation")

    return session, conversation


def determine_routing_and_context(
    user_message: str,
    context: Optional[Dict[str, Any]] = None,
    history: Optional[list] = None,
) -> Dict[str, Any]:
    """A very small routing shim.

    Returns a dict containing agent_id, intent, language_code, and an
    updated context. The MVP here defaults to a generic FAQ routing path
    and can be extended to implement the full routing logic incrementally.
    """
    return {
        "agent_id": "faq",
        "intent": "about_faix",
        "language_code": "en",
        "context": context or {},
    }


def process_query_through_nlp_and_kb(
    user_message: str,
    context: Dict[str, Any],
) -> Tuple[str, Dict[str, Any]]:
    """Placeholder for NLP/KB/LLM processing.

    MVP: return an empty answer so the caller can proceed with LLM as
    in the original pipeline. This function is intended to be swapped with
    a real implementation that talks to KB/LLM.
    """
    # In MVP, we simply return no answer, signaling to the caller to
    # fall back to LLM or knowledge base as appropriate.
    return "", {"context": context}


def format_response(
    answer: str,
    session_id: str,
    conversation_id: str,
    intent: str,
    confidence: float,
    entities: Dict[str, Any],
    pdf_url: Optional[str] = None,
    response_time_ms: Optional[int] = None,
    agent_id: str = "faq",
) -> Dict[str, Any]:
    """Format the final response envelope to match the backend API shape."""
    return {
        "response": answer,
        "session_id": session_id,
        "conversation_id": conversation_id,
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
        "timestamp": timezone.now().isoformat(),
        "pdf_url": pdf_url,
        "response_time_ms": response_time_ms if response_time_ms is not None else 0,
        "agent_id": agent_id,
    }


__all__ = [
    "load_and_validate_request",
    "get_session_and_conversation",
    "determine_routing_and_context",
    "process_query_through_nlp_and_kb",
    "format_response",
]
