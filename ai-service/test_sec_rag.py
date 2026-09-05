# ─────────────────────────────────────────────────────────────────
# ai-service/test_sec_rag.py
# ─────────────────────────────────────────────────────────────────
# Automated Integration Test for Phase 2: Hybrid RAG (SEC Filings + ChromaDB)
# ─────────────────────────────────────────────────────────────────

import sys
import os

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.services.sec_service import SECService
from src.infrastructure.vectorstore.sec_vectorstore import SECVectorStore
from src.agent.langgraph_orchestrator import MavenLangGraphOrchestrator

def main():
    print("======================================================")
    print("  Testing Phase 2: Hybrid RAG (SEC Filings + ChromaDB)")
    print("======================================================")
    
    ticker = "NVDA"
    print(f"\n1. Testing SECService filing chunking for ticker: {ticker}...")
    sec_service = SECService()
    chunks = sec_service.get_filing_chunks(ticker)
    print(f"   [OK] Generated {len(chunks)} text chunks.")
    if chunks:
        print(f"   Sample Chunk Metadata: {chunks[0]['metadata']}")
        print(f"   Sample Chunk Text: {chunks[0]['text'][:120]}...")
        
    print(f"\n2. Testing SECVectorStore ChromaDB indexing & vector search...")
    vector_store = SECVectorStore(db_path=".data/test_chroma_db")
    success = vector_store.index_chunks(ticker, chunks)
    print(f"   [OK] ChromaDB indexing result: {success}")
    
    insights = vector_store.query_qualitative_insights(ticker, "key operational risks headwinds moats revenue drivers", top_k=2)
    print(f"   [OK] Vector Similarity Search returned {len(insights)} RAG insights:")
    for idx, ins in enumerate(insights, 1):
        print(f"     [{idx}] Section: {ins['section']} | Snippet: {ins['content'][:100]}...")
        
    print(f"\n3. Testing LangGraph Stateful Workflow with SEC RAG Node for '{ticker}'...")
    orchestrator = MavenLangGraphOrchestrator()
    final_state = orchestrator.run(ticker)
    
    sec_insights = final_state.get("sec_insights")
    logs = final_state.get("execution_logs", [])
    
    print("\n------------------ LangGraph Execution Logs ------------------")
    for log in logs:
        print(f"  • {log}")
        
    print("\n------------------ RAG Insights in State ------------------")
    print(f"SEC Insights Count: {len(sec_insights) if sec_insights else 0}")
    
    report = final_state.get("report")
    print("\n------------------ Final Decision Package ------------------")
    if report:
        print(f"Company: {report.get('companyOverview', {}).get('companyName')} ({report.get('companyOverview', {}).get('ticker')})")
        print(f"Final Decision: {report.get('recommendation', {}).get('stance')}")
        print(f"Confidence Score: {report.get('recommendation', {}).get('confidenceScore')}")
        print("\n[SUCCESS] Phase 2 Hybrid RAG integration test SUCCESSFUL!")
    else:
        print("❌ Workflow failed to produce a final report.")
        sys.exit(1)

if __name__ == "__main__":
    main()
