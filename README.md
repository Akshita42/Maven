# Maven – AI Investment Research Copilot
*Submission for Altuni AI Labs – AI Product Development Engineer Assignment*

---

# Overview — What it does

Maven is an AI-powered investment research copilot designed to help users evaluate publicly listed companies through an explainable, evidence-first workflow.

Instead of functioning as a traditional chatbot, Maven follows a structured investment research pipeline inspired by professional equity research practices. It collects real-time financial data, performs deterministic financial analysis, synthesizes the findings into an investment thesis, reviews that thesis through an AI investment committee, critiques its own reasoning, and finally generates both a conversational recommendation and a detailed research report.

The final recommendation is presented as **INVEST** or **PASS**, supported by transparent reasoning and traceable financial evidence.

---

# Key Engineering Decisions & Trade-offs

## 1. Hybrid AI Architecture

The assignment requested React/Next.js, Node.js, and LangChain.js.

For this MVP, I implemented the application using a layered architecture consisting of:

- Next.js frontend
- Node.js API gateway (built directly into Next.js API Routes)
- Python FastAPI AI service

The AI orchestration currently resides inside the Python service because Python provides a mature ecosystem for financial data processing and AI workflows.

The architecture intentionally separates the orchestration layer from the frontend, making it straightforward to migrate the workflow to LangChain/LangGraph in a future version without changing the overall system design.

---

## 2. Deterministic Analysis Before AI Reasoning

Financial calculations should be reproducible.

Instead of asking an LLM to calculate financial metrics, Maven computes all financial ratios and derived metrics deterministically from structured financial data.

The language model receives only validated outputs and focuses exclusively on:

- interpretation
- reasoning
- synthesis
- explanation

This significantly reduces hallucinations while improving consistency.

---

## 3. Explainability Through Evidence

Trust is essential for AI-assisted financial decision making.

Every recommendation is backed by supporting financial evidence.

The report includes an Evidence section that allows users to trace important financial metrics back to their originating data source, making the recommendation transparent rather than a black-box AI opinion.

---

# How it Works — Architecture

Maven uses a modular microservice architecture.

```text
Next.js Frontend
        │
        ▼
Node.js API Gateway (Next.js API Routes)
        │
        ▼
Python AI Service
        │
        ▼
Evidence Collection
        │
        ▼
Financial Intelligence
        │
        ▼
Investment Thesis
        │
        ▼
AI Investment Committee
        │
        ▼
AI Self-Critique
        │
        ▼
Recommendation Builder
        │
        ▼
Professional Research Report
```

The major stages are:

### 1. Company Resolution

Maps the company name supplied by the user to the corresponding market ticker.

### 2. Evidence Collection

Retrieves structured financial and market data from public financial data providers.

### 3. Financial Intelligence

Deterministic analyzers evaluate the company across multiple dimensions, including:

- Business Quality
- Financial Health
- Growth
- Valuation
- Risk
- Management

### 4. Investment Thesis

The AI synthesizes the deterministic findings into an evidence-based investment thesis.

### 5. AI Investment Committee

An AI committee evaluates the thesis, weighs supporting and opposing evidence, and produces a committee decision.

### 6. AI Self-Critique

The recommendation is challenged before publication by identifying assumptions, missing evidence, and reasoning weaknesses.

### 7. Recommendation Builder

Combines deterministic confidence with AI reasoning to generate the final **INVEST** or **PASS** recommendation.

### 8. Report Generation

Transforms the recommendation into a professional research report with evidence traceability and supporting analysis.

---

# How to Run

## Prerequisites

- Node.js 18+
- Python 3.10+
- Google Gemini API Key

---

## 1. Clone Repository

```bash
git clone <repository-url>
cd Maven
```

---

## 2. Start the AI Service

```bash
cd ai-service

python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file in the `ai-service` directory:
```env
ENV=development
HOST=127.0.0.1
PORT=8000
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Run

```bash
python -m uvicorn src.main:app
```

---

## 3. Start the Frontend & API Gateway

```bash
cd frontend

npm install

npm run dev
```

---

## Future Improvements

This MVP focuses on building an explainable investment research pipeline.

Future work includes:

- LangChain/LangGraph orchestration
- Retrieval-Augmented Generation (RAG)
- Vector databases for semantic retrieval
- SEC filing and annual report retrieval
- Earnings call transcript analysis
- Multi-agent specialist reviewers
- Historical report memory
- Portfolio analysis
- Company comparison
- Continuous investment monitoring
- PDF export
- Research collaboration
- Multi-LLM support
- Real-time market alerts

The current architecture was intentionally designed so these capabilities can be incorporated with minimal changes to the overall system. 

## Note

This project was developed as a time-constrained MVP to demonstrate an explainable AI investment research workflow.

The focus was on building a transparent, modular, and extensible architecture rather than maximizing feature count. Several advanced capabilities—including LangChain/LangGraph orchestration, Retrieval-Augmented Generation (RAG), semantic search, and portfolio intelligence—have been intentionally identified as future enhancements.