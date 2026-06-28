# ─────────────────────────────────────────────────────────────────
# src/critique/models.py
# ─────────────────────────────────────────────────────────────────
#
# Immutable domain models and type-safe AI observation schemas.
# ─────────────────────────────────────────────────────────────────

from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field
from src.critique.constants import BiasCategory, CritiquePriority, CritiqueSeverity, CritiqueStatus

class LineageTrace(BaseModel):
    model_config = ConfigDict(frozen=True)
    reviewerIds: List[str]
    statementIds: List[str]

# Intermediate AI Observations (Parser inputs before normalization)
class AIAssumptionObservation(BaseModel):
    model_config = ConfigDict(frozen=True)
    reviewerId: str
    statementId: str
    description: str
    vulnerabilityScore: float
    weaknessRationale: str

class AIBiasObservation(BaseModel):
    model_config = ConfigDict(frozen=True)
    category: str
    description: str
    involvedReviewers: List[str]
    involvedStatements: List[str]

class AIReasoningFlawObservation(BaseModel):
    model_config = ConfigDict(frozen=True)
    reviewerId: str
    involvedStatements: List[str]
    logicalLeak: str

class AICritiqueObservation(BaseModel):
    model_config = ConfigDict(frozen=True)
    observedAssumptions: List[AIAssumptionObservation]
    observedBiases: List[AIBiasObservation]
    observedReasoningFlaws: List[AIReasoningFlawObservation]

# Domain Models (Strictly validated and frozen)
class RobustnessSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    stabilityIndex: float = Field(ge=0.0, le=1.0)
    assumptionQuality: float = Field(ge=0.0, le=1.0)
    coverageQuality: float = Field(ge=0.0, le=1.0)
    confidenceConsistency: float = Field(ge=0.0, le=1.0)
    biasRisk: float = Field(ge=0.0, le=1.0)

class ScenarioOutcome(BaseModel):
    model_config = ConfigDict(frozen=True)
    scenarioId: str
    name: str
    simulatedScore: float = Field(ge=0.0, le=10.0)
    scoreDelta: float
    isRobust: bool

class RobustnessAnalysis(BaseModel):
    model_config = ConfigDict(frozen=True)
    originalScore: float
    scenarios: List[ScenarioOutcome]
    mostSensitiveMetric: str
    robustnessRationale: str

class BiasCheck(BaseModel):
    model_config = ConfigDict(frozen=True)
    biasId: str
    category: BiasCategory
    severity: CritiqueSeverity
    priority: CritiquePriority
    description: str
    lineage: LineageTrace

class CoverageAudit(BaseModel):
    model_config = ConfigDict(frozen=True)
    auditId: str
    targetPillar: str
    severity: CritiqueSeverity
    priority: CritiquePriority
    description: str
    missingIdentifiers: List[str]

class InvalidatingAssumption(BaseModel):
    model_config = ConfigDict(frozen=True)
    assumptionId: str
    description: str
    invalidationTrigger: str
    priority: CritiquePriority
    lineage: LineageTrace

class DecisionChangingEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)
    description: str
    targetMetric: str
    criticalThresholdValue: str
    priority: CritiquePriority
    lineage: LineageTrace

class MissingEvidenceValue(BaseModel):
    model_config = ConfigDict(frozen=True)
    missingIdentifier: str
    benefitDescription: str
    priority: CritiquePriority
    lineage: LineageTrace

class WeakReasoningLink(BaseModel):
    model_config = ConfigDict(frozen=True)
    reviewerId: str
    logicalLeak: str
    priority: CritiquePriority
    lineage: LineageTrace

class ActionableVulnerabilities(BaseModel):
    model_config = ConfigDict(frozen=True)
    invalidatingAssumptions: List[InvalidatingAssumption]
    decisionChangingEvidence: List[DecisionChangingEvidence]
    highestValueMissingEvidence: List[MissingEvidenceValue]
    weakestReasoningChain: List[WeakReasoningLink]

class CritiqueCompilerReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    totalObservationsReceived: int
    totalObservationsValidated: int
    totalObservationsRejected: int
    validationWarnings: List[str]
    normalizedFieldCount: int

class CritiqueMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    critiqueVersion: str = "1.0.0"
    compiledAt: str
    latencyMs: float
    status: CritiqueStatus
    evaluatorsExecuted: List[str]
    llmModelName: str
    llmTemperature: float
    compilerReport: CritiqueCompilerReport

class InvestmentCritique(BaseModel):
    model_config = ConfigDict(frozen=True)
    critiqueId: str
    thesisId: str
    committeeReviewId: str
    intelligenceId: str
    evidenceId: str
    schemaVersion: str = "1.0.0"
    robustnessSummary: RobustnessSummary
    robustnessAnalysis: RobustnessAnalysis
    biasEvaluations: List[BiasCheck]
    coverageAudits: List[CoverageAudit]
    actionableVulnerabilities: ActionableVulnerabilities
    meta: CritiqueMetadata
