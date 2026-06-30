import asyncio
from src.report.repository import FileReportRepository
from src.report.models import InvestmentReport
import uuid

def test_repo():
    repo = FileReportRepository()
    
    # create a mock report
    r_id = str(uuid.uuid4())
    s_id = str(uuid.uuid4())
    report_dict = {
        "reportId": r_id,
        "executiveSummary": {},
        "companyOverview": {},
        "recommendation": {"stance": "BUY"}
    }
    
    repo.save(report_dict, s_id)
    print("Saved report", r_id)
    
    loaded = repo.get(r_id)
    print("Loaded by get:", loaded is not None)
    
    latest = repo.get_latest(s_id)
    print("Loaded by get_latest:", latest is not None)
    
if __name__ == "__main__":
    test_repo()
