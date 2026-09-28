from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user, require_admin, require_doctor
from app.models.assignment import DoctorPatient
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User
from app.schemas.assignment import AssignmentResponse
from app.schemas.patient import PatientResponse


router = APIRouter(
    prefix="/doctors",
    tags=["Doctor-Patient Assignment"]
)


@router.post(
    "/{doctor_id}/patients/{patient_id}",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED
)
def assign_patient(
    doctor_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    doctor = (
        db.query(Doctor)
        .filter(
            Doctor.id == doctor_id,
            Doctor.is_active == True
        )
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found or inactive"
        )

    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    existing_assignment = (
        db.query(DoctorPatient)
        .filter(
            DoctorPatient.doctor_id == doctor_id,
            DoctorPatient.patient_id == patient_id
        )
        .first()
    )

    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient is already assigned to this doctor"
        )

    assignment = DoctorPatient(
        doctor_id=doctor_id,
        patient_id=patient_id
    )

    db.add(assignment)
    db.commit()

    return {
        "message": "Patient assigned successfully",
        "doctor_id": doctor_id,
        "patient_id": patient_id
    }


@router.get(
    "/{doctor_id}/patients",
    response_model=list[PatientResponse]
)
def get_doctor_patients(
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

    # Admin can view any doctor's patients.
    if current_user.role == "admin":
        pass

    # Doctor can only view their own patients.
    elif current_user.role == "doctor":

        if doctor.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own patients"
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    patients = (
        db.query(Patient)
        .join(
            DoctorPatient,
            DoctorPatient.patient_id == Patient.id
        )
        .filter(
            DoctorPatient.doctor_id == doctor_id
        )
        .all()
    )

    return patients