# 🚀 Maven – Autonomous Multi-Agent Financial Research Copilot
*Submission for Razorpay AI Buildathon — Real-Time Agentic Financial Intelligence with SEC Hybrid RAG & Live Evals*

---

## 🌟 Overview — What Maven Is

**Maven** is an autonomous, multi-agent investment research copilot designed to evaluate publicly traded companies through a stateful, explainable, zero-hallucination workflow.

Unlike generic LLM wrappers that guess financial numbers, Maven pairs a **deterministic mathematical scoring engine** with a **LangGraph state machine graph**, an **adversarial Bull vs. Bear debate committee**, **ChromaDB vector RAG over SEC 10-K/10-Q filings**, and **real-time AI observability evals**.

Every recommendation is delivered as **INVEST** or **PASS**, complete with confidence scores, target price bands, risk factors, and complete trace evidence.

---

## 🏗️ Architecture & Core System Design

Maven uses a modular microservices architecture separating the high-performance Next.js 14 App Router frontend from the stateful Python FastAPI AI service.

```text
       ┌────────────────────────────────────────────────────────┐
       │                   Next.js 14 Frontend                  │
       │     (Dark Glassmorphism, SSE Streaming, Evals UI)      │
       └───────────────────────────┬────────────────────────────┘
                                   │ Real-time SSE / REST
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                 FastAPI AI Engine Backend              │
       └───────────────────────────┬────────────────────────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
┌─────────────────────────┐ ┌───────────────────┐ ┌──────────────────────┐
│  LangGraph Orchestrator │ │ Deterministic Math│ │ SEC 10-K Chroma Vector│
│  State Machine Graph    │ │ Engine (0 Halluc.)│ │ Hybrid RAG Pipeline  │
└────────────┬────────────┘ └─────────┬─────────┘ └──────────┬───────────┘
             │                        │                      │
             └───────────────────┬────┴──────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Bull vs. Bear Committee │
                    │   Adversarial Debate    │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ AI Observability & Evals│
                    │ (Faithfulness, Precision│
                    └─────────────────────────┘
```

---

## ⚡ Core Features & Capabilities

### 1. 🔄 Stateful LangGraph Multi-Agent Orchestration
Powered by `langgraph`, Maven runs a multi-agent graph state machine featuring specialized nodes:
- **Fundamental & Valuation Specialist**
- **Growth & Capital Allocation Analyst**
- **Financial Health & Solvency Inspector**
- **Technical & Price Momentum Analyst**
- **SEC Filing Risk Factor Specialist**

### 2. 📚 Hybrid SEC 10-K / 10-Q Vector RAG Engine
Integrates `ChromaDB` and SEC Edgar data pipelines to extract, chunk, and embed official 10-K and 10-Q risk disclosures and MD&A sections. Eliminates black-box hallucination by anchoring qualitative claims in official regulatory filings.

### 3. ⚔️ Bull vs. Bear Adversarial Debate Engine
Before finalizing any rating, an adversarial committee node spawns opposing Bull and Bear agents:
- **Bull Agent**: Formulates upside catalysts, revenue expansion paths, and valuation margin-of-safety.
- **Bear Agent**: Cross-examines debt obligations, margin contraction, competitive pressures, and regulatory red flags.
- **Moderator Node**: Synthesizes cross-examinations into a battle-tested investment verdict.

### 4. 📐 Zero-Hallucination Mathematical Determinism
Financial metrics (P/E, EV/EBITDA, Debt-to-Equity, FCF Yield, Piotroski F-Score) are calculated programmatically in Python (`math_engine.py`) using raw balance sheet and income statement data before being passed to LLM reasoning nodes.

### 5. 🔍 Live AI Observability & Runtime Evals
Includes an internal tracing engine (`tracer.py`) and evaluation pipeline (`evals.py`) scoring every single research run on:
- **Faithfulness Score**: Measures alignment between context and final claims.
- **Answer Relevance**: Ensures prompt intent is strictly met.
- **Context Precision**: Evaluates quality of retrieved SEC vectors.
*(Accessible directly in the frontend via **Developer Mode**)*

---

## 🛠️ Quick Start & Local Setup

### Prerequisites
- **Node.js**: v18+
- **Python**: v3.10+
- **Gemini API Key**: Set `GEMINI_API_KEY` in `.env`

---

### 1. Clone Repository & Setup Environment

```bash
git clone https://github.com/Akshita42/Maven.git
cd Maven
```

---

### 2. Start Python FastAPI AI Backend

```bash
cd ai-service

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo ENV=development > .env
echo HOST=127.0.0.1 >> .env
echo PORT=8000 >> .env
echo GEMINI_API_KEY=your_gemini_api_key_here >> .env
echo GEMINI_MODEL=gemini-2.5-flash >> .env

# Run FastAPI Server
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

---

### 3. Start Next.js Frontend

Open a new terminal window:

```bash
cd Maven/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit `http://localhost:3000` in your browser.

---

## 🧪 Verification & Testing

To run the automated system test suite for the LangGraph workflow and evaluation engine:

```bash
cd ai-service
.venv\Scripts\python.exe test_langgraph.py
```

---

## 🏆 Submission Details

- **Event**: [Razorpay AI Buildathon](https://razorpay.com/buildathon/)
- **Repository**: [https://github.com/Akshita42/Maven](https://github.com/Akshita42/Maven)
- **Tech Stack**: Next.js 14, Tailwind CSS, TypeScript, FastAPI, Python 3.10, LangGraph, ChromaDB, Google Gemini 2.5 Flash, Uvicorn.