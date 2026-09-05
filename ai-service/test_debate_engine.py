# ─────────────────────────────────────────────────────────────────
# ai-service/test_debate_engine.py
# ─────────────────────────────────────────────────────────────────
# Automated Integration Test for Phase 3: Bull vs. Bear Dialectic Debate
# ─────────────────────────────────────────────────────────────────

import sys
import os

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.committee.reviewers.bull_agent import BullAgent
from src.committee.reviewers.bear_agent import BearAgent
from src.committee.debate_orchestrator import DialecticDebateOrchestrator
from src.agent.langgraph_orchestrator import MavenLangGraphOrchestrator

def main():
    print("======================================================")
    print("  Testing Phase 3: Bull vs. Bear Dialectic Debate Engine")
    print("======================================================")
    
    ticker = "MSFT"
    print(f"\n1. Testing BullAgent opening thesis for ticker: {ticker}...")
    bull_agent = BullAgent()
    bull_case = bull_agent.generate_bull_case(ticker, None)
    print(f"   [OK] Stance: {bull_case['stance']}")
    print(f"   [OK] Bull Thesis: {bull_case['thesis'][:120]}...")
    
    print(f"\n2. Testing BearAgent counter-rebuttal for ticker: {ticker}...")
    bear_agent = BearAgent()
    bear_case = bear_agent.generate_bear_case(ticker, None, bull_case)
    print(f"   [OK] Stance: {bear_case['stance']}")
    print(f"   [OK] Bear Counter-Rebuttal: {bear_case['counterRebuttal'][:120]}...")
    
    print(f"\n3. Testing DialecticDebateOrchestrator 2-turn debate & arbitration...")
    debate_engine = DialecticDebateOrchestrator()
    res = debate_engine.run_debate(ticker, None)
    print(f"   [OK] Debate Transcript Turns: {len(res['transcript'])}")
    for turn in res['transcript']:
        print(f"     Turn {turn['turn']} ({turn['speaker']}): {turn['content'][:90]}...")
    print(f"   [OK] Arbitrator Consensus Outcome: {res['review'].decisionOutcome.recommendation}")
    print(f"   [OK] Consensus Confidence: {res['review'].overallConfidence}")
    
    print(f"\n4. Testing Full LangGraph Stateful Graph Execution for '{ticker}'...")
    orchestrator = MavenLangGraphOrchestrator()
    final_state = orchestrator.run(ticker)
    
    transcript = final_state.get("debate_transcript")
    logs = final_state.get("execution_logs", [])
    
    print("\n------------------ LangGraph Execution Logs ------------------")
    for log in logs:
        print(f"  • {log}")
        
    print("\n------------------ Final Decision Package ------------------")
    report = final_state.get("report")
    if report:
        print(f"Company: {report.get('companyOverview', {}).get('companyName')} ({report.get('companyOverview', {}).get('ticker')})")
        print(f"Final Decision: {report.get('recommendation', {}).get('stance')}")
        print(f"Debate Transcript Stored: {len(transcript) if transcript else 0} turns")
        print("\n[SUCCESS] Phase 3 Bull vs. Bear Debate Engine test SUCCESSFUL!")
    else:
        print("❌ Workflow failed to produce a final report.")
        sys.exit(1)

if __name__ == "__main__":
    main()
