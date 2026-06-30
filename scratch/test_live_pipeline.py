import sys
import os
import time

# Add the project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ai-service')))

from src.agent.services.pipeline_service import PipelineService
from src.agent.exceptions import TerminalAgentError

def test_company(query: str):
    print(f"\n{'='*50}")
    print(f"Testing Query: {query}")
    print(f"{'='*50}")
    
    start_time = time.time()
    try:
        report = PipelineService.run_from_query(query)
    except TerminalAgentError as e:
        print(f"PIPELINE FAILED: {str(e)}")
        return
    except Exception as e:
        print(f"UNEXPECTED ERROR: {str(e)}")
        return
        
    exec_time = time.time() - start_time
    
    ev = report.evidence
    
    comp_name = ev.companyProfile.companyName.value if ev.companyProfile and ev.companyProfile.companyName else "Unknown"
    ticker = ev.companyProfile.ticker.value if ev.companyProfile and ev.companyProfile.ticker else "Unknown"
    
    providers = list(ev.providers.keys()) if ev.providers else []
    
    market_cap = ev.marketData.marketCap.value if ev.marketData and ev.marketData.marketCap else "N/A"
    
    # Financials extract
    rev = "N/A"
    ni = "N/A"
    if ev.financials and ev.financials.value and ev.financials.value.annualIncomeStatements:
        stmt = ev.financials.value.annualIncomeStatements[0]
        if stmt.revenue: rev = stmt.revenue.value
        if stmt.netIncome: ni = stmt.netIncome.value
        
    evidence_conf = ev.resolutionConfidence
    
    # Recommendation
    rec = report.recommendation
    stance = rec.stance.value if rec and rec.stance else "Unknown"
    conv = rec.conviction.value if rec and rec.conviction else "Unknown"
    
    # Committee
    com = report.committee
    com_decision = com.decisionOutcome.recommendation.value if com and com.decisionOutcome else "Unknown"
    
    print(f"Company Name       : {comp_name}")
    print(f"Ticker             : {ticker}")
    print(f"Providers Used     : {', '.join(providers)}")
    print(f"Revenue            : {rev}")
    print(f"Net Income         : {ni}")
    print(f"Market Cap         : {market_cap}")
    print(f"PE Ratio           : N/A (Not in evidence schema)")
    print(f"Evidence Confidence: {evidence_conf}")
    print(f"Committee Decision : {com_decision}")
    print(f"Recommendation     : {stance}")
    print(f"Conviction         : {conv}")
    print(f"Execution Time     : {exec_time:.2f} seconds")

if __name__ == "__main__":
    queries = [
        "Apple",
        "Microsoft",
        "Nvidia",
        "Tesla",
        "Reliance Industries",
        "FakeCompanyXYZ"
    ]
    
    for q in queries:
        test_company(q)
