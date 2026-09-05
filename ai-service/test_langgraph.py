import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.agent.langgraph_orchestrator import MavenLangGraphOrchestrator
from src.utils.logger import logger

def main():
    print("=" * 60)
    print(" Testing LangGraph Stateful Graph Orchestrator for Maven")
    print("=" * 60)
    
    orchestrator = MavenLangGraphOrchestrator()
    print("\nLangGraph StateGraph compiled successfully!")
    
    query = "Apple"
    print(f"\nExecuting LangGraph workflow for query: '{query}'")
    
    result = orchestrator.run(query)
    
    print("\n" + "=" * 60)
    print(" Execution Completed Successfully!")
    print("=" * 60)
    print(f"Ticker: {result.get('ticker')}")
    print(f"Quality Score: {result.get('quality_score')}")
    print(f"Needs Fallback: {result.get('needs_fallback')}")
    print(f"Execution Logs: {result.get('execution_logs')}")
    
    report = result.get("report")
    if report:
        rec = report.get("recommendation", {})
        print(f"\nFinal Recommendation Stance: {rec.get('stance')}")
        print(f"Report ID: {report.get('reportId')}")
    else:
        print("\nNo report generated.")

if __name__ == "__main__":
    main()
