# Approach & Design Decisions

Building Maven was not just about creating an AI chatbot that gives investment recommendations. My goal was to understand how traditional software engineering and modern AI could work together to build an investment research assistant that is reliable, explainable, and easy to interact with.

Throughout the project, I had to make several engineering decisions where there wasn't a single "correct" answer. In many cases, I chose reliability and transparency over complexity, while keeping the architecture modular enough to improve in the future.

---

# Design Philosophy

One of the biggest decisions I made was separating financial computation from language generation.

Large Language Models are very good at understanding natural language and explaining complex concepts, but they are not always reliable when performing numerical calculations. Small calculation mistakes can significantly change an investment recommendation.

To avoid this, Maven follows a hybrid approach.

- Financial metrics are calculated programmatically using deterministic logic.
- AI is responsible for understanding user intent, answering follow-up questions, and explaining the generated analysis in natural language.

This separation ensures that the numerical foundation of every report remains consistent while still providing a conversational user experience.

---

# Major Design Decisions

## 1. Hybrid AI Architecture

Instead of allowing the language model to generate an investment recommendation directly, I separated the application into two responsibilities.

The deterministic pipeline handles financial calculations, evidence processing, and recommendation generation.

The LLM is used only where natural language understanding provides value, such as:

- Understanding what the user is asking.
- Handling conversational follow-up questions.
- Explaining the generated report in different levels of detail.

This makes the system more predictable and reduces the chances of AI hallucinating financial information.

---

## 2. Modular Pipeline

Rather than writing one large function that performs the complete analysis, I divided the backend into multiple modules responsible for specific tasks.

These include:

- Company Resolution
- Evidence Collection
- Financial Analysis
- Review
- Recommendation
- Report Generation
- Explanation

Although some of these modules currently use deterministic logic, the modular design makes it easier to improve or replace individual components without affecting the entire application.

---

## 3. Streaming User Experience

Investment analysis takes several seconds because multiple external requests are performed.

Instead of making the user wait on a blank screen, I chose Server-Sent Events (SSE) to stream progress updates throughout the workflow.

This allows the frontend to continuously update the user with the current stage of execution, making the application feel much more responsive.

---

## 4. Report Persistence

Initially, I stored the generated reports directly in frontend state. This quickly became difficult to manage because large report objects consumed unnecessary browser memory.

I later changed the design so that reports are persisted separately and the frontend only keeps track of the active report identifier. This made follow-up conversations simpler and reduced unnecessary state duplication.

---

# Engineering Trade-offs

Every project involves compromises, especially within a limited development timeline.

## Deterministic Analysis vs AI Analysis

One of the biggest trade-offs was choosing deterministic financial analysis instead of allowing the LLM to perform the complete investment reasoning.

Advantages:

- Consistent calculations
- Reproducible recommendations
- Lower API usage
- Faster execution

Limitations:

- Less flexible reasoning
- Harder to capture qualitative business insights

Given the project timeline, I believed this was the more reliable engineering decision.

---

## Yahoo Finance as the Data Source

I chose Yahoo Finance because it provides a wide range of publicly available financial information without requiring a paid subscription.

Advantages:

- Free to use
- Good company coverage
- Sufficient for a prototype

Limitations:

- Unofficial endpoints
- Occasional missing fields
- Rate limiting

In a production system I would replace this with a structured financial data provider.

---

## File-Based Report Storage

For persistence I chose simple file-based storage rather than introducing a database.

Advantages:

- Easy to implement
- Minimal setup
- Suitable for a prototype

Limitations:

- Not suitable for multiple users
- Limited scalability

If this project were extended further, I would migrate to PostgreSQL or another relational database.

---

# Challenges Faced

## Working with Financial Data

One of the most time-consuming parts of the project was handling inconsistent financial data.

Different companies expose different financial fields, and many values are missing depending on the exchange or reporting format. Building reliable fallback logic required much more work than expected.

---

## Maintaining Conversation Context

Another challenge was preserving conversation context across the chat interface while keeping browser memory usage reasonable.

Initially I stored large report objects inside the frontend session, which eventually exceeded browser storage limits.

I redesigned the workflow so that only the active report identifier is stored while the report itself is loaded whenever it is needed.

---

## Balancing AI with Deterministic Logic

Throughout development I constantly evaluated where AI genuinely added value.

I found that using LLMs for financial calculations reduced reliability, while using them for conversation and explanation significantly improved the overall user experience.

Finding this balance became one of the biggest design decisions of the project.

---

# Lessons Learned

Building Maven taught me several important lessons beyond simply integrating an LLM into an application.

- AI works best when combined with traditional software engineering rather than replacing it.
- Reliable data pipelines are just as important as prompt engineering.
- Good user experience often matters more than adding additional AI features.
- Transparency helps users trust AI-generated recommendations.
- Building production-style applications requires much more effort in error handling and state management than initially expected.

Perhaps the biggest lesson was that building an AI product is not just about using an LLM. Most of the work involves designing reliable systems around the model.

---

# Future Direction

If I continue developing Maven, my next focus would be improving the quality of investment reasoning rather than adding more features.

Some of the improvements I would like to make include:

- LLM-powered investment reviewers for deeper reasoning
- Better valuation models such as DCF analysis
- SEC filing analysis
- News sentiment integration
- Analyst consensus data
- Portfolio analysis
- Persistent user accounts
- Watchlists
- Better comparison workflows between companies
- LangGraph-based orchestration for more advanced AI workflows

The current architecture was intentionally designed so these improvements can be added incrementally without requiring a complete redesign of the application.