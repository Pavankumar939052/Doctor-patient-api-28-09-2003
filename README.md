# Doctor Patient API

A production-ready REST API built with FastAPI for managing doctors, patients, authentication, and doctor-patient assignments.

## Tech Stack

* Python 3.9+
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* JWT Authentication
* Passlib / bcrypt
* Uvicorn
* Pytest

## Project Structure

```text
doctor patient api/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── dependencies.py
│   └── main.py
├── scripts/
│   └── create_admin.py
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd "doctor patient api"
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example`.

Example:

```env
DATABASE_URL=sqlite:///./doctor_patient.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Do not commit `.env` to GitHub.

## Run the API

```bash
python -m uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Authentication Flow

1. Register a doctor using:

```text
POST /auth/register
```

2. Create the initial administrator using:

```bash
python scripts/create_admin.py
```

3. Login using:

```text
POST /auth/login
```

4. Copy the returned JWT access token.

5. Use the token in Swagger with:

```text
Authorize
```

and:

```text
Bearer <access_token>
```

## API Flow

### Authentication

```text
POST /auth/register
POST /auth/login
```

### Doctors

```text
POST   /doctors
GET    /doctors
GET    /doctors/{doctor_id}
PUT    /doctors/{doctor_id}
DELETE /doctors/{doctor_id}
```

Doctor deletion is implemented as a soft delete by setting `is_active` to `false`.

### Patients

```text
POST /patients
GET  /patients
GET  /patients/{patient_id}
PUT  /patients/{patient_id}
```

### Doctor-Patient Assignment

```text
POST /doctors/{doctor_id}/patients/{patient_id}
GET  /doctors/{doctor_id}/patients
```

## Authorization

### Admin

Administrators can:

* Create doctors
* Update doctors
* Soft-delete doctors
* Create patients
* Update patients
* Assign patients to doctors
* View doctors and patients

### Doctor

Doctors can:

* Login
* View doctors
* View their assigned patients
* View individual patients only when assigned to them

Doctors cannot create or update patients.

## Validation

The API validates:

* Email format
* Unique doctor email
* Password minimum length
* Patient age greater than zero
* Patient phone number containing 10–15 digits
* Duplicate doctor-patient assignments

Invalid request data returns HTTP `422`.

Unauthorized requests return HTTP `401`.

Forbidden operations return HTTP `403`.

Missing resources return HTTP `404`.

## Pagination and Filtering

Doctor listing supports:

```text
GET /doctors?skip=0&limit=10
```

Doctor specialization filtering:

```text
GET /doctors?specialization=Cardiology
```

Patient listing supports:

```text
GET /patients?skip=0&limit=10
```

Patient name filtering:

```text
GET /patients?name=Rahul
```

## Testing

Run all tests with:

```bash
python -m pytest -v
```

The test suite covers:

* Root endpoint
* Health endpoint
* Swagger endpoint
* User registration
* User login
* Patient validation
* Authentication protection
* Role-based authorization

## Security Notes

* Passwords are stored as bcrypt hashes.
* Authentication uses JWT access tokens.
* The JWT secret is loaded from environment variables.
* `.env` is excluded from Git.
* Public registration creates doctor accounts only.
* Administrator accounts are created through the controlled `create_admin.py` script.

## Assumptions

* SQLite is used for simplicity and local development.
* Doctor accounts are linked to doctor profiles through `user_id`.
* A doctor can view only patients assigned to that doctor.
* Doctor deletion is a soft delete.
* Patient deletion is not included because it is not required by the assignment.
* Database migrations are not included; tables are created automatically when the application starts.

## License

This project was created as an assignment/project submission.
