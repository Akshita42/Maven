# How Maven Works

This document explains the complete flow of Maven from the moment a user submits a query until a research report is generated and follow-up questions can be answered.

The overall workflow is divided into multiple stages so that each component has a clear responsibility. This makes the system easier to maintain, debug, and extend while keeping the user experience conversational.

---

# Step 1: User Request

Everything starts with a user entering a query in the chat interface.

Examples include:

- Analyze Microsoft
- Research NVIDIA
- Analyze Apple
- Why did you recommend this?
- What are the biggest risks?

The frontend sends the request to the backend using Server-Sent Events (SSE), allowing progress updates to be streamed while the research is being performed.

---

# Step 2: Understanding the User's Intent

The first backend component to process the request is the Planner.

Its responsibility is understanding what the user wants to do.

For example, it determines whether the user is:

- requesting a new company analysis,
- asking a follow-up question,
- continuing an existing conversation,
- or requesting a comparison.

This prevents Maven from unnecessarily repeating the complete research workflow when an existing report can simply be reused.

---

# Step 3: Company Resolution

If a new analysis is required, Maven identifies the correct publicly traded company.

Users may enter:

- Company names
- Stock tickers
- Abbreviations
- Common names

The Company Resolution module converts these into the correct publicly traded company.

If multiple companies match the request, Maven asks the user for clarification before continuing.

If the requested company is private or unavailable, Maven explains the situation naturally instead of exposing technical errors.

---

# Step 4: Evidence Collection

Once the target company has been identified, Maven gathers the financial information required for analysis.

The Evidence Collection stage retrieves information such as:

- Company profile
- Market data
- Historical financial statements
- Financial metrics
- Basic company information

The collected information is organized into a structured evidence package that becomes the foundation for the remaining analysis.

---

# Step 5: Financial Analysis

The collected evidence is then evaluated from multiple financial perspectives.

The analysis includes areas such as:

- Business Quality
- Financial Health
- Growth
- Valuation
- Risk
- Management

Instead of relying on an LLM for numerical calculations, Maven evaluates financial metrics programmatically to ensure consistent and reproducible results.

Each analysis produces structured findings that contribute to the overall investment assessment.

---

# Step 6: Review and Recommendation

After the financial analysis is complete, Maven consolidates the findings into a structured review.

This stage evaluates the available evidence and generates:

- Overall investment outlook
- Recommendation
- Confidence
- Key strengths
- Primary concerns

Separating this stage from financial analysis keeps the architecture modular and allows future improvements without redesigning the complete system.

---

# Step 7: Report Generation

Once the recommendation has been generated, Maven creates a structured investment report.

The report combines:

- Company overview
- Financial analysis
- Investment findings
- Recommendation
- Supporting evidence

The report is then stored and assigned a unique report identifier.

Rather than repeating the complete research process, future conversations can simply reuse this report.

---

# Step 8: Conversational Follow-up

One of the goals of Maven is to behave like an AI research copilot rather than a one-time report generator.

After a report has been generated, users can continue asking questions naturally.

For example:

- Why was this recommendation made?
- Explain this in simple terms.
- What are the biggest risks?
- Challenge this recommendation.
- Compare it with Microsoft.

Instead of performing another financial analysis, Maven retrieves the existing report and uses it as context to generate a conversational explanation.

This keeps responses faster while ensuring they remain consistent with the original research.

---

# Error Handling

Real-world financial data is not always available.

Whenever possible, Maven avoids exposing technical errors directly to users.

Instead, it attempts to explain problems in a conversational way.

Examples include:

- Company not found
- Ambiguous company names
- Private companies
- Rate limits
- Temporary service failures

The goal is to provide helpful guidance rather than displaying internal implementation details.

---

# Complete Workflow

The complete research lifecycle can be summarized as:

```
User Request
      │
      ▼
Intent Planning
      │
      ▼
Company Resolution
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
Conversation & Follow-up
```

---

# Summary

Maven combines deterministic financial analysis with conversational AI to create an investment research experience that is both reliable and easy to use.

Financial calculations are handled programmatically to maintain consistency, while AI is used to understand user requests, explain recommendations, and support natural follow-up conversations.

This separation allows Maven to provide transparent investment research while maintaining a conversational user experience.