# Progress Report 3: Testing Phase & System Demonstration

**Project:** FAIX Chatbot (Faculty of Artificial Intelligence and Cyber Security)  
**Date:** January 2026  
**Phase:** Testing, Validation & Demonstration

---

## 1. Executive Summary
This report outlines the **Testing Phase** and **System Demonstration** activities for the FAIX Chatbot. During this period, the team executed a comprehensive testing strategy covering unit, integration, and performance metrics. Following validation, the system was prepared for demonstration using a specialized "Demo Mode" to showcase its capabilities to stakeholders.

---

## 2. Testing Phase
The testing phase utilized a multi-layered approach to ensure system reliability, accuracy, and performance.

### 2.1 Unit Testing
Focused on validating individual components in isolation.
*   **Agent Logic**: Verified that specialized agents (`StaffAgent`, `ScheduleAgent`, `FAQAgent`) correctly load and parse their respective JSON data sources.
    *   *Script*: `tests/test_separated_data_agents.py`
*   **Intent Classification**: Validated the confidence scoring mechanism of the NLP engine to ensure accurate routing.
    *   *Script*: `tests/test_confidence.py`
*   **Name Matching**: Tested fuzzy matching algorithms to ensure user typos in staff names (e.g., "Smit" vs "Smith") are handled correctly.
    *   *Script*: `scripts/test_staff_name_matching.py`

### 2.2 Integration Testing
Focused on the end-to-end data flow from API input to response generation.
*   **API & Routing**: Verified that HTTP requests to `/api/chat/` are correctly sanitized, routed to the proper agent, and returned with valid JSON.
    *   *Script*: `tests/test_chatbot_performance.py`
*   **RAG Pipeline**: Confirmed that the Retriever successfully fetches context from the Knowledge Base and injects it into the LLM prompt.
*   **Multi-Language Support**: Validated the system's ability to process and respond to queries in English, Malay, Chinese, and Arabic.
    *   *Script*: `tests/test_multiple_language.py`

### 2.3 Performance Testing
Focused on system responsiveness and efficiency.
*   **Latency Benchmarking**: Measured response times for cached vs. non-cached queries.
    *   *Result*: Fast-path queries (greetings) avg <20ms; LLM queries avg <3s (on local hardware).
*   **Concurrency**: Simulated multiple sequential requests to ensure the Django server and Ollama instance handle load without crashing.

### 2.4 User Acceptance Testing (UAT) Simulation
*   **Hallucination Check**: Verified that asking for non-existent staff members triggers a fallback response rather than a fabricated one.
*   **Feedback System**: Tested the "Thumbs Up/Down" mechanism to ensure user feedback is correctly logged to the database/Firebase.

---

## 3. System Demonstration
To effectively showcase the system's complex internal logic to non-technical stakeholders, a specialized **Demo Mode** was developed and utilized.

### 3.1 Demo Mode Features
The demonstration interface overlays technical insights onto the standard chat UI:
*   **Real-Time Metrics**: Displays processing time (ms) and intent confidence scores (%) for each message.
*   **Tech Stack Visualization**: Shows "badges" (NLP, RAG, LLM) indicating which technologies were active for a given response.
*   **Process Visualization**: A "Processing Steps" indicator shows the backend workflow in real-time:
    1.  🔍 Analyzing Query
    2.  🧠 Detecting Intent
    3.  📚 Retrieving Context
    4.  🤖 Generating Response
*   **Quick Actions**: Pre-configured buttons (e.g., "Show Timetable", "Contact Dean") to instantly demonstrate key scenarios without manual typing.

### 3.2 Demonstration Scenarios
The system was demonstrated using the following key scenarios:

| Scenario | Objective | Outcome |
| :--- | :--- | :--- |
| **General Inquiry** | Ask "What programs are offered?" | System retrieves program list from JSON and summarizes via LLM. |
| **Staff Search** | Ask "Email for Dr. Chong" | System identifies "Staff" intent, retrieves exact email from `staff_contacts.json`. |
| **Schedule Check** | Ask "When is the AI class?" | System identifies "Schedule" intent, finds venue/time in `schedule.json`. |
| **Multi-Turn Chat** | Ask "Who is the Dean?" -> "Email?" | System maintains context to provide the Dean's email in the second turn. |
| **Error Handling** | Ask "Recipe for cake" | System detects "Off-Topic" intent and politely refuses. |

---

## 4. Conclusion
The Testing Phase confirmed that the FAIX Chatbot meets its functional requirements with high accuracy and stability. The subsequent System Demonstration successfully illustrated the project's value, proving that the local RAG architecture delivers privacy-preserving, context-aware AI assistance effectively.

**Deliverables:**
*   Comprehensive Test Suite (`tests/` directory).
*   Demo Video/Script (`docs/demo/DEMO_VIDEO_SCRIPT.md`).
*   Performance Benchmark Reports.
