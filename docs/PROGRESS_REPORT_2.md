# Progress Report 2: Module Implementation & Integration

**Project:** FAIX Chatbot (Faculty of Artificial Intelligence and Cyber Security)  
**Date:** January 2026  
**Phase:** Development & Integration

---

## 1. Executive Summary
This report covers the **Module Implementation** and **Module Integration** phases of the FAIX Chatbot project. During this period, the team successfully built the core functional modules (Frontend, Backend API, Intelligence Engine, Data Layer) and integrated them into a cohesive Retrieval-Augmented Generation (RAG) system. A key highlight is the implementation of a "Demo Mode" to visualize internal system processes (NLP, RAG, LLM) for stakeholders.

---

## 2. Module Implementation Phase
In this phase, distinct components were developed in isolation to ensure modularity and testability.

### 2.1 Frontend Module (Client-Side)
*   **Chat Interface**: Developed a responsive, JavaScript-based chat widget (`chat.js`) embedded in Django templates. Features include:
    *   Real-time message streaming.
    *   Markdown rendering for rich text responses.
    *   Voice-to-Text input support.
*   **Demo Mode Enhancements**: Implemented a specialized presentation layer:
    *   **Quick Actions**: One-click buttons for common queries (e.g., "Timetable", "Staff").
    *   **Tech Badges**: Visual indicators showing active technologies (NLP, RAG, LLM) per response.
    *   **Metrics Display**: Real-time visualization of response latency and confidence scores.

### 2.2 Backend Core Module (Server-Side)
*   **API Development**: Built robust REST API endpoints (`/api/chat/`) using Django REST Framework.
*   **Session Management**: Implemented stateful sessions to track conversation history, enabling context-aware follow-up questions.
*   **Guardrails**: Developed security middleware to sanitize inputs and filter out gibberish or off-topic queries before they reach expensive AI models.

### 2.3 Intelligence Module (AI Core)
*   **Agent System**: Created specialized agents to handle distinct domains:
    *   **Staff Agent**: Validates faculty names against a safe list to prevent hallucinations.
    *   **Schedule Agent**: Parses semantic queries about time and venues.
    *   **FAQ Agent**: Handles general inquiries using semantic similarity.
*   **NLP Processor**: Integrated **Spacy** for intent classification and entity extraction.
*   **RAG Retriever**: Implemented **Sentence-Transformers** to generate embeddings and retrieve relevant chunks from the local JSON knowledge base.

### 2.4 LLM Interface Module
*   **Ollama Client**: Developed a Python wrapper (`llm_client.py`) to communicate with the local **Ollama** instance. This allows the system to swap underlying models (e.g., Llama 3.2, Mistral) without changing application logic.

---

## 3. Module Integration Phase
In this phase, the isolated modules were connected to form the complete end-to-end system.

### 3.1 Frontend-Backend Integration
*   **API Connection**: Connected the React frontend to the Django backend via asynchronous `fetch` calls.
*   **State Sync**: Ensured session IDs are persisted in `localStorage` and synced with the backend SQLite database, allowing users to refresh the page without losing context.

### 3.2 RAG Pipeline Integration
*   **Context Injection**: Integrated the **Retriever** with the **LLM Client**. The pipeline now:
    1.  Receives a user query.
    2.  Retrieves relevant context (JSON/CSV data).
    3.  Injects this context into the system prompt.
    4.  Generates a grounded response via Ollama.
*   **Hybrid Search**: Combined keyword search (BM25-style) with semantic vector search to improve retrieval accuracy for specific terms (e.g., staff names) vs. conceptual questions.

### 3.3 Agent Orchestration
*   **Router Logic**: Integrated the "Agent Router" in `views.py`. The system now dynamically routes queries to the best-suited agent based on intent confidence scores.
    *   *Example*: "Where is Dr. Smith?" -> **Staff Agent**
    *   *Example*: "When is the AI exam?" -> **Schedule Agent**

### 3.4 External Service Integration
*   **Local AI Service**: Successfully integrated the Python backend with the locally running **Ollama** service via HTTP/API.
*   **Firebase (Optional)**: Integrated a Firebase service module for real-time analytics logging and conversation monitoring (configurable via environment variables).

---

## 4. Challenges & Solutions

| Challenge | Solution |
| :--- | :--- |
| **Hallucinations** | Implemented a "Safe List" verification step. If the LLM generates a staff name not found in the official directory, the system flags it and falls back to a search. |
| **Response Latency** | Implemented a "Fast Path" for common queries (Greetings, "What can you do?"). These return cached responses immediately, bypassing the LLM. |
| **Context Window** | Limited conversation history sent to the LLM to the last 10 turns to prevent context overflow and maintain speed. |

---

## 5. Conclusion
The FAIX Chatbot has successfully moved from individual component development to a fully integrated, functional prototype. The system effectively demonstrates the RAG architecture, responding accurately to domain-specific queries while running entirely on local infrastructure. The addition of "Demo Mode" significantly aids in presenting the system's technical capabilities to stakeholders.

**Next Steps:**
*   User Acceptance Testing (UAT).
*   Refining the Knowledge Base with more academic data.
*   Performance tuning for concurrent users.
