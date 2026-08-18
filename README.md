# ProjectForge AI — Multi-Agent Project Architecture & Planning Platform

ProjectForge AI takes a user's raw project idea (e.g. *"Build an e-commerce website for 3 people within 30 days"*) and transforms it into a complete, personalized project blueprint using 6 specialized AI agents orchestrated by LangGraph, with a mandatory human-in-the-loop technology selection checkpoint.

---

## 🌟 Key Architecture & Stack

- **Frontend**: **React 18 + Vite** SPA with React Router v6, Axios, Lucide Icons, Mermaid.js diagram rendering, and Server-Sent Events (SSE) progress listener.
- **Backend**: **FastAPI** REST API + SSE progress stream, LangGraph agent orchestration.
- **Database**: **PostgreSQL 16** installed directly on Windows via SQLAlchemy ORM.
- **Agents**: Exactly 6 specialized AI agents (Requirement Analyst, Technology Advisor, Architecture Agent, Task Planner, Timeline & Resource Agent, Critic & Risk Agent).
- **Human-in-the-Loop Technology Lock**: Technology alternatives presented as interactive cards. The **user explicitly selects and locks** choices before architecture generation begins. Agents never override locked choices.
- **NO-RAG Architecture**: Zero vector DBs, zero embeddings, zero document ingestion. Uses Tavily for web search and structured LLM reasoning.
- **Multi-LLM Provider Abstraction**: Configurable support for **Google Gemini**, **Groq**, and **OpenRouter**.

---

## 🏗️ Architecture Diagram

```
React + Vite Frontend (:3000) ──[Axios / SSE]──> FastAPI Backend (:8000) ──> Local Windows PostgreSQL (:5432)
                                                        │
                                               LangGraph Engine
                                                        │
                     ┌──────────────────────────────────┴──────────────────────────────────┐
                     │ Phase 1: Requirements → Tech Analysis → WAIT (human lock selection)   │
                     │ Phase 2: Architecture → Tasks → Timeline → Critic → Blueprint       │
                     └─────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Local Windows PostgreSQL Setup

Before running the application, PostgreSQL must be installed directly on Windows.

### 1. Install PostgreSQL on Windows
Download and run the official installer from [PostgreSQL Official Windows Downloads](https://www.postgresql.org/download/windows/). During installation, set a password for the `postgres` superuser (e.g. `your_password`).

### 2. Create the Database

#### Method 1: Using pgAdmin (GUI)
1. Open **pgAdmin 4** from your Start menu.
2. Connect to your local server (enter your `postgres` password).
3. Right-click on **Databases** → **Create** → **Database...**
4. Enter `projectforge` as the Database name and click **Save**.

#### Method 2: Using PostgreSQL Command Line (`psql` or `createdb`)
Open PowerShell or Command Prompt:
```cmd
createdb -U postgres projectforge
```
Or via `psql`:
```cmd
psql -U postgres -c "CREATE DATABASE projectforge;"
```

---

## 🚀 Environment Configuration & Running

### 1. Set Up Environment Variables
Copy `.env.example` to `.env` in the root directory:
```bash
cp .env.example .env
```
Open `.env` and set your PostgreSQL password and at least one LLM API key:

```env
# LLM PROVIDERS
GEMINI_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=

# WEB SEARCH
TAVILY_API_KEY=

# DATABASE (Update YOUR_PASSWORD with your local PostgreSQL password)
DATABASE_URL=

# APPLICATION
SECRET_KEY=change-me-to-a-random-secret
DEBUG=True
BACKEND_URL=http://localhost:8000
VITE_BACKEND_URL=http://localhost:8000

# AGENT MODELS
REQUIREMENT_AGENT_MODEL=
TECHNOLOGY_AGENT_MODEL=
ARCHITECTURE_AGENT_MODEL=
TASK_PLANNER_AGENT_MODEL=
TIMELINE_AGENT_MODEL=
CRITIC_AGENT_MODEL=
```

### 2. Start FastAPI Backend (Terminal 1)
```cmd
python -m uvicorn backend.app.main:app --reload --port 8000
```

### 3. Start React / Vite Frontend (Terminal 2)
```cmd
cd frontend
npm run dev
```
Open your browser to: **`http://localhost:3000`**

---

## 🧪 Verification & Tests

### Run Backend Unit Tests
```cmd
python -m pytest backend/tests/ -v
```

### Build React Production Bundle
```cmd
cd frontend
npm run build
```

---

## ⚡ Demo Data (Test Without API Keys)

To test the complete workflow without LLM keys:
```cmd
python scripts/demo_data.py
```
Then log in on the React frontend (`http://localhost:3000/login`) with:
- **Username**: `demo`
- **Password**: `demo123`

# 1. Backend

# Terminal 1:

cd "D:\ITR\ITR ASSIGNMENTS COPY BRANCH\ProjectForge AI"
.\backend\venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload --port 8000


# 2. Frontend

# Terminal 2:

cd "D:\ITR\ITR ASSIGNMENTS COPY BRANCH\ProjectForge AI\frontend"
npm install
npm run dev

# Website Link
https://project-forge-ai-ten.vercel.app?utm_source=chatgpt.com

#For Login

USERNAME- Aditya
PASSWORD- 123456
