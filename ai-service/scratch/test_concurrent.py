import os
import sys
import threading
from src.agent.services.pipeline_service import PipelineService

def run_for_company(c):
    try:
        report = PipelineService.run_from_query(c)
        
        # --- GEMINI VALIDATION ---
        model_used = "N/A"
        tokens = 0
        finish_reason = "N/A"
        if hasattr(report.critique.meta, 'llmModelName'):
            model_used = report.critique.meta.llmModelName
            if hasattr(report.critique.meta, 'tokensUsed'):
                tokens = report.critique.meta.tokensUsed
            if hasattr(report.critique.meta, 'finishReason'):
                finish_reason = report.critique.meta.finishReason
        
        name = report.evidence.companyProfile.companyName.value
        status = report.critique.meta.status.value
        stance = report.executiveSummary.stance.value
        conviction = report.executiveSummary.conviction.value
        
        print(f"\n- Company: {name}")
        print(f"- Gemini Model: {model_used}")
        print(f"- Tokens Used: {tokens}")
        print(f"- Finish Reason: {finish_reason}")
        print(f"- Critique Status: {status}")
        print(f"- Recommendation: {stance}")
        print(f"- Conviction: {conviction}")
        
    except Exception as e:
        print(f"\nFailed processing {c}: {str(e)}")

if __name__ == "__main__":
    companies = ["Microsoft", "Nvidia"]
    threads = []
    for c in companies:
        t = threading.Thread(target=run_for_company, args=(c,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
