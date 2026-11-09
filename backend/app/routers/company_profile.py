from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CompanyProfile, User
from ..schemas.company_profile import CompanyProfileCreate, CompanyProfileUpdate, CompanyProfileRead
from ..dependencies import get_current_user

router = APIRouter(prefix="/company-profile", tags=["company-profile"])


@router.get("", response_model=CompanyProfileRead)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found")
    return profile


@router.put("", response_model=CompanyProfileRead)
def upsert_profile(
    payload: CompanyProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == current_user.id).first()
    if profile:
        for k, v in payload.model_dump().items():
            setattr(profile, k, v)
    else:
        profile = CompanyProfile(user_id=current_user.id, **payload.model_dump())
        db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.patch("", response_model=CompanyProfileRead)
def patch_profile(
    payload: CompanyProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    return profile
