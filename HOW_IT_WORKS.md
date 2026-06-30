# How It Works

This document explains the complete, end-to-end flow of Maven when a user submits a research request. It outlines how the conversational inputs map to the backend logic, detailing both where AI is used and where deterministic code is used.

## 1. Intent Classification (Planner Agent)
When a user types a message (e.g., "Analyze Microsoft" or "Should I invest in it?"), the request first goes to the **Planner Agent**.
- **What it does:** The Planner uses a Large Language Model (Google Gemini) to analyze the chat history, active report context, and the user's raw message.
- **Output:** It classifies the request into an intent like `ANALYSIS` (for a new company), `EXPLANATION` (for a follow-up question), or `COMPARE`. It also extracts the target company name or ticker if a new search is required.

## 2. Entity Resolution & Clarification
If the intent is `ANALYSIS`, the system takes the extracted company name and hits the Yahoo Finance Search API.
- If an exact match is found with high confidence, the pipeline continues.
- If the search is ambiguous (e.g., searching for "TCS" returns multiple global companies), the pipeline pauses and returns a graceful message to the user asking them to pick the right one.
- If the company is private or unlisted, it gracefully informs the user that it cannot be analyzed.

## 3. Evidence Collection
Once a valid ticker symbol (e.g., `MSFT`) is locked in, the **Evidence Collector** kicks off.
- **What it does:** It makes HTTP requests to various public endpoints (mainly Yahoo Finance) to download raw JSON and HTML data.
- **Output:** It gathers Market Data, Company Profile strings, and large blocks of historical Financial Statements, packaging them into an `EvidencePackage`.

## 4. Financial Analysis (Intelligence Service)
This is where the raw numbers are turned into human-readable insights.
- **What it does:** The system runs the evidence through six **deterministic analyzers** (Business Quality, Financial Health, Growth, Valuation, Risk, Management).
- **How it works (Truthful Implementation):** No LLMs are used here. Instead, it uses hardcoded mathematical rules. For example, if `operating_margin > 20%`, it pushes the string *"Strong operating margin"* to a list. 
- **Output:** An `InvestmentIntelligence` object containing arrays of static text findings.

## 5. Thesis & Committee Evaluation
The system simulates a multi-agent debate to decide whether to support or reject the stock.
- **What it does:** The intelligence strings are repackaged into an `InvestmentThesis`. Then, various "Reviewers" in the `CommitteeOrchestrator` evaluate the thesis.
- **How it works (Truthful Implementation):** Again, no LLMs are used here. The reviewers execute simple Python string-matching. For instance, the Business Reviewer scans the text for the phrase `"small enterprise"`. If it finds it, it votes to `REJECT/QUESTION` the stock. If it finds `"high-moat"`, it votes to `SUPPORT`.
- **Output:** A `CommitteeReview` object containing the votes.

## 6. Recommendation Generation
The final `BUY/HOLD/SELL` stance is computed.
- **What it does:** The `RecommendationBuilder` takes the votes from the committee and applies a static matrix.
- **How it works:** If the committee voted `SUPPORT` and confidence scores are mathematically > 80%, it outputs a `BUY`. If it voted `REJECT`, it outputs `SELL`. Otherwise, `HOLD`.

## 7. Report Generation
The `ReportBuilder` gathers the Evidence, Thesis, Committee Review, and Recommendation objects and compiles them into a massive, heavily structured JSON document. This document is saved and a `reportId` is passed back to the frontend.
The frontend uses this JSON to render the rich, visual dashboard the user sees.

## 8. Conversational Follow-Up (Explanation Agent)
Once the report is generated, the user can ask questions like *"Why did you recommend this?"* or *"What are the risks?"*
- **What it does:** The Planner routes this to the **Explanation Agent**.
- **How it works:** This agent uses Google Gemini. It takes the user's question, attaches the entire generated JSON report as context (RAG - Retrieval-Augmented Generation), and asks the LLM to generate a helpful, conversational answer based *only* on the data in the report.
- **Output:** A natural language chat bubble responding directly to the user's inquiry.
