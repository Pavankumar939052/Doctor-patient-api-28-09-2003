from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


def create_patient(
    db: Session,
    patient_data: PatientCreate
):
    patient = Patient(
        name=patient_data.name,
        age=patient_data.age,
        phone=patient_data.phone
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


def update_patient(
    db: Session,
    patient_id: int,
    patient_data: PatientUpdate
):
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

    update_data = patient_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    return patient