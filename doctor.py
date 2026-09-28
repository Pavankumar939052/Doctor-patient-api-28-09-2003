from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.dependencies import get_current_user, require_admin
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.post(
    "",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED
)
def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    existing_doctor = (
        db.query(Doctor)
        .filter(Doctor.email == doctor_data.email)
        .first()
    )

    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor email already exists"
        )

    existing_user = (
        db.query(User)
        .filter(User.email == doctor_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Create login account for the doctor
    doctor_user = User(
        email=doctor_data.email,
        hashed_password=hash_password(doctor_data.password),
        role="doctor"
    )

    db.add(doctor_user)
    db.flush()

    # Create doctor record linked to the user
    doctor = Doctor(
        user_id=doctor_user.id,
        name=doctor_data.name,
        specialization=doctor_data.specialization,
        email=doctor_data.email
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


@router.get(
    "",
    response_model=list[DoctorResponse]
)
def get_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Doctor).all()


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return doctor


@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def update_doctor(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    if doctor_data.email:
        existing_doctor = (
            db.query(Doctor)
            .filter(
                Doctor.email == doctor_data.email,
                Doctor.id != doctor_id
            )
            .first()
        )

        if existing_doctor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor email already exists"
            )

    update_data = doctor_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(doctor, field, value)

    db.commit()
    db.refresh(doctor)

    return doctor


@router.delete(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    # Soft delete
    doctor.is_active = False

    db.commit()
    db.refresh(doctor)

    return doctor