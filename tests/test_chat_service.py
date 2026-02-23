import uuid
import pytest

from backend.chat_service import load_and_validate_request, get_session_and_conversation, format_response


def test_load_and_validate_request_valid():
    data = {"message": "Hello"}
    payload, error = load_and_validate_request(data)
    assert error is None
    assert payload["message"] == "Hello"


@pytest.mark.django_db
def test_get_session_and_conversation_creates():
    # Call with no session_id to create new session and conversation
    session, conversation = get_session_and_conversation(None, user_id=None)
    assert session is not None
    assert conversation is not None
    assert conversation.session == session


def test_format_response_basic():
    resp = format_response(
        answer="Hi",
        session_id=str(uuid.uuid4()),
        conversation_id=str(uuid.uuid4()),
        intent="greeting",
        confidence=0.9,
        entities={},
        pdf_url=None,
        response_time_ms=120,
        agent_id="faq",
    )
    assert resp["response"] == "Hi"
    assert resp["intent"] == "greeting"
    assert resp["response_time_ms"] == 120
