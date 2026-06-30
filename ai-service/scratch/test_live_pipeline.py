import sys
from src.agent.services.pipeline_service import PipelineService

def run_validation():
    companies = ["Apple", "Microsoft", "Nvidia"]
    
    print("==================================================")
    print("LIVE GEMINI VALIDATION")
    print("==================================================\n")
    
    for c in companies:
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
            
            print(f"- Company: {name}")
            print(f"- Gemini Model: {model_used}")
            print(f"- Tokens Used: {tokens}")
            print(f"- Finish Reason: {finish_reason}")
            print(f"- Critique Status: {status}")
            print(f"- Recommendation: {stance}")
            print(f"- Conviction: {conviction}")
            print()
            
        except Exception as e:
            print(f"Failed processing {c}")
            print(f"  Error: {str(e)}")
            import traceback
            traceback.print_exc(limit=2)
            print()

if __name__ == "__main__":
    run_validation()
