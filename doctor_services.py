from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.doctor import DoctorCreate


def create_doctor(
    db: Session,
    doctor_data: DoctorCreate
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

    doctor_user = User(
        email=doctor_data.email,
        hashed_password=hash_password(
            doctor_data.password
        ),
        role="doctor"
    )

    db.add(doctor_user)
    db.flush()

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