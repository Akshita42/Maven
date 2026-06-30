# Architecture Overview

This document describes the overall architecture of Maven, the responsibilities of each major module, and how information flows through the system from a user's request to the final investment report.

The project follows a modular architecture where each layer has a clearly defined responsibility. This separation keeps the system easier to understand, maintain, and extend without tightly coupling different parts of the application.

---

# High-Level Architecture

```
                        User
                          │
                          ▼
                 Next.js Frontend
                          │
              Server-Sent Events (SSE)
                          │
                          ▼
                  FastAPI Backend
                          │
                Intent Planning Layer
                          │
                          ▼
                Company Resolution
                          │
                          ▼
               Evidence Collection
                          │
                          ▼
             Financial Analysis Layer
                          │
                          ▼
                 Review & Evaluation
                          │
                          ▼
             Recommendation Generation
                          │
                          ▼
                 Report Generation
                          │
                          ▼
                 Persisted Investment Report
                          │
                          ▼
               Conversational Explanation
```

---

# System Components

## 1. Frontend

The frontend is built using Next.js and provides the conversational interface through which users interact with Maven.

Its responsibilities include:

- Accepting research requests
- Displaying streaming progress updates
- Rendering investment reports
- Handling conversational follow-up questions
- Managing the active research session

The frontend communicates with the backend using Server-Sent Events (SSE), allowing long-running research tasks to stream progress instead of blocking the user interface.

---

## 2. Planner

The Planner acts as the entry point for every user request.

Its primary responsibility is understanding what the user wants to do.

For example, it determines whether the user is:

- requesting a new company analysis,
- asking a follow-up question,
- requesting a comparison,
- or continuing an existing conversation.

This prevents unnecessary execution of the complete research pipeline when only an explanation is required.

---

## 3. Company Resolution

Users often enter company names in different ways.

Examples include:

- Apple
- AAPL
- Microsoft
- Tata Consultancy Services
- TCS

The Company Resolution module converts these inputs into a valid publicly traded company before research begins.

If multiple companies match the request, Maven asks the user for clarification instead of analyzing the wrong company.

---

## 4. Evidence Collection

Once the company has been identified, Maven gathers the financial information required for analysis.

The Evidence Collection layer retrieves information such as:

- Company profile
- Market data
- Historical financial statements
- Financial metrics

This information is combined into a structured evidence package that becomes the foundation for the rest of the pipeline.

---

## 5. Financial Analysis

The Financial Analysis layer transforms raw financial data into meaningful observations.

Rather than relying on an LLM for numerical calculations, Maven evaluates financial metrics programmatically to ensure consistency and reproducibility.

The analysis is organized into several perspectives including:

- Business Quality
- Financial Health
- Growth
- Valuation
- Risk
- Management

Each perspective contributes findings that are later considered when generating the final recommendation.

---

## 6. Review Pipeline

The review pipeline consolidates the analytical findings into a structured investment assessment.

Instead of directly generating a recommendation from raw financial data, Maven first organizes the available evidence into a review stage.

Separating review from analysis keeps the architecture modular and makes it easier to improve or replace individual components in the future without affecting the rest of the system.

---

## 7. Recommendation Generation

The Recommendation layer combines the outputs of the financial analysis and review stages to produce a final investment recommendation.

Along with the recommendation itself, the system also generates supporting information such as:

- Confidence
- Investment outlook
- Key strengths
- Primary concerns

These become part of the final report presented to the user.

---

## 8. Report Generation

All outputs from previous stages are consolidated into a single Investment Report.

The report acts as the single source of truth for the application and is used by both:

- the report viewer
- conversational follow-up questions

Persisting reports also allows users to revisit previous analyses without repeating the complete research workflow.

---

## 9. Conversational Layer

After a report has been generated, users can continue interacting with Maven naturally.

Instead of performing another financial analysis, Maven retrieves the existing report and uses it as context to answer follow-up questions such as:

- Why was this recommendation made?
- What are the biggest risks?
- Explain this in simpler terms.
- Challenge this recommendation.

This approach keeps responses fast while maintaining consistency with the original analysis.

---

# Data Flow

The overall request lifecycle follows these steps:

1. The user submits a research request.
2. The Planner determines the user's intent.
3. The company is identified and resolved.
4. Financial evidence is collected.
5. The evidence is analyzed from multiple financial perspectives.
6. The analytical findings are reviewed.
7. A recommendation is generated.
8. A structured investment report is created and stored.
9. The user can continue asking conversational follow-up questions using the generated report as context.

---

# Why This Architecture?

One of the main goals of Maven was to separate responsibilities across independent modules instead of building one large service that performs every task.

This provides several benefits:

- Easier maintenance
- Better separation of concerns
- Simpler testing of individual components
- Reusable report generation
- Support for conversational follow-up without repeating analysis

The modular design also makes future improvements significantly easier. New evidence providers, financial analyzers, or AI-powered review modules can be introduced without requiring major changes to the rest of the application.

---

# Design Principles

Throughout development, I tried to follow a few core principles:

- Keep financial calculations deterministic.
- Use AI where language understanding provides the most value.
- Make recommendations explainable rather than opaque.
- Separate data collection, analysis, and presentation.
- Build each module so it can evolve independently.

While Maven is still evolving, this architecture provides a solid foundation for expanding the system into a more capable AI investment research platform.