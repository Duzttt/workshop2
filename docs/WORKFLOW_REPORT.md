# FAIX Chatbot Workflow Report

## 1. Introduction
This document details the step-by-step processing workflow of the FAIX Chatbot, from the moment a user sends a message to the final response delivery. The system is designed with multiple efficiency layers, prioritizing speed for simple queries (Fast Path) and depth for complex ones (RAG + LLM).

## 2. Detailed Workflow Steps

### Step 1: Input Validation & Pre-processing
**Component**: `django_app/views.py` (API View)
Before any AI processing occurs, the system sanitizes and filters the input:
1.  **Rate Limiting**: Ensures the user isn't spamming the server.
2.  **Gibberish Detection**: Checks for random character strings (e.g., "asdfjkl") to reject invalid inputs early.
3.  **Off-Topic Filter**: Analyzes the query to ensure it relates to the faculty domain (academic, staff, facilities).

### Step 2: Fast-Path Routing
**Goal**: Sub-second response time for common interactions.
The system checks for specific patterns that don't require AI inference:
*   **Greetings/Farewells**: "Hi", "Bye", "Thanks" trigger pre-written, randomized responses.
*   **Capabilities**: "What can you do?" triggers a static help message.
*   **If Matched**: The system returns the cached response immediately, skipping all subsequent steps.

### Step 3: Intent Classification & Agent Selection
**Component**: `backend/chatbot/logic.py` & `agents.py`
If the query is unique, the system determines *what* the user wants:
1.  **Keyword Priority**: Checks for strong keywords first (e.g., "email" -> Staff Agent, "timetable" -> Schedule Agent).
2.  **NLP Classification**: Uses Spacy to detect semantic intent (e.g., `program_info`, `admission_req`).
3.  **Agent Routing**:
    *   **Staff Agent**: Specialized in faculty directory, contacts, and office locations.
    *   **Schedule Agent**: Handles academic calendars, class times, and venues.
    *   **FAQ Agent**: Handles general inquiries about programs, fees, and facilities.

### Step 4: Retrieval-Augmented Generation (RAG)
**Component**: `backend/chatbot/knowledge_base.py`
The selected agent retrieves accurate data to ground the response:
1.  **Semantic Search**: Converts the user query into a vector embedding and finds matching chunks in the Knowledge Base (JSON/CSV files).
2.  **Structured Lookup**: For specific agents, it looks up exact matches (e.g., finding "Dr. Smith" in `staff_contacts.json`).
3.  **Direct Answer Check**: If the retrieval finds a high-confidence factual answer (e.g., "The Dean is Prof. X"), it skips the LLM and returns this fact directly to ensure 100% accuracy.

### Step 5: LLM Generation
**Component**: `backend/llm/llm_client.py` (Ollama)
If a natural language explanation is needed:
1.  **Prompt Construction**: The system builds a prompt containing:
    *   **System Instruction**: "You are a helpful assistant for FAIX..."
    *   **Context**: The retrieved data from Step 4.
    *   **User Query**: The original question.
2.  **Inference**: The local Llama 3.2 model generates a response based *only* on the provided context.

### Step 6: Response Validation
**Component**: `django_app/views.py` (Post-processing)
Safety checks before showing the user:
1.  **Hallucination Guard**: For staff queries, the system cross-references any names in the generated text against the official database. If the LLM invented a name, it is corrected or flagged.
2.  **Inadequacy Check**: If the LLM says "I don't know", the system falls back to a standard "Please contact the office" message.

### Step 7: Delivery
The final text is formatted (Markdown) and sent back to the React frontend via JSON.
