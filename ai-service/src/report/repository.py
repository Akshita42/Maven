import os
import json
import glob
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class ReportRepository(ABC):
    @abstractmethod
    def save(self, report: Dict[str, Any], session_id: str) -> None:
        pass

    @abstractmethod
    def get(self, report_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_latest(self, session_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_latest_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete(self, report_id: str) -> bool:
        pass

class FileReportRepository(ReportRepository):
    def __init__(self, base_dir: str = ".data/reports"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_file_path(self, report_id: str) -> str:
        return os.path.join(self.base_dir, f"{report_id}.json")

    def save(self, report: Dict[str, Any], session_id: str) -> None:
        report_id = report.get("reportId")
        if not report_id:
            raise ValueError("Report missing reportId")
            
        # Enrich the report with sessionId so it can be queried later
        report["_sessionId"] = session_id
        
        file_path = self._get_file_path(report_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def get(self, report_id: str) -> Optional[Dict[str, Any]]:
        file_path = self._get_file_path(report_id)
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def get_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        reports = []
        for file_path in glob.glob(os.path.join(self.base_dir, "*.json")):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("_sessionId") == session_id:
                        reports.append(data)
            except Exception:
                continue
        # Sort by generatedAt descending if available
        reports.sort(key=lambda r: r.get("generatedAt", ""), reverse=True)
        return reports

    def get_latest(self, session_id: str) -> Optional[Dict[str, Any]]:
        reports = self.get_by_session(session_id)
        return reports[0] if reports else None

    def get_latest_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        reports = []
        for file_path in glob.glob(os.path.join(self.base_dir, "*.json")):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("companyOverview", {}).get("ticker") == ticker:
                        reports.append(data)
            except Exception:
                continue
        reports.sort(key=lambda r: r.get("meta", {}).get("compiledAt", ""), reverse=True)
        return reports[0] if reports else None

    def delete(self, report_id: str) -> bool:
        file_path = self._get_file_path(report_id)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        return False
