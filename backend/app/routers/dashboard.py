from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas.dashboard import DashboardSummary
from ..services import dashboard_service
from ..dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return dashboard_service.get_summary(db, current_user.id)