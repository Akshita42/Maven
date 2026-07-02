# Maven - AI Investment Research Copilot
*(Submission for Altuni AI Labs - AI Product Development Engineer)*

## Overview — What it does
Maven is an institutional-grade, AI-powered equity research platform. Instead of a standard chatbot that spits out walls of text, Maven acts as a professional financial analyst. It takes a company name, autonomously scrapes real-time financial evidence, and runs the data through a multi-agent **"AI Committee."** 

This committee evaluates the company across multiple pillars (Growth, Valuation, Risk, Health), debates the thesis, and delivers a highly structured, visually stunning investment report with a final `INVEST` or `PASS` recommendation.

## Key decisions & trade-offs (Please Read)

### 1. The Microservice Architecture (Python AI vs LangChain.js)
The assignment requested: `React/Next.js (front end) · Node.js/Next.js (back end) · LangChain.js`. 

**The Trade-off:** While I am fully proficient in JS/TS and utilized **Next.js API Routes** as the primary backend API Gateway, I made the deliberate architectural decision to build the core AI orchestration as a dedicated **Python Microservice** (FastAPI) instead of using LangChain.js natively. 

**Why?** To build an enterprise-grade AI product in 7 days, I wanted to go beyond a simple single-prompt wrapper. Maven utilizes a complex, multi-agent "AI Committee" that strictly separates deterministic data gathering from LLM reasoning to eliminate financial hallucinations. Python remains the most robust, mature ecosystem for this level of AI orchestration. I prioritized building an exceptional, resilient product architecture. **I am fully prepared to rebuild this pipeline in LangChain.js for production.**

### 2. Deterministic Math vs LLM Math
LLMs are terrible at math. Instead of asking the AI to calculate P/E ratios or Revenue Growth, Maven uses a deterministic Python script to calculate all financial metrics from raw Yahoo Finance data. The LLM is only given the *final, verified numbers* to reason about.

### 3. The Evidence Audit Tracker (Combating Black Boxes)
Trust is the biggest hurdle for AI in FinTech. To combat the "black box" effect, I built an **Evidence Audit** data room into the bottom of every report. It displays the exact metric, value, and source that the AI was fed, ensuring complete transparency for the user.

## How it works — Approach and Architecture

Maven relies on a microservice architecture communicating via Server-Sent Events (SSE) for real-time streaming:

1. **Frontend (Next.js / React):** A premium, dark-themed dashboard built with Tailwind and Framer Motion. 
2. **API Gateway (Next.js API Routes / Node.js):** Acts as the backend router, proxying requests securely to the AI worker.
3. **AI Worker (Python / FastAPI / LangChain):** 
   - **Company Resolution:** Maps user input (e.g., "Apple") to ticker (AAPL).
   - **Evidence Collection:** Scrapes Yahoo Finance.
   - **AI Committee Review:** Multiple LLM personas review the data independently and vote.
   - **Recommendation Generation:** Synthesizes the votes into a final `BUY/SELL/HOLD` report.

## How to run it

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- Google Gemini API Key

### 1. Start the AI Microservice (Backend)
```bash
cd ai-service
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```
Create a `.env` file in `ai-service`:
```env
ENV=development
HOST=127.0.0.1
PORT=8000
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
Start the worker:
```bash
python -m uvicorn src.main:app
```

### 2. Start the Frontend & API Gateway
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000` to use Maven.

## Example Runs
You can test the agent on any publicly traded company. Some great examples to try:
- **NVIDIA (NVDA):** Watch the AI handle hyper-growth and high valuation.
- **Intel (INTC):** Watch the AI committee critique declining margins and issue a PASS/SELL.
- **Apple (AAPL):** See how the agent evaluates a mature, cash-rich business.

## What I would improve with more time
1. **Rewrite Orchestration in LangChain.js:** Fully consolidate the Python microservice into the Next.js Node backend to unify the codebase.
2. **RAG for SEC Filings:** Integrate a vector database (like Pinecone) to allow the AI to read and cite the latest 10-K and 10-Q filings.
3. **Auth & Portfolios:** Add user authentication so users can save reports and track the performance of Maven's recommendations over time.

---
*Bonus points included: I have zipped my raw AI development logs (transcript.jsonl) in the submission folder so you can see exactly how I collaborated with my AI coding assistant to architect this product!*