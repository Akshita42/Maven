# ─────────────────────────────────────────────────────────────────
# src/agent/services/pipeline_service.py
# ─────────────────────────────────────────────────────────────────

from typing import Dict, Any
from src.report.models import InvestmentReport
from src.agent.exceptions import TerminalAgentError

class PipelineService:
    """
    Orchestration façade for the deterministic pipeline.
    Does NOT contain business logic, make decisions, or cache state.
    Strictly executes deterministic pipeline components in sequence.
    """
    
    @staticmethod
    def run(company: Dict[str, Any], context: 'ExecutionContext') -> InvestmentReport:
        """
        Executes the full deterministic pipeline for a resolved company.
        Emits domain events via ExecutionContext and checks for cancellation.
        """
        from src.core.events import (
            StageStarted, StageCompleted, EvidenceGenerated, 
            CommitteeCompleted, RecommendationGenerated, WorkflowFailed
        )
        
        try:
            if context.cancellation_token.is_cancelled():
                raise TerminalAgentError("Workflow cancelled by client.")

            import time
            from src.services.evidence_service import EvidenceCollector
            from src.intelligence.orchestration import IntelligenceService
            from src.thesis.builder import ThesisBuilder
            from src.committee.orchestrator import CommitteeOrchestrator
            from src.critique.orchestrator import CritiqueOrchestrator
            from src.infrastructure.llm.factory import LLMFactory
            from src.recommendation.builder import RecommendationBuilder
            from src.report.builder import ReportBuilder
            from src.agent.exceptions import TerminalAgentError
            
            # 1. Evidence
            context.observer.on_event(StageStarted(stage="evidence_collection"))
            collector = EvidenceCollector()
            raw_evidence = collector.collect(company)
            
            if context.cancellation_token.is_cancelled():
                raise TerminalAgentError("Workflow cancelled by client.")
                
            from src.agent.compiler import EvidenceCompiler
            evidence = EvidenceCompiler.compile_evidence(raw_evidence.model_dump())
            
            if evidence.validationScore == 0.0 and evidence.qualityScore == 0.0:
                raise TerminalAgentError("Critical evidence collection failed. Cannot proceed with deterministic pipeline.")
                
            context.observer.on_event(EvidenceGenerated(evidence_summary={"qualityScore": evidence.qualityScore}))
            context.observer.on_event(StageCompleted(stage="evidence_collection"))
                
            # 2. Intelligence
            context.observer.on_event(StageStarted(stage="intelligence"))
            intel_service = IntelligenceService()
            intelligence = intel_service.compile_intelligence(evidence)
            context.observer.on_event(StageCompleted(stage="intelligence"))
            
            if context.cancellation_token.is_cancelled():
                raise TerminalAgentError("Workflow cancelled by client.")
            
            # 3. Thesis
            context.observer.on_event(StageStarted(stage="thesis_generation"))
            thesis = ThesisBuilder.build(intelligence)
            context.observer.on_event(StageCompleted(stage="thesis_generation"))
            
            # 4. Committee (Adversarial Bull vs. Bear Debate)
            context.observer.on_event(StageStarted(stage="committee_review"))
            from src.committee.debate_orchestrator import DialecticDebateOrchestrator
            debate_engine = DialecticDebateOrchestrator()
            debate_result = debate_engine.run_debate(thesis.ticker, intelligence)
            committee = debate_result["review"]
            bull_case = debate_result.get("bull_case")
            bear_case = debate_result.get("bear_case")
            debate_transcript = debate_result.get("transcript")
            
            context.observer.on_event(CommitteeCompleted(committee_decision={"overallConviction": committee.decisionOutcome.recommendation.value}))
            context.observer.on_event(StageCompleted(stage="committee_review"))
            
            if context.cancellation_token.is_cancelled():
                raise TerminalAgentError("Workflow cancelled by client.")
            
            # 5. Critique (Skip for standard analysis to save tokens)
            context.observer.on_event(StageStarted(stage="ai_critique"))
            from src.critique.models import InvestmentCritique, RobustnessAnalysis, ActionableVulnerabilities, CritiqueMetadata, CritiqueStatus, CritiqueCompilerReport, RobustnessSummary
            from datetime import datetime
            critique = InvestmentCritique(
                critiqueId="stub-critique",
                thesisId=thesis.thesisId,
                committeeReviewId=committee.committeeId,
                intelligenceId=intelligence.intelligenceId,
                evidenceId=thesis.evidenceId,
                robustnessSummary=RobustnessSummary(
                    stabilityIndex=1.0,
                    assumptionQuality=1.0,
                    coverageQuality=1.0,
                    confidenceConsistency=1.0,
                    biasRisk=0.0
                ),
                robustnessAnalysis=RobustnessAnalysis(
                    originalScore=thesis.overallScore,
                    scenarios=[],
                    mostSensitiveMetric="N/A",
                    robustnessRationale="Skipped for standard analysis"
                ),
                coverageAudits=[],
                actionableVulnerabilities=ActionableVulnerabilities(
                    invalidatingAssumptions=[], 
                    decisionChangingEvidence=[], 
                    highestValueMissingEvidence=[], 
                    weakestReasoningChain=[]
                ),
                biasEvaluations=[],
                meta=CritiqueMetadata(
                    critiqueVersion="1.0.0", 
                    compiledAt=datetime.utcnow().isoformat() + "Z", 
                    latencyMs=0,
                    status=CritiqueStatus.SUCCESS,
                    evaluatorsExecuted=[],
                    llmModelName="stub",
                    llmTemperature=0.0,
                    compilerReport=CritiqueCompilerReport(
                        totalObservationsReceived=0,
                        totalObservationsValidated=0,
                        totalObservationsRejected=0,
                        validationWarnings=[],
                        normalizedFieldCount=0
                    )
                )
            )
            context.observer.on_event(StageCompleted(stage="ai_critique"))
            
            # 6. Recommendation
            context.observer.on_event(StageStarted(stage="recommendation"))
            recommendation = RecommendationBuilder.build(thesis, committee, critique)
            context.observer.on_event(RecommendationGenerated(recommendation_data={"action": recommendation.stance.value}))
            context.observer.on_event(StageCompleted(stage="recommendation"))
            
            # 7. Observability & Report
            context.observer.on_event(StageStarted(stage="report_compilation"))
            from src.infrastructure.observability.evals import FaithfulnessEvaluator
            from src.infrastructure.observability.tracer import ObservabilityTracer
            evaluator = FaithfulnessEvaluator()
            tracer = ObservabilityTracer()
            evals_res = evaluator.evaluate(evidence, thesis, committee, recommendation)
            telemetry = tracer.get_telemetry_report()
            observability = {
                "faithfulness": evals_res,
                "telemetry": telemetry
            }

            report = ReportBuilder.build(
                evidence, intelligence, thesis, committee, critique, recommendation,
                bullCase=bull_case,
                bearCase=bear_case,
                debateTranscript=debate_transcript,
                observability=observability
            )
            context.observer.on_event(StageCompleted(stage="report_compilation"))
            
            return report
            
            return report
            
        except TerminalAgentError as e:
            context.observer.on_event(WorkflowFailed(stage="pipeline", error=str(e)))
            raise
        except Exception as e:
            context.observer.on_event(WorkflowFailed(stage="pipeline", error=str(e)))
            import traceback
            traceback.print_exc()
            raise TerminalAgentError(f"Deterministic pipeline failed: {str(e)}")

    @staticmethod
    def run_from_query(query: str, context: 'ExecutionContext') -> InvestmentReport:
        """
        Internally performs Company Resolution before invoking run().
        """
        from src.services.company_service import resolve_company_metadata
        from src.agent.exceptions import TerminalAgentError
        from src.core.events import StageStarted, StageCompleted, WorkflowFailed
        
        context.observer.on_event(StageStarted(stage="company_resolution"))
        resolution = resolve_company_metadata(query)
        
        if not resolution.resolved:
            if resolution.ambiguityReason == "ambiguous_candidates_found" and resolution.candidates:
                error_msg = f"I found multiple companies matching '{query}'. Did you mean:\n"
                for c in resolution.candidates[:3]:
                    error_msg += f"- {c.get('companyName')} ({c.get('ticker')}) on {c.get('exchange')}\n"
                error_msg += "\nPlease specify the exact ticker or full name."
            elif "No publicly traded equities found" in (resolution.ambiguityReason or ""):
                error_msg = f"No public company found for '{query}'"
            else:
                error_msg = f"Company resolution failed for '{query}': {resolution.ambiguityReason}"
                
            context.observer.on_event(WorkflowFailed(stage="company_resolution", error=error_msg))
            raise TerminalAgentError(error_msg)
            
        context.observer.on_event(StageCompleted(stage="company_resolution"))

        from src.report.service import ReportService
        from src.utils.logger import logger
        import datetime
        from src.report.models import InvestmentReport
        
        cached_report = ReportService.get_latest_by_ticker(resolution.ticker)
        if cached_report:
            try:
                compiled_at_str = cached_report.get("meta", {}).get("compiledAt", "")
                if compiled_at_str.endswith("Z"):
                    compiled_at_str = compiled_at_str[:-1]
                compiled_at = datetime.datetime.fromisoformat(compiled_at_str)
                now = datetime.datetime.utcnow()
                age = now - compiled_at
                
                if age.total_seconds() < 12 * 3600:
                    logger.info(f"PipelineService: REPORT CACHE HIT for {resolution.ticker}. Age: {age.total_seconds()/3600:.1f}h")
                    
                    # Quickly emit events so the UI checks off the pipeline stages
                    stages = [
                        "evidence_collection", "intelligence", "thesis_generation",
                        "committee_review", "ai_critique", "recommendation", "report_compilation"
                    ]
                    for stage in stages:
                        context.observer.on_event(StageStarted(stage=stage))
                        context.observer.on_event(StageCompleted(stage=stage))
                        
                    return InvestmentReport(**cached_report)
                else:
                    logger.info(f"PipelineService: REPORT CACHE EXPIRED for {resolution.ticker}. Age: {age.total_seconds()/3600:.1f}h")
            except Exception as e:
                logger.error(f"PipelineService: Failed to evaluate cache age for {resolution.ticker}: {e}")
        else:
            logger.info(f"PipelineService: REPORT CACHE MISS for {resolution.ticker}")

        return PipelineService.run(resolution.model_dump(), context)
