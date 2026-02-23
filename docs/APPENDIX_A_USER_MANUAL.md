# Appendix A: User Manual and Installation Guide

## 1. Introduction
This manual provides the comprehensive instructions necessary to replicate the development environment for the FAIX Chatbot project at UTeM. Following these steps will ensure all dependencies (backend, frontend, and AI models) are correctly configured.

---

## 2. Environment Setup

### 2.1 Prerequisites
Ensure your system meets the following requirements:
*   **Operating System**: Windows 10/11, macOS, or Linux.
*   **Python**: Version 3.10 or higher.
*   **Node.js**: Version 16+ (for frontend dependencies).
*   **Git**: For version control.

### 2.2 Backend Setup (Python)
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/shanle1117/workshop2.git
    cd workshop2
    ```

2.  **Create a Virtual Environment**:
    It is recommended to use a virtual environment to manage Python dependencies.
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    Install the required Python packages from `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

### 2.3 Frontend Setup (Node.js)
1.  **Install Node Modules**:
    Navigate to the project root (where `package.json` is located) and install dependencies.
    ```bash
    npm install
    ```

---

## 3. LLM Configuration (Ollama)

The chatbot relies on **Ollama** to run the Llama 3.2 model locally.

1.  **Install Ollama**:
    *   Download the installer from [ollama.com](https://ollama.com).
    *   Follow the installation wizard for your operating system.

2.  **Pull the Model**:
    Open a new terminal and run the following command to download the Llama 3.2 (3 billion parameter) model.
    ```bash
    ollama pull llama3.2:3b
    ```

3.  **Verify Installation**:
    Run the model briefly to ensure it works.
    ```bash
    ollama run llama3.2:3b "Hello, are you ready?"
    ```
    (Press `Ctrl+D` to exit the chat).

4.  **Start Ollama Server**:
    Ensure the Ollama server is running (it usually runs in the background). If not, start it:
    ```bash
    ollama serve
    ```

---

## 4. Configuration (.env)

Create a file named `.env` in the root directory of the project. Copy the template below and update the values if necessary.

**File:** `.env`
```ini
# ==============================================
# Django Settings
# ==============================================
# Security key for Django (keep secret in production)
SECRET_KEY=django-insecure-your-secret-key-here
# Set to True for development debugging
DEBUG=True

# ==============================================
# LLM / AI Settings
# ==============================================
# Provider (ollama)
LLM_PROVIDER=ollama
# Base URL for local Ollama instance
OLLAMA_BASE_URL=http://localhost:11434
# Model to use (must match the one pulled)
OLLAMA_MODEL=llama3.2:3b
# Timeout in seconds for AI responses
LLM_REQUEST_TIMEOUT=60

# ==============================================
# Optional Services
# ==============================================
# Enable Firebase for analytics (0=False, 1=True)
FIREBASE_ENABLED=0
# Path to firebase credentials if enabled
# FIREBASE_CREDENTIALS_PATH=backend/services/firebase_credentials.json
```

---

## 5. Application Launch

To run the full application, you will need two terminal windows.

### Terminal 1: Backend Server
Start the Django development server. This handles the API and serves the application.

```bash
# Ensure your virtual environment is activated
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

python manage.py runserver
```
*   The server will start at `http://127.0.0.1:8000/`.

### Terminal 2: Frontend Watcher
Start the Webpack watcher to compile React/JS assets in real-time.

```bash
npm start
```
*   This command runs `webpack serve` or the configured start script to watch for changes in `src/` and update the build.

---

## 6. Accessing the Application

1.  Open your web browser.
2.  Navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.
3.  You should see the FAIX Faculty landing page.
4.  Click the **Chatbot Icon** (bottom right) to open the assistant.

