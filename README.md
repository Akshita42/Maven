# Maven - AI Investment Research Copilot

## Project Overview

Maven is an AI-powered investment research copilot that helps users analyze publicly traded companies through a conversational interface. Instead of manually reading financial statements, calculating ratios, and switching between multiple websites, users can simply ask Maven to research a company and receive a structured investment report along with the reasoning behind the recommendation.

The project combines deterministic financial analysis with conversational AI. Financial metrics are calculated programmatically to ensure consistency, while Large Language Models (LLMs) are used to understand user intent and explain the results in natural language.


## Motivation

## Motivation

While learning about investing, I realized that understanding a company's financial health usually involves jumping between multiple sources, reading lengthy reports, and manually interpreting financial metrics. Although LLMs can summarize information well, they are not always reliable when performing numerical calculations.

The goal behind Maven was to combine deterministic financial analysis with AI-assisted explanations. Rather than asking an LLM to calculate financial metrics, Maven computes those values programmatically and uses AI where it provides the most value—understanding user questions and explaining investment reasoning.

## Design Philosophy

One of the main design goals of Maven was to separate factual computation from language generation.

Financial calculations such as profitability, liquidity, leverage, and growth metrics are computed deterministically so that the same financial data always produces the same analytical result. This avoids numerical hallucinations and keeps the analysis reproducible.

LLMs are used for tasks where natural language understanding is important, such as interpreting user intent, answering follow-up questions, and explaining the reasoning behind an investment recommendation.

This hybrid approach balances reliability, transparency, and usability.

## Features

### Research
- Company search and resolution
- Automated evidence collection
- Fundamental financial analysis
- Structured investment report

### AI Assistance
- Conversational interface
- Follow-up questions
- Context-aware explanations
- Natural language interaction

### Engineering
- Streaming responses using SSE
- Report persistence
- Transparent evidence collection
- Modular backend architecture

## Tech Stack

**Frontend:**
- Next.js (React)
- Tailwind CSS (Styling)
- Framer Motion (Animations)
- Lucide React (Icons)

**Backend:**
- Python 3.10+
- FastAPI (REST and Server-Sent Events)
- Uvicorn (ASGI Server)
- Google Gemini API (LLM Integration)
- Yahoo Finance endpoints (via HTTP requests)

## High-Level Architecture

User
    │
    ▼
Conversation Layer
    │
    ▼
Intent Planning
    │
    ▼
Evidence Collection
    │
    ▼
Financial Analysis
    │
    ▼
Review & Recommendation
    │
    ▼
Report Generation
    │
    ▼
Conversational Explanation

## Folder Structure

```
Maven/
├── ai-service/             # Python backend
│   ├── src/
│   │   ├── agent/          # LLM integrations (Planner, Explanation, Research wrappers)
│   │   ├── intelligence/   # Deterministic financial analyzers (Growth, Health, etc.)
│   │   ├── thesis/         # Data repackaging for sections
│   │   ├── committee/      # Review and evaluation modules
│   │   ├── recommendation/ # Recommendation generation
│   │   ├── report/         # # Report creation layer
│   │   └── main.py         # FastAPI entry point
│   ├── requirements.txt
│   └── .env.example
└── frontend/               # Next.js frontend
    ├── src/
    │   ├── app/            # Pages and routing
    │   ├── components/     # UI Components
    │   └── lib/            # API services and utilities
    ├── package.json
    └── tailwind.config.ts
```

## Installation

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- A Google Gemini API Key

### Clone the Repository
```bash
git clone <repository_url>
cd Maven
```

## Running the Backend

1. Navigate to the `ai-service` directory:
   ```bash
   cd ai-service
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables (see below).
5. Run the server:
   ```bash
   python -m uvicorn src.main:app --reload
   ```
   The backend will be available at `http://localhost:8000`.

## Running the Frontend

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`.

## Environment Variables

In the `ai-service` directory, create a `.env` file based on `.env.example`:

```env
ENV=development
HOST=127.0.0.1
PORT=8000
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

## Example Workflow

1. User asks Maven to analyze a company.
2. Maven resolves the company and collects financial evidence.
3. The financial analysis pipeline evaluates the available data.
4. A structured investment report is generated.
5. Users can continue the conversation by asking follow-up questions about the report.

## Example Questions

Analyze Microsoft

Research NVIDIA

Analyze Tata Consultancy Services

What are the biggest risks?

Why is the recommendation bullish?

What could change this recommendation?

Compare Microsoft with Google.

Summarize this report.

## Known Limitations

- The current version focuses primarily on publicly traded companies with reliable financial data.
- Financial data is collected from publicly available Yahoo Finance endpoints, which may occasionally be rate limited or unavailable.
- The conversational assistant currently answers questions using the generated report as context rather than performing fresh research.
- Some advanced investment techniques such as DCF modelling, analyst consensus, SEC filing analysis, and real-time news sentiment are outside the scope of the current implementation.

## Future Scope

Future work includes richer financial data sources, portfolio analysis, watchlists, SEC filing analysis, news sentiment, comparison workflows, and a more advanced AI-driven review pipeline capable of performing deeper investment reasoning while preserving deterministic financial calculations.

Maven represents my attempt to combine traditional software engineering with modern AI to create a practical investment research assistant. Building this project taught me not only how to integrate LLMs into applications, but also when deterministic systems are the better engineering choice.