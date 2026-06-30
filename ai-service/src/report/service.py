from typing import Optional, List, Dict, Any, Union
from src.report.repository import ReportRepository, FileReportRepository
from src.report.models import InvestmentReport

class ReportService:
    _repository: ReportRepository = FileReportRepository()

    @classmethod
    def set_repository(cls, repo: ReportRepository):
        cls._repository = repo

    @classmethod
    def save(cls, report: Union[InvestmentReport, Dict[str, Any]], session_id: str) -> None:
        if isinstance(report, dict):
            report_data = report
        else:
            report_data = report.model_dump()
        cls._repository.save(report_data, session_id)

    @classmethod
    def get(cls, report_id: str) -> Optional[Dict[str, Any]]:
        return cls._repository.get(report_id)

    @classmethod
    def get_latest(cls, session_id: str) -> Optional[Dict[str, Any]]:
        return cls._repository.get_latest(session_id)

    @classmethod
    def get_by_session(cls, session_id: str) -> List[Dict[str, Any]]:
        return cls._repository.get_by_session(session_id)

    @classmethod
    def build_conversation_context(cls, report: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts context from a report for Conversational Agents."""
        return {
            "reportId": report.get("reportId"),
            "companyName": report.get("companyOverview", {}).get("companyName"),
            "ticker": report.get("companyOverview", {}).get("ticker"),
            "recommendation": report.get("recommendation", {}).get("stance")
        }

    @classmethod
    def build_explainability_context(cls, report: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts full lineage data for the ExplanationAgent."""
        return {
            "evidence": report.get("evidenceSummary"),
            "intelligence": report.get("intelligenceHighlights"),
            "committee": report.get("committeeDecision"),
            "critique": report.get("critique"),
            "recommendation": report.get("recommendation")
        }
