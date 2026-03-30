# services/auth_services.py
import bcrypt

from database.user_dao import create_user, get_user_by_email
from database.patient_dao import create_patient


def register_patient(name, email, password, age, gender, phone, address):
    """Register a new patient: creates users row + patient profile row."""
    if get_user_by_email(email):
        return False, "Email already registered"

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    if not create_user(name, email, hashed, "patient"):
        return False, "Registration failed"

    user = get_user_by_email(email)
    if not user:
        return False, "Registration failed"
    if not create_patient(user[0], age, gender, phone, address):
        return False, "Failed to create patient profile"

    return True, "Registered successfully"


def register_doctor(name, email, password, department_id, experience_years, qualification):
    """Register a new doctor: creates users row + doctor profile row. Returns (bool, message)."""
    if get_user_by_email(email):
        return False, "Email already registered"

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    if not create_user(name, email, hashed, "doctor"):
        return False, "Failed to create account"

    user = get_user_by_email(email)
    if not user:
        return False, "Failed to create account"

    from database.doctor_dao import create_doctor
    if not create_doctor(user[0], department_id, experience_years, qualification):
        return False, "Failed to create doctor profile"

    return True, "Doctor added successfully"


def register_user(name, email, password, role):
    """Register admin/doctor user (no profile row — used internally)."""
    if get_user_by_email(email):
        return False

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return create_user(name, email, hashed, role)


def login_user(email, password):
    """Returns user tuple (user_id, name, email, password_hash, role) on success, None on failure."""
    user = get_user_by_email(email)
    if not user:
        return None

    if bcrypt.checkpw(password.encode("utf-8"), user[3].encode("utf-8")):
        return user
    return None
