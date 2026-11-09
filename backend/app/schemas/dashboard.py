from pydantic import BaseModel
from typing import Dict


class DashboardSummary(BaseModel):
    total_invoiced: float
    total_paid: float
    total_pending: float
    count_by_status: Dict[str, int]
