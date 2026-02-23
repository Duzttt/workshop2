# Chat API Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Break the monolithic chat_api in django_app/views.py into a modular service layer with clear boundaries, enabling easier testing, maintenance, and future enhancements.

**Architecture:** Introduce a dedicated chat service module that encapsulates: request validation, session/conversation management, language/routing, agent dispatch, NLP/LLM interactions, KB/RAG flows, caching, and fallbacks. chat_api will be a thin orchestration layer that delegates to the service.

**Tech Stack:** Python, Django, existing NLP/LLM/KBA components, unit/integration tests, documentation.

---

## Task Structure

### Task 1: Create Chat Service Module
**Files:** `backend/chat_service.py`
**Goal:** Encapsulate core chat workflow into testable functions.
**Key functions (examples):**
- `load_and_validate_request(data: dict) -> (dict, error)`
- `get_session_and_conversation(session_id, user_id)`
- `determine_routing_and_context(...)`
- `process_nlp_and_intent(text, context) -> (intent, confidence, entities, normalized_query)`
- `resolve_response_via_kb_or_llm(...) -> str`
- `build_final_response(...) -> dict`

### Task 2: Extract Validation Layer
**Files:** `backend/chat_service.py` (or `backend/validators.py`)
**Goals:** Validate message length, JSON payload structure, and basic schema checks. Return structured errors for the API.

### Task 3: Extract Session & Conversation Management
**Files:** `backend/chat_service.py`
**Goals:** Centralize creation/retrieval of UserSession and Conversation with consistent context handling.

### Task 4: Extract Language Detection & Routing
**Files:** `backend/chat_service.py`
**Goals:** Isolate quick language detection, greeting/farewell routing, capability/query handling.

### Task 5: Extract Agent Routing Logic
**Files:** `backend/chat_service.py`
**Goals:** Decide on `agent_id` based on staff, schedule, or FAQ routing rules; allow easy extension.

### Task 6: Extract LLM Call & Response Processing
**Files:** `backend/chat_service.py`
**Goals:** Build prompt/messages, call LLM (via `get_llm_client`), handle timeouts, temperature, and response parsing; include fallback paths.

### Task 7: Extract Caching Layer
**Files:** `backend/chat_service.py` and cache usage
**Goals:** Centralize response caching with TTL rules; ensure fast cache hits for common queries.

### Task 8: Extract Error Handling & Fallback Logic
**Files:** `backend/chat_service.py`
**Goals:** Implement consistent fallback strategies when KB/LLM fail; ensure user-friendly multilingual fallbacks.

### Task 9: Integrate Chat API with Service Layer
**Files:** `django_app/views.py` (refactor to call `backend.chat_service`)
**Goals:** Replace inlined logic with service calls; retain existing endpoints and payload formats.

### Task 10: Testing Plan
**Files:** `tests/`
**Goals:** Write unit tests for each extracted function, and integration tests for `chat_api` orchestrating the service layer. Include tests for:
- Validation errors
- Session/Conversation flows
- NLP/Intent handling
- KB/LLM fallback paths
- Caching behavior

### Task 11: Documentation & DRI
**Files:** `docs/` ancillary docs
**Goals:** Update architecture overview, runbooks, and developer onboarding docs.

---

## Execution Options

After saving this plan:

**Option 1: Subagent-Driven (this session)** - I dispatch fresh subagents per task, review between tasks, fast iteration.
**Option 2: Parallel Session (separate)** - Open a new session with executing-plans, batch execution with checkpoints.

Which approach would you like to proceed with? If you prefer, I can start with Option 1 in this session and create a new patch per task as we complete them.

---

Acceptance Criteria
- Chat API is decoupled into a service layer with clearly defined interfaces.
- All existing request/response formats remain backward-compatible for now.
- Tests cover critical paths and edge cases for validation, routing, KB/LLM, and caching.
- Documentation updated to reflect architecture and usage.
