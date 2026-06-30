# ─────────────────────────────────────────────────────────────────
# src/critique/compiler.py
# ─────────────────────────────────────────────────────────────────
#
# CritiqueCompiler merging, sanitizing, and validating observations.
# ─────────────────────────────────────────────────────────────────

import uuid
from datetime import datetime
from typing import List, Dict
from src.committee.models import InvestmentCommitteeReview
from src.critique.constants import BiasCategory, CritiquePriority, CritiqueSeverity, CritiqueStatus
from src.critique.models import (
    AIAssumptionObservation,
    AIBiasObservation,
    AIReasoningFlawObservation,
    AICritiqueObservation,
    LineageTrace,
    RobustnessSummary,
    RobustnessAnalysis,
    BiasCheck,
    CoverageAudit,
    InvalidatingAssumption,
    DecisionChangingEvidence,
    MissingEvidenceValue,
    WeakReasoningLink,
    ActionableVulnerabilities,
    CritiqueCompilerReport,
    CritiqueMetadata,
    InvestmentCritique
)
from src.thesis.models import InvestmentThesis

class CritiqueCompiler:
    """
    Sanitizes raw AI observations, handles value clamping, normalizes enums,
    filters out hallucinated statement IDs, and compiles the final InvestmentCritique.
    """
    @staticmethod
    def compile(
        det_out: dict,
        ai_obs: AICritiqueObservation,
        thesis: InvestmentThesis,
        review: InvestmentCommitteeReview,
        status: CritiqueStatus,
        initial_warnings: List[str],
        prompt_version: str = None,
        prompt_hash: str = None,
        finish_reason: str = None,
        tokens_used: int = None,
        llm_model_name: str = "unknown"
    ) -> InvestmentCritique:
        
        # 1. Collect all valid statement IDs in the thesis to detect hallucinations
        valid_stmt_ids = set()
        for sec in thesis.sections.values():
            for stmt in sec.statements:
                valid_stmt_ids.add(stmt.statementId)
                
        # Compilation tracking metrics
        received = len(ai_obs.observedAssumptions) + len(ai_obs.observedBiases) + len(ai_obs.observedReasoningFlaws)
        validated = 0
        rejected = 0
        normalized_count = 0
        warnings = list(initial_warnings)
        
        bias_evals: List[BiasCheck] = []
        invalidating_assumptions: List[InvalidatingAssumption] = []
        weakest_reasoning: List[WeakReasoningLink] = []
        
        # Helper: Numeric clamping utility
        def clamp_value(val: float, val_name: str) -> (float, bool):
            if val < 0.0:
                return 0.0, True
            if val > 1.0:
                return 1.0, True
            return val, False

        # --- A. Compile Assumptions ---
        for idx, asm in enumerate(ai_obs.observedAssumptions):
            # Check statement ID validation
            if asm.statementId not in valid_stmt_ids:
                rejected += 1
                warnings.append(f"Assumption observation discarded: statementId '{asm.statementId}' is hallucinated/invalid.")
                continue
                
            # Clamp vulnerability score
            score, was_clamped = clamp_value(asm.vulnerabilityScore, "vulnerabilityScore")
            if was_clamped:
                normalized_count += 1
                warnings.append(f"Assumption vulnerabilityScore '{asm.vulnerabilityScore}' clamped to valid range [0.0, 1.0].")
                
            validated += 1
            asm_id = f"ASM-{len(invalidating_assumptions)+1:03d}"
            
            # Map priority based on vulnerability score
            priority = CritiquePriority.LOW
            if score >= 0.80:
                priority = CritiquePriority.BLOCKING
            elif score >= 0.60:
                priority = CritiquePriority.HIGH
            elif score >= 0.40:
                priority = CritiquePriority.MEDIUM
                
            invalidating_assumptions.append(InvalidatingAssumption(
                assumptionId=asm_id,
                description=asm.description,
                invalidationTrigger=asm.weaknessRationale,
                priority=priority,
                lineage=LineageTrace(
                    reviewerIds=[asm.reviewerId],
                    statementIds=[asm.statementId]
                )
            ))

        # --- B. Compile Biases ---
        for idx, bias in enumerate(ai_obs.observedBiases):
            # Normalization 1: Case-insensitive enum parsing
            raw_cat = bias.category
            norm_cat = raw_cat.strip().upper().replace(" ", "_")
            if norm_cat not in BiasCategory.__members__:
                rejected += 1
                warnings.append(f"Bias check observation discarded: unknown category '{raw_cat}'.")
                continue
                
            cat_enum = BiasCategory[norm_cat]
            if raw_cat != cat_enum.value:
                normalized_count += 1
                warnings.append(f"Bias category '{raw_cat}' normalized case-insensitively to '{cat_enum.value}'.")
                
            # Normalization 2: Sanitize list of statement IDs
            sanitized_stmts = []
            for stmt in bias.involvedStatements:
                if stmt in valid_stmt_ids:
                    sanitized_stmts.append(stmt)
                else:
                    normalized_count += 1
                    warnings.append(f"Sanitized bias observation: discarded invalid ID '{stmt}'.")
                    
            if not sanitized_stmts:
                rejected += 1
                warnings.append(f"Bias check observation discarded: involvedStatements is empty after validation.")
                continue
                
            validated += 1
            bias_id = f"CB-{len(bias_evals)+1:03d}"
            
            bias_evals.append(BiasCheck(
                biasId=bias_id,
                category=cat_enum,
                severity=CritiqueSeverity.WARNING,
                priority=CritiquePriority.MEDIUM,
                description=bias.description,
                lineage=LineageTrace(
                    reviewerIds=bias.involvedReviewers,
                    statementIds=sanitized_stmts
                )
            ))

        # --- C. Compile Reasoning Flaws ---
        for idx, flaw in enumerate(ai_obs.observedReasoningFlaws):
            # Sanitize statement IDs
            sanitized_stmts = []
            for stmt in flaw.involvedStatements:
                if stmt in valid_stmt_ids:
                    sanitized_stmts.append(stmt)
                else:
                    normalized_count += 1
                    warnings.append(f"Sanitized reasoning flaw observation: discarded invalid ID '{stmt}'.")
                    
            if not sanitized_stmts:
                rejected += 1
                warnings.append(f"Reasoning flaw observation discarded: involvedStatements is empty after validation.")
                continue
                
            validated += 1
            
            weakest_reasoning.append(WeakReasoningLink(
                reviewerId=flaw.reviewerId,
                logicalLeak=flaw.logicalLeak,
                priority=CritiquePriority.HIGH,
                lineage=LineageTrace(
                    reviewerIds=[flaw.reviewerId],
                    statementIds=sanitized_stmts
                )
            ))

        # --- D. Compute Bias Risk Index inside RobustnessSummary ---
        total_biases = len(bias_evals)
        bias_risk = min(1.0, total_biases * 0.20)
        
        rob_summary_base = det_out["robustnessSummary"]
        rob_summary = RobustnessSummary(
            stabilityIndex=rob_summary_base.stabilityIndex,
            assumptionQuality=0.90 if len(invalidating_assumptions) == 0 else max(0.0, round(1.0 - (len(invalidating_assumptions) * 0.15), 4)),
            coverageQuality=rob_summary_base.coverageQuality,
            confidenceConsistency=rob_summary_base.confidenceConsistency,
            biasRisk=round(bias_risk, 4)
        )

        # Assemble remaining ActionableVulnerabilities placeholders
        decision_changing_ev: List[DecisionChangingEvidence] = []
        missing_ev: List[MissingEvidenceValue] = []
        
        # Pull missing evidence lists from Coverage Audits
        for audit in det_out["coverageAudits"]:
            for identifier in audit.missingIdentifiers:
                missing_ev.append(MissingEvidenceValue(
                    missingIdentifier=identifier,
                    benefitDescription=f"Increases valuation analysis metrics confidence bounds for target '{audit.targetPillar}'.",
                    priority=CritiquePriority.HIGH,
                    lineage=LineageTrace(reviewerIds=[audit.targetPillar], statementIds=[])
                ))

        actionable = ActionableVulnerabilities(
            invalidatingAssumptions=invalidating_assumptions,
            decisionChangingEvidence=decision_changing_ev,
            highestValueMissingEvidence=missing_ev,
            weakestReasoningChain=weakest_reasoning
        )

        report = CritiqueCompilerReport(
            totalObservationsReceived=received,
            totalObservationsValidated=validated,
            totalObservationsRejected=rejected,
            validationWarnings=warnings,
            normalizedFieldCount=normalized_count
        )

        meta = CritiqueMetadata(
            critiqueVersion="1.0.0",
            compiledAt=datetime.utcnow().isoformat() + "Z",
            latencyMs=0.0, # Will be set by orchestrator
            status=status,
            evaluatorsExecuted=["DeterministicCritiqueEngine", "AICritiqueEngine"],
            llmModelName=llm_model_name if status != CritiqueStatus.DEGRADED else "none",
            llmTemperature=0.1,
            compilerReport=report,
            promptVersion=prompt_version,
            promptHash=prompt_hash,
            finishReason=finish_reason,
            tokensUsed=tokens_used
        )

        return InvestmentCritique(
            critiqueId=str(uuid.uuid4()),
            thesisId=thesis.thesisId,
            committeeReviewId=review.committeeId,
            intelligenceId=thesis.intelligenceId,
            evidenceId=thesis.evidenceId,
            schemaVersion="1.0.0",
            robustnessSummary=rob_summary,
            robustnessAnalysis=det_out["robustnessAnalysis"],
            biasEvaluations=bias_evals,
            coverageAudits=det_out["coverageAudits"],
            actionableVulnerabilities=actionable,
            meta=meta
        )
