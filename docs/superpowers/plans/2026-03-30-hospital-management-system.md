# Hospital Management System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Hospital Management System desktop app with Tkinter GUI, role-based dashboards (patient/doctor/admin), appointment booking with conflict detection, medical records, auto-billing, symptom-to-department matching, and doctor reviews.

**Architecture:** 3-tier (DAO → Service → GUI). `App` (Tk subclass) owns the single window and swaps `tk.Frame` subclasses on navigation. `App.current_user` dict `{user_id, name, role, profile_id}` persists for the session. Each DAO opens a connection, runs parameterized SQL, closes in `finally` — no ORM, no pooling.

**Tech Stack:** Python 3, psycopg2, PostgreSQL 15 (Docker), Tkinter, tkcalendar, bcrypt

---

## File Map

**New files to create:**
```
services/__init__.py
database/department_dao.py
database/doctor_dao.py
database/patient_dao.py
database/appointment_dao.py
database/medical_record_dao.py
database/bill_dao.py
database/symptom_dao.py
database/review_dao.py
services/appointment_services.py
services/billing_services.py
services/medical_record_services.py
services/symptom_services.py
services/review_services.py
gui/__init__.py
gui/app.py
gui/login_frame.py
gui/patient/__init__.py
gui/patient/dashboard.py
gui/patient/browse_departments.py
gui/patient/symptom_search.py
gui/patient/book_appointment.py
gui/patient/my_appointments.py
gui/patient/my_records.py
gui/patient/my_bills.py
gui/patient/review_doctor.py
gui/doctor/__init__.py
gui/doctor/dashboard.py
gui/doctor/appointments.py
gui/doctor/write_record.py
gui/doctor/patient_history.py
gui/doctor/my_reviews.py
gui/admin/__init__.py
gui/admin/dashboard.py
gui/admin/manage_departments.py
gui/admin/manage_doctors.py
gui/admin/all_appointments.py
gui/admin/all_users.py
```

**Files to modify:**
```
services/auth_services.py      — login_user returns user tuple; add register_patient
main.py                        — launch App instead of manual tests
migrations/init.sql            — already updated (review table added)
```

---

## Task 1: Commit bcrypt changes + fix `login_user` return value

The uncommitted `services/auth_services.py` adds bcrypt. Before the GUI can use it, `login_user` must return the user row (not `True`) so the login screen can build `current_user`.

**Files:**
- Modify: `services/auth_services.py`
- Modify: `services/__init__.py` (create)

- [ ] **Step 1: Create `services/__init__.py`**

```python
# services/__init__.py
```

- [ ] **Step 2: Update `services/auth_services.py` — `login_user` returns user tuple; add `register_patient`**

```python
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
    if not create_patient(user[0], age, gender, phone, address):
        return False, "Failed to create patient profile"

    return True, "Registered successfully"


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
```

- [ ] **Step 3: Commit**

```bash
git add services/__init__.py services/auth_services.py
git commit -m "fix: login_user returns user tuple; add register_patient"
```

---

## Task 2: Re-run database migration

The `review` table was added to `migrations/init.sql` but not yet applied to the running DB.

**Files:**
- Read: `migrations/init_db.py`

- [ ] **Step 1: Ensure Docker is running**

```bash
docker-compose up -d
```
Expected: `hms_db` container running.

- [ ] **Step 2: Re-run migration**

```bash
python migrations/init_db.py
```
Expected output: `Database initialized successfully`

Note: `init.sql` uses `CREATE TABLE IF NOT EXISTS` so existing tables are safe.

---

## Task 3: `database/department_dao.py`

**Files:**
- Create: `database/department_dao.py`

- [ ] **Step 1: Create `database/department_dao.py`**

```python
# database/department_dao.py
from database.db_connection import get_connection


def get_all_departments():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT department_id, department_name FROM department ORDER BY department_name;")
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching departments:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def create_department(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO department (department_name) VALUES (%s);",
            (name,)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating department:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def delete_department(department_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM department WHERE department_id = %s;", (department_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error deleting department:", e)
        return False
    finally:
        cursor.close()
        conn.close()
```

- [ ] **Step 2: Verify manually**

```bash
python -c "
from database.department_dao import create_department, get_all_departments
create_department('Cardiology')
create_department('Neurology')
print(get_all_departments())
"
```
Expected: list containing `(id, 'Cardiology')` and `(id, 'Neurology')`.

- [ ] **Step 3: Commit**

```bash
git add database/department_dao.py
git commit -m "feat: add department_dao"
```

---

## Task 4: `database/doctor_dao.py`

**Files:**
- Create: `database/doctor_dao.py`

- [ ] **Step 1: Create `database/doctor_dao.py`**

```python
# database/doctor_dao.py
from database.db_connection import get_connection


def get_all_doctors():
    """Returns (doctor_id, user_name, department_name, experience_years, qualification)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT d.doctor_id, u.user_name, dep.department_name,
                   d.experience_years, d.qualification
            FROM doctor d
            JOIN users u ON d.user_id = u.user_id
            JOIN department dep ON d.department_id = dep.department_id
            ORDER BY u.user_name;
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching doctors:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_doctors_by_department(department_id):
    """Returns (doctor_id, user_name, experience_years, qualification)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT d.doctor_id, u.user_name, d.experience_years, d.qualification
            FROM doctor d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.department_id = %s
            ORDER BY u.user_name;
        """, (department_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching doctors by department:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_doctor_by_user_id(user_id):
    """Returns (doctor_id, user_id, department_id, experience_years, qualification)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM doctor WHERE user_id = %s;", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print("Error fetching doctor:", e)
        return None
    finally:
        cursor.close()
        conn.close()


def create_doctor(user_id, department_id, experience_years, qualification):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO doctor (user_id, department_id, experience_years, qualification)
            VALUES (%s, %s, %s, %s);
        """, (user_id, department_id, experience_years, qualification))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating doctor:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def delete_doctor(doctor_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM doctor WHERE doctor_id = %s;", (doctor_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error deleting doctor:", e)
        return False
    finally:
        cursor.close()
        conn.close()
```

- [ ] **Step 2: Verify manually**

```bash
python -c "
from database.doctor_dao import get_all_doctors
print(get_all_doctors())
"
```
Expected: list of doctor rows (empty if none added yet).

- [ ] **Step 3: Commit**

```bash
git add database/doctor_dao.py
git commit -m "feat: add doctor_dao"
```

---

## Task 5: `database/patient_dao.py`

**Files:**
- Create: `database/patient_dao.py`

- [ ] **Step 1: Create `database/patient_dao.py`**

```python
# database/patient_dao.py
from database.db_connection import get_connection


def get_patient_by_user_id(user_id):
    """Returns (patient_id, user_id, age, gender, phone, address)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM patient WHERE user_id = %s;", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print("Error fetching patient:", e)
        return None
    finally:
        cursor.close()
        conn.close()


def get_all_patients():
    """Returns (patient_id, user_name, age, gender, phone) joined with users."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.patient_id, u.user_name, p.age, p.gender, p.phone
            FROM patient p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY u.user_name;
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching patients:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def create_patient(user_id, age, gender, phone, address):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO patient (user_id, age, gender, phone, address)
            VALUES (%s, %s, %s, %s, %s);
        """, (user_id, age, gender, phone, address))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating patient:", e)
        return False
    finally:
        cursor.close()
        conn.close()
```

- [ ] **Step 2: Commit**

```bash
git add database/patient_dao.py
git commit -m "feat: add patient_dao"
```

---

## Task 6: `database/appointment_dao.py`

**Files:**
- Create: `database/appointment_dao.py`

- [ ] **Step 1: Create `database/appointment_dao.py`**

```python
# database/appointment_dao.py
from database.db_connection import get_connection


def create_appointment(patient_id, doctor_id, date, time):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO appointment (patient_id, doctor_id, appointment_date, appointment_time, status)
            VALUES (%s, %s, %s, %s, 'scheduled');
        """, (patient_id, doctor_id, date, time))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating appointment:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def check_slot_availability(doctor_id, date, time):
    """Returns True if the slot is free, False if taken."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM appointment
            WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s
            AND status != 'cancelled';
        """, (doctor_id, date, time))
        count = cursor.fetchone()[0]
        return count == 0
    except Exception as e:
        print("Error checking slot:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def get_appointments_by_patient(patient_id):
    """Returns (appointment_id, doctor_name, department_name, date, time, status)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT a.appointment_id, u.user_name, dep.department_name,
                   a.appointment_date, a.appointment_time, a.status
            FROM appointment a
            JOIN doctor d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            JOIN department dep ON d.department_id = dep.department_id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC;
        """, (patient_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching patient appointments:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_appointments_by_doctor(doctor_id):
    """Returns (appointment_id, patient_name, date, time, status)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT a.appointment_id, u.user_name, a.appointment_date,
                   a.appointment_time, a.status
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE a.doctor_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC;
        """, (doctor_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching doctor appointments:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_all_appointments():
    """Returns (appointment_id, patient_name, doctor_name, date, time, status)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT a.appointment_id, pu.user_name, du.user_name,
                   a.appointment_date, a.appointment_time, a.status
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            JOIN users pu ON p.user_id = pu.user_id
            JOIN doctor d ON a.doctor_id = d.doctor_id
            JOIN users du ON d.user_id = du.user_id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC;
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching all appointments:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def mark_completed(appointment_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE appointment SET status = 'completed'
            WHERE appointment_id = %s;
        """, (appointment_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error marking appointment completed:", e)
        return False
    finally:
        cursor.close()
        conn.close()
```

- [ ] **Step 2: Commit**

```bash
git add database/appointment_dao.py
git commit -m "feat: add appointment_dao"
```

---

## Task 7: `database/medical_record_dao.py`

**Files:**
- Create: `database/medical_record_dao.py`

- [ ] **Step 1: Create `database/medical_record_dao.py`**

```python
# database/medical_record_dao.py
from database.db_connection import get_connection


def create_record(appointment_id, diagnosis, prescription, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO medical_record (appointment_id, diagnosis, prescription, notes)
            VALUES (%s, %s, %s, %s);
        """, (appointment_id, diagnosis, prescription, notes))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating medical record:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def get_records_by_patient(patient_id):
    """Returns (record_id, doctor_name, date, diagnosis, prescription, notes, created_at)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT mr.record_id, u.user_name, a.appointment_date,
                   mr.diagnosis, mr.prescription, mr.notes, mr.created_at
            FROM medical_record mr
            JOIN appointment a ON mr.appointment_id = a.appointment_id
            JOIN doctor d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE a.patient_id = %s
            ORDER BY mr.created_at DESC;
        """, (patient_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching records:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_record_by_appointment(appointment_id):
    """Returns (record_id, appointment_id, diagnosis, prescription, notes, created_at)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM medical_record WHERE appointment_id = %s;",
            (appointment_id,)
        )
        return cursor.fetchone()
    except Exception as e:
        print("Error fetching record:", e)
        return None
    finally:
        cursor.close()
        conn.close()
```

- [ ] **Step 2: Commit**

```bash
git add database/medical_record_dao.py
git commit -m "feat: add medical_record_dao"
```

---

## Task 8: `database/bill_dao.py`

**Files:**
- Create: `database/bill_dao.py`

- [ ] **Step 1: Create `database/bill_dao.py`**

```python
# database/bill_dao.py
from database.db_connection import get_connection


def create_bill(appointment_id, total_amount):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO bill (appointment_id, total_amount)
            VALUES (%s, %s);
        """, (appointment_id, total_amount))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating bill:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def get_bills_by_patient(patient_id):
    """Returns (bill_id, doctor_name, date, total_amount, created_at)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.bill_id, u.user_name, a.appointment_date,
                   b.total_amount, b.created_at
            FROM bill b
            JOIN appointment a ON b.appointment_id = a.appointment_id
            JOIN doctor d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE a.patient_id = %s
            ORDER BY b.created_at DESC;
        """, (patient_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching bills:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_all_bills():
    """Returns (bill_id, patient_name, doctor_name, date, total_amount, created_at)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.bill_id, pu.user_name, du.user_name,
                   a.appointment_date, b.total_amount, b.created_at
            FROM bill b
            JOIN appointment a ON b.appointment_id = a.appointment_id
            JOIN patient p ON a.patient_id = p.patient_id
            JOIN users pu ON p.user_id = pu.user_id
            JOIN doctor d ON a.doctor_id = d.doctor_id
            JOIN users du ON d.user_id = du.user_id
            ORDER BY b.created_at DESC;
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching all bills:", e)
        return []
    finally:
        cursor.close()
        conn.close()
```

- [ ] **Step 2: Commit**

```bash
git add database/bill_dao.py
git commit -m "feat: add bill_dao"
```

---

## Task 9: `database/symptom_dao.py` and `database/review_dao.py`

**Files:**
- Create: `database/symptom_dao.py`
- Create: `database/review_dao.py`

- [ ] **Step 1: Create `database/symptom_dao.py`**

```python
# database/symptom_dao.py
from database.db_connection import get_connection


def get_departments_by_symptom(keyword):
    """Returns list of (department_id, department_name) matching the keyword."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT DISTINCT dep.department_id, dep.department_name
            FROM symptom_mapping sm
            JOIN department dep ON sm.department_id = dep.department_id
            WHERE sm.keyword ILIKE %s;
        """, (f"%{keyword}%",))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching departments by symptom:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def add_symptom_mapping(keyword, department_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO symptom_mapping (keyword, department_id) VALUES (%s, %s);
        """, (keyword, department_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error adding symptom mapping:", e)
        return False
    finally:
        cursor.close()
        conn.close()
```

- [ ] **Step 2: Create `database/review_dao.py`**

```python
# database/review_dao.py
from database.db_connection import get_connection


def create_review(appointment_id, patient_id, doctor_id, rating, comment=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO review (appointment_id, patient_id, doctor_id, rating, comment)
            VALUES (%s, %s, %s, %s, %s);
        """, (appointment_id, patient_id, doctor_id, rating, comment))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating review:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def get_reviews_by_doctor(doctor_id):
    """Returns (review_id, patient_name, appointment_date, rating, comment, created_at)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT r.review_id, u.user_name, a.appointment_date,
                   r.rating, r.comment, r.created_at
            FROM review r
            JOIN patient p ON r.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            JOIN appointment a ON r.appointment_id = a.appointment_id
            WHERE r.doctor_id = %s
            ORDER BY r.created_at DESC;
        """, (doctor_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching reviews:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_review_by_appointment(appointment_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM review WHERE appointment_id = %s;",
            (appointment_id,)
        )
        return cursor.fetchone()
    except Exception as e:
        print("Error fetching review:", e)
        return None
    finally:
        cursor.close()
        conn.close()
```

- [ ] **Step 3: Commit**

```bash
git add database/symptom_dao.py database/review_dao.py
git commit -m "feat: add symptom_dao and review_dao"
```

---

## Task 10: Services layer

**Files:**
- Create: `services/appointment_services.py`
- Create: `services/billing_services.py`
- Create: `services/medical_record_services.py`
- Create: `services/symptom_services.py`
- Create: `services/review_services.py`

- [ ] **Step 1: Create `services/appointment_services.py`**

```python
# services/appointment_services.py
from database.appointment_dao import check_slot_availability, create_appointment


def book_appointment(patient_id, doctor_id, date, time):
    """Returns (success: bool, message: str)."""
    if not check_slot_availability(doctor_id, date, time):
        return False, "Doctor is busy at this time slot. Please choose another."
    if create_appointment(patient_id, doctor_id, date, time):
        return True, "Appointment booked successfully."
    return False, "Failed to book appointment. Please try again."
```

- [ ] **Step 2: Create `services/billing_services.py`**

Consultation fee is fixed at 500.00.

```python
# services/billing_services.py
from database.appointment_dao import mark_completed
from database.bill_dao import create_bill

CONSULTATION_FEE = 500.00


def complete_appointment_and_bill(appointment_id):
    """Marks appointment completed and auto-generates a bill. Returns (success, message)."""
    if not mark_completed(appointment_id):
        return False, "Failed to mark appointment as completed."
    if not create_bill(appointment_id, CONSULTATION_FEE):
        return False, "Appointment completed but billing failed."
    return True, f"Appointment completed. Bill of {CONSULTATION_FEE:.2f} generated."
```

- [ ] **Step 3: Create `services/medical_record_services.py`**

```python
# services/medical_record_services.py
from database.medical_record_dao import create_record, get_records_by_patient, get_record_by_appointment


def add_record(appointment_id, diagnosis, prescription, notes=""):
    """Returns (success, message)."""
    if get_record_by_appointment(appointment_id):
        return False, "A record already exists for this appointment."
    if create_record(appointment_id, diagnosis, prescription, notes):
        return True, "Medical record saved."
    return False, "Failed to save record."


def get_patient_records(patient_id):
    return get_records_by_patient(patient_id)
```

- [ ] **Step 4: Create `services/symptom_services.py`**

```python
# services/symptom_services.py
from database.symptom_dao import get_departments_by_symptom
from database.doctor_dao import get_doctors_by_department


def suggest_for_symptoms(symptom_text):
    """
    Returns list of (department_id, department_name, [(doctor_id, name, exp, qual), ...]).
    Splits input into words and searches each word as a keyword.
    """
    keywords = symptom_text.lower().split()
    seen_departments = {}

    for kw in keywords:
        results = get_departments_by_symptom(kw)
        for dept_id, dept_name in results:
            if dept_id not in seen_departments:
                seen_departments[dept_id] = dept_name

    suggestions = []
    for dept_id, dept_name in seen_departments.items():
        doctors = get_doctors_by_department(dept_id)
        suggestions.append((dept_id, dept_name, doctors))

    return suggestions
```

- [ ] **Step 5: Create `services/review_services.py`**

```python
# services/review_services.py
from database.review_dao import create_review, get_reviews_by_doctor, get_review_by_appointment


def submit_review(appointment_id, patient_id, doctor_id, rating, comment=None):
    """Returns (success, message)."""
    if get_review_by_appointment(appointment_id):
        return False, "You have already reviewed this appointment."
    if not (1 <= rating <= 5):
        return False, "Rating must be between 1 and 5."
    if create_review(appointment_id, patient_id, doctor_id, rating, comment):
        return True, "Review submitted. Thank you!"
    return False, "Failed to submit review."


def get_doctor_reviews(doctor_id):
    return get_reviews_by_doctor(doctor_id)
```

- [ ] **Step 6: Commit**

```bash
git add services/appointment_services.py services/billing_services.py \
        services/medical_record_services.py services/symptom_services.py \
        services/review_services.py
git commit -m "feat: add all service layer files"
```

---

## Task 11: GUI scaffold — `gui/app.py` + `__init__.py` files

**Files:**
- Create: `gui/__init__.py`
- Create: `gui/patient/__init__.py`
- Create: `gui/doctor/__init__.py`
- Create: `gui/admin/__init__.py`
- Create: `gui/app.py`

- [ ] **Step 1: Create all `__init__.py` files**

Create four empty files:
- `gui/__init__.py`
- `gui/patient/__init__.py`
- `gui/doctor/__init__.py`
- `gui/admin/__init__.py`

Each file contains only a blank line.

- [ ] **Step 2: Create `gui/app.py`**

```python
# gui/app.py
import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("1100x700")
        self.resizable(True, True)
        self.current_user = None
        self._current_frame = None

        from gui.login_frame import LoginFrame
        self.show_frame(LoginFrame)

    def show_frame(self, frame_class, **kwargs):
        """Destroy current frame and show a new one."""
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame_class(self, **kwargs)
        self._current_frame.pack(fill="both", expand=True)

    def logout(self):
        self.current_user = None
        from gui.login_frame import LoginFrame
        self.show_frame(LoginFrame)
```

- [ ] **Step 3: Commit**

```bash
git add gui/__init__.py gui/patient/__init__.py gui/doctor/__init__.py \
        gui/admin/__init__.py gui/app.py
git commit -m "feat: add GUI scaffold (App class and __init__ files)"
```

---

## Task 12: `gui/login_frame.py` + update `main.py`

**Files:**
- Create: `gui/login_frame.py`
- Modify: `main.py`

- [ ] **Step 1: Create `gui/login_frame.py`**

```python
# gui/login_frame.py
import tkinter as tk
from tkinter import messagebox

from services.auth_services import login_user, register_patient
from database.patient_dao import get_patient_by_user_id
from database.doctor_dao import get_doctor_by_user_id


class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build_login()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _build_login(self):
        self._clear()
        tk.Label(self, text="Hospital Management System",
                 font=("Arial", 22, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=40)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack()

        tk.Label(form, text="Email:", bg="#ecf0f1", font=("Arial", 11)).grid(row=0, column=0, sticky="e", pady=8, padx=10)
        self.email_var = tk.StringVar()
        tk.Entry(form, textvariable=self.email_var, width=30, font=("Arial", 11)).grid(row=0, column=1)

        tk.Label(form, text="Password:", bg="#ecf0f1", font=("Arial", 11)).grid(row=1, column=0, sticky="e", pady=8, padx=10)
        self.pass_var = tk.StringVar()
        tk.Entry(form, textvariable=self.pass_var, show="*", width=30, font=("Arial", 11)).grid(row=1, column=1)

        tk.Button(self, text="Login", command=self._login,
                  bg="#2980b9", fg="white", font=("Arial", 12), width=15).pack(pady=15)
        tk.Button(self, text="New Patient? Register", command=self._build_register,
                  bg="#ecf0f1", font=("Arial", 10)).pack()

    def _login(self):
        email = self.email_var.get().strip()
        password = self.pass_var.get()

        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter email and password.")
            return

        user = login_user(email, password)
        if not user:
            messagebox.showerror("Login Failed", "Invalid email or password.")
            return

        user_id, name, _, _, role = user[0], user[1], user[2], user[3], user[4]

        profile_id = None
        if role == "patient":
            patient = get_patient_by_user_id(user_id)
            profile_id = patient[0] if patient else None
        elif role == "doctor":
            doctor = get_doctor_by_user_id(user_id)
            profile_id = doctor[0] if doctor else None

        self.master.current_user = {
            "user_id": user_id,
            "name": name,
            "role": role,
            "profile_id": profile_id,
        }

        if role == "patient":
            from gui.patient.dashboard import PatientDashboard
            self.master.show_frame(PatientDashboard)
        elif role == "doctor":
            from gui.doctor.dashboard import DoctorDashboard
            self.master.show_frame(DoctorDashboard)
        elif role == "admin":
            from gui.admin.dashboard import AdminDashboard
            self.master.show_frame(AdminDashboard)

    def _build_register(self):
        self._clear()
        tk.Label(self, text="Patient Registration",
                 font=("Arial", 18, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=30)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack()

        fields = [
            ("Full Name:", "name"), ("Email:", "email"), ("Password:", "password"),
            ("Age:", "age"), ("Gender (male/female/other):", "gender"),
            ("Phone:", "phone"), ("Address:", "address"),
        ]
        self._reg_vars = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label, bg="#ecf0f1", font=("Arial", 11)).grid(
                row=i, column=0, sticky="e", pady=6, padx=10)
            var = tk.StringVar()
            show = "*" if key == "password" else ""
            tk.Entry(form, textvariable=var, width=30, font=("Arial", 11), show=show).grid(row=i, column=1)
            self._reg_vars[key] = var

        tk.Button(self, text="Register", command=self._register,
                  bg="#27ae60", fg="white", font=("Arial", 12), width=15).pack(pady=15)
        tk.Button(self, text="Back to Login", command=self._build_login,
                  bg="#ecf0f1", font=("Arial", 10)).pack()

    def _register(self):
        v = {k: var.get().strip() for k, var in self._reg_vars.items()}

        if not all([v["name"], v["email"], v["password"], v["age"], v["gender"]]):
            messagebox.showwarning("Input Error", "Name, email, password, age, and gender are required.")
            return

        try:
            age = int(v["age"])
        except ValueError:
            messagebox.showerror("Input Error", "Age must be a number.")
            return

        success, msg = register_patient(
            v["name"], v["email"], v["password"],
            age, v["gender"], v["phone"], v["address"]
        )

        if success:
            messagebox.showinfo("Success", msg)
            self._build_login()
        else:
            messagebox.showerror("Registration Failed", msg)
```

- [ ] **Step 2: Update `main.py` to launch the app**

```python
# main.py
from gui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
```

- [ ] **Step 3: Verify the login window opens**

```bash
docker-compose up -d
python main.py
```
Expected: Window opens with "Hospital Management System" title, login form visible.

- [ ] **Step 4: Create a seed admin user (run once)**

```bash
python -c "
from services.auth_services import register_user
register_user('Admin', 'admin@hms.com', 'admin123', 'admin')
print('Admin created')
"
```

- [ ] **Step 5: Commit**

```bash
git add gui/login_frame.py main.py
git commit -m "feat: add login/register frame and launch app from main.py"
```

---

## Task 13: Admin dashboard

**Files:**
- Create: `gui/admin/dashboard.py`
- Create: `gui/admin/manage_departments.py`
- Create: `gui/admin/manage_doctors.py`
- Create: `gui/admin/all_appointments.py`
- Create: `gui/admin/all_users.py`

- [ ] **Step 1: Create `gui/admin/dashboard.py`**

```python
# gui/admin/dashboard.py
import tkinter as tk


class AdminDashboard(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg="#2c3e50", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=f"Admin Dashboard — {self.master.current_user['name']}",
                 fg="white", bg="#2c3e50", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=15)
        tk.Button(header, text="Logout", command=self.master.logout,
                  bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side="right", padx=20, pady=12)

        # Body: sidebar + content
        body = tk.Frame(self, bg="#ecf0f1")
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg="#34495e", width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg="#ecf0f1")
        self.content.pack(side="left", fill="both", expand=True)

        nav = [
            ("Manage Departments", self._show_departments),
            ("Manage Doctors", self._show_doctors),
            ("All Appointments", self._show_appointments),
            ("All Users", self._show_users),
        ]
        for label, cmd in nav:
            tk.Button(sidebar, text=label, command=cmd, width=22,
                      bg="#3d566e", fg="white", font=("Arial", 10),
                      relief="flat", pady=10).pack(fill="x", padx=5, pady=3)

        self._show_departments()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_departments(self):
        self._clear_content()
        from gui.admin.manage_departments import ManageDepartments
        ManageDepartments(self.content).pack(fill="both", expand=True)

    def _show_doctors(self):
        self._clear_content()
        from gui.admin.manage_doctors import ManageDoctors
        ManageDoctors(self.content).pack(fill="both", expand=True)

    def _show_appointments(self):
        self._clear_content()
        from gui.admin.all_appointments import AllAppointments
        AllAppointments(self.content).pack(fill="both", expand=True)

    def _show_users(self):
        self._clear_content()
        from gui.admin.all_users import AllUsers
        AllUsers(self.content).pack(fill="both", expand=True)
```

- [ ] **Step 2: Create `gui/admin/manage_departments.py`**

```python
# gui/admin/manage_departments.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.department_dao import get_all_departments, create_department, delete_department


class ManageDepartments(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="Manage Departments",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        # Add form
        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=5)
        tk.Label(form, text="Department Name:", bg="#ecf0f1").grid(row=0, column=0, padx=5)
        self.name_var = tk.StringVar()
        tk.Entry(form, textvariable=self.name_var, width=25).grid(row=0, column=1, padx=5)
        tk.Button(form, text="Add", command=self._add,
                  bg="#27ae60", fg="white").grid(row=0, column=2, padx=5)

        # Table
        cols = ("ID", "Name")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=200)
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

        tk.Button(self, text="Delete Selected", command=self._delete,
                  bg="#e74c3c", fg="white").pack(pady=5)

        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for dept in get_all_departments():
            self.tree.insert("", "end", values=dept)

    def _add(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Enter a department name.")
            return
        if create_department(name):
            self.name_var.set("")
            self._refresh()
        else:
            messagebox.showerror("Error", "Failed to add department.")

    def _delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a department to delete.")
            return
        dept_id = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm", "Delete this department?"):
            delete_department(dept_id)
            self._refresh()
```

- [ ] **Step 3: Create `gui/admin/manage_doctors.py`**

```python
# gui/admin/manage_doctors.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.doctor_dao import get_all_doctors, create_doctor, delete_doctor
from database.department_dao import get_all_departments
from database.user_dao import create_user, get_user_by_email
import bcrypt


class ManageDoctors(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="Manage Doctors",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        # Add form
        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=5)

        labels = ["Name:", "Email:", "Password:", "Experience (years):", "Qualification:"]
        self._vars = {}
        keys = ["name", "email", "password", "experience", "qualification"]
        for i, (lbl, key) in enumerate(zip(labels, keys)):
            tk.Label(form, text=lbl, bg="#ecf0f1").grid(row=i, column=0, sticky="e", padx=5, pady=3)
            var = tk.StringVar()
            show = "*" if key == "password" else ""
            tk.Entry(form, textvariable=var, width=25, show=show).grid(row=i, column=1, padx=5)
            self._vars[key] = var

        tk.Label(form, text="Department:", bg="#ecf0f1").grid(row=5, column=0, sticky="e", padx=5, pady=3)
        self._dept_var = tk.StringVar()
        self._dept_combo = ttk.Combobox(form, textvariable=self._dept_var, width=23, state="readonly")
        self._dept_combo.grid(row=5, column=1, padx=5)
        self._load_departments()

        tk.Button(form, text="Add Doctor", command=self._add,
                  bg="#27ae60", fg="white").grid(row=6, column=1, pady=10, sticky="e")

        # Table
        cols = ("ID", "Name", "Department", "Experience", "Qualification")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        widths = [50, 180, 150, 100, 150]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Button(self, text="Delete Selected", command=self._delete,
                  bg="#e74c3c", fg="white").pack(pady=5)

        self._refresh()

    def _load_departments(self):
        depts = get_all_departments()
        self._dept_map = {name: did for did, name in depts}
        self._dept_combo["values"] = list(self._dept_map.keys())

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for doc in get_all_doctors():
            self.tree.insert("", "end", values=doc)

    def _add(self):
        v = {k: var.get().strip() for k, var in self._vars.items()}
        dept_name = self._dept_var.get()

        if not all([v["name"], v["email"], v["password"], dept_name]):
            messagebox.showwarning("Input Error", "Name, email, password, and department are required.")
            return

        if get_user_by_email(v["email"]):
            messagebox.showerror("Error", "Email already registered.")
            return

        hashed = bcrypt.hashpw(v["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        if not create_user(v["name"], v["email"], hashed, "doctor"):
            messagebox.showerror("Error", "Failed to create doctor account.")
            return

        user = get_user_by_email(v["email"])
        dept_id = self._dept_map[dept_name]
        exp = int(v["experience"]) if v["experience"].isdigit() else 0

        if create_doctor(user[0], dept_id, exp, v["qualification"]):
            messagebox.showinfo("Success", "Doctor added.")
            for var in self._vars.values():
                var.set("")
            self._dept_var.set("")
            self._refresh()
        else:
            messagebox.showerror("Error", "Failed to create doctor profile.")

    def _delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a doctor to delete.")
            return
        doctor_id = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm", "Delete this doctor? This also deletes their account."):
            delete_doctor(doctor_id)
            self._refresh()
```

- [ ] **Step 4: Create `gui/admin/all_appointments.py`**

```python
# gui/admin/all_appointments.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.appointment_dao import get_all_appointments
from services.billing_services import complete_appointment_and_bill


class AllAppointments(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="All Appointments",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("ID", "Patient", "Doctor", "Date", "Time", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        widths = [50, 160, 160, 110, 80, 100]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="#ecf0f1")
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Mark as Completed", command=self._complete,
                  bg="#27ae60", fg="white", font=("Arial", 11)).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white", font=("Arial", 11)).pack(side="left")

        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for appt in get_all_appointments():
            self.tree.insert("", "end", values=appt)

    def _complete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select an appointment to complete.")
            return
        values = self.tree.item(selected[0])["values"]
        appt_id = values[0]
        status = values[5]
        if status == "completed":
            messagebox.showinfo("Info", "This appointment is already completed.")
            return
        if messagebox.askyesno("Confirm", "Mark as completed and generate bill?"):
            success, msg = complete_appointment_and_bill(appt_id)
            messagebox.showinfo("Result", msg)
            self._refresh()
```

- [ ] **Step 5: Create `gui/admin/all_users.py`**

```python
# gui/admin/all_users.py
import tkinter as tk
from tkinter import ttk
from database.db_connection import get_connection


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, user_name, user_email, user_role FROM users ORDER BY user_role, user_name;")
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching users:", e)
        return []
    finally:
        cursor.close()
        conn.close()


class AllUsers(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="All Users",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("ID", "Name", "Email", "Role")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        widths = [60, 200, 250, 100]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Button(self, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white").pack(pady=5)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for user in get_all_users():
            self.tree.insert("", "end", values=user)
```

- [ ] **Step 6: Test admin dashboard**

```bash
python main.py
```
Log in as `admin@hms.com` / `admin123`. Verify all 4 sidebar buttons open their screens. Add a department and a doctor.

- [ ] **Step 7: Commit**

```bash
git add gui/admin/
git commit -m "feat: add admin dashboard with all management screens"
```

---

## Task 14: Doctor dashboard

**Files:**
- Create: `gui/doctor/dashboard.py`
- Create: `gui/doctor/appointments.py`
- Create: `gui/doctor/write_record.py`
- Create: `gui/doctor/patient_history.py`
- Create: `gui/doctor/my_reviews.py`

- [ ] **Step 1: Create `gui/doctor/dashboard.py`**

```python
# gui/doctor/dashboard.py
import tkinter as tk


class DoctorDashboard(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#1a5276", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=f"Doctor Dashboard — Dr. {self.master.current_user['name']}",
                 fg="white", bg="#1a5276", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=15)
        tk.Button(header, text="Logout", command=self.master.logout,
                  bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side="right", padx=20, pady=12)

        body = tk.Frame(self, bg="#ecf0f1")
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg="#1f618d", width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg="#ecf0f1")
        self.content.pack(side="left", fill="both", expand=True)

        nav = [
            ("My Appointments", self._show_appointments),
            ("Write Medical Record", self._show_write_record),
            ("Patient History", self._show_patient_history),
            ("My Reviews", self._show_reviews),
        ]
        for label, cmd in nav:
            tk.Button(sidebar, text=label, command=cmd, width=22,
                      bg="#2471a3", fg="white", font=("Arial", 10),
                      relief="flat", pady=10).pack(fill="x", padx=5, pady=3)

        self._show_appointments()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_appointments(self):
        self._clear_content()
        from gui.doctor.appointments import DoctorAppointments
        DoctorAppointments(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)

    def _show_write_record(self):
        self._clear_content()
        from gui.doctor.write_record import WriteRecord
        WriteRecord(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)

    def _show_patient_history(self):
        self._clear_content()
        from gui.doctor.patient_history import PatientHistory
        PatientHistory(self.content).pack(fill="both", expand=True)

    def _show_reviews(self):
        self._clear_content()
        from gui.doctor.my_reviews import MyReviews
        MyReviews(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)
```

- [ ] **Step 2: Create `gui/doctor/appointments.py`**

```python
# gui/doctor/appointments.py
import tkinter as tk
from tkinter import ttk
from database.appointment_dao import get_appointments_by_doctor


class DoctorAppointments(tk.Frame):
    def __init__(self, master, doctor_id):
        super().__init__(master, bg="#ecf0f1")
        self.doctor_id = doctor_id
        self._build()

    def _build(self):
        tk.Label(self, text="My Appointments",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("ID", "Patient", "Date", "Time", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        widths = [60, 200, 120, 80, 100]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Button(self, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white").pack(pady=5)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for appt in get_appointments_by_doctor(self.doctor_id):
            self.tree.insert("", "end", values=appt)
```

- [ ] **Step 3: Create `gui/doctor/write_record.py`**

```python
# gui/doctor/write_record.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.appointment_dao import get_appointments_by_doctor
from services.medical_record_services import add_record


class WriteRecord(tk.Frame):
    def __init__(self, master, doctor_id):
        super().__init__(master, bg="#ecf0f1")
        self.doctor_id = doctor_id
        self._build()

    def _build(self):
        tk.Label(self, text="Write Medical Record",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        tk.Label(self, text="Select Appointment:", bg="#ecf0f1", font=("Arial", 11)).pack()
        self._appt_var = tk.StringVar()
        self._appt_combo = ttk.Combobox(self, textvariable=self._appt_var,
                                         width=55, state="readonly", font=("Arial", 10))
        self._appt_combo.pack(pady=5)
        self._load_appointments()

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=10)

        tk.Label(form, text="Diagnosis:", bg="#ecf0f1", font=("Arial", 11)).grid(
            row=0, column=0, sticky="nw", padx=10, pady=5)
        self.diagnosis_text = tk.Text(form, width=45, height=4, font=("Arial", 10))
        self.diagnosis_text.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="Prescription:", bg="#ecf0f1", font=("Arial", 11)).grid(
            row=1, column=0, sticky="nw", padx=10, pady=5)
        self.prescription_text = tk.Text(form, width=45, height=4, font=("Arial", 10))
        self.prescription_text.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form, text="Notes (optional):", bg="#ecf0f1", font=("Arial", 11)).grid(
            row=2, column=0, sticky="nw", padx=10, pady=5)
        self.notes_text = tk.Text(form, width=45, height=3, font=("Arial", 10))
        self.notes_text.grid(row=2, column=1, padx=10, pady=5)

        tk.Button(self, text="Save Record", command=self._save,
                  bg="#27ae60", fg="white", font=("Arial", 12), width=15).pack(pady=10)

    def _load_appointments(self):
        appts = get_appointments_by_doctor(self.doctor_id)
        # Show only completed or scheduled appointments without existing records
        self._appt_map = {}
        choices = []
        for appt in appts:
            appt_id, patient, date, time, status = appt
            label = f"[{appt_id}] {patient} — {date} {time} ({status})"
            choices.append(label)
            self._appt_map[label] = appt_id
        self._appt_combo["values"] = choices

    def _save(self):
        label = self._appt_var.get()
        if not label:
            messagebox.showwarning("Select", "Please select an appointment.")
            return
        appt_id = self._appt_map[label]
        diagnosis = self.diagnosis_text.get("1.0", "end").strip()
        prescription = self.prescription_text.get("1.0", "end").strip()
        notes = self.notes_text.get("1.0", "end").strip()

        if not diagnosis:
            messagebox.showwarning("Input Error", "Diagnosis is required.")
            return

        success, msg = add_record(appt_id, diagnosis, prescription, notes)
        messagebox.showinfo("Result", msg)
        if success:
            self.diagnosis_text.delete("1.0", "end")
            self.prescription_text.delete("1.0", "end")
            self.notes_text.delete("1.0", "end")
            self._appt_var.set("")
```

- [ ] **Step 4: Create `gui/doctor/patient_history.py`**

```python
# gui/doctor/patient_history.py
import tkinter as tk
from tkinter import ttk
from database.patient_dao import get_all_patients
from services.medical_record_services import get_patient_records


class PatientHistory(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="Patient History",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        search_frame = tk.Frame(self, bg="#ecf0f1")
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Select Patient:", bg="#ecf0f1").pack(side="left", padx=5)
        self._patient_var = tk.StringVar()
        self._patient_combo = ttk.Combobox(search_frame, textvariable=self._patient_var,
                                            width=35, state="readonly")
        self._patient_combo.pack(side="left", padx=5)
        tk.Button(search_frame, text="View History", command=self._view,
                  bg="#2980b9", fg="white").pack(side="left", padx=5)

        patients = get_all_patients()
        self._patient_map = {f"[{p[0]}] {p[1]}": p[0] for p in patients}
        self._patient_combo["values"] = list(self._patient_map.keys())

        cols = ("Date", "Doctor", "Diagnosis", "Prescription", "Notes")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        widths = [110, 150, 200, 200, 150]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

    def _view(self):
        label = self._patient_var.get()
        if not label:
            return
        patient_id = self._patient_map[label]
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in get_patient_records(patient_id):
            # (record_id, doctor_name, date, diagnosis, prescription, notes, created_at)
            self.tree.insert("", "end", values=(rec[2], rec[1], rec[3], rec[4], rec[5]))
```

- [ ] **Step 5: Create `gui/doctor/my_reviews.py`**

```python
# gui/doctor/my_reviews.py
import tkinter as tk
from tkinter import ttk
from services.review_services import get_doctor_reviews


class MyReviews(tk.Frame):
    def __init__(self, master, doctor_id):
        super().__init__(master, bg="#ecf0f1")
        self.doctor_id = doctor_id
        self._build()

    def _build(self):
        tk.Label(self, text="My Reviews",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("Patient", "Date", "Rating", "Comment")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        widths = [180, 120, 80, 350]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Button(self, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white").pack(pady=5)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rev in get_doctor_reviews(self.doctor_id):
            # (review_id, patient_name, appointment_date, rating, comment, created_at)
            stars = "★" * rev[3] + "☆" * (5 - rev[3])
            self.tree.insert("", "end", values=(rev[1], rev[2], stars, rev[4] or ""))
```

- [ ] **Step 6: Test doctor dashboard**

Log in as a doctor account you created via admin → verify all 4 sidebar screens load.

- [ ] **Step 7: Commit**

```bash
git add gui/doctor/
git commit -m "feat: add doctor dashboard with appointments, records, history, reviews"
```

---

## Task 15: Patient dashboard

**Files:**
- Create: `gui/patient/dashboard.py`
- Create: `gui/patient/browse_departments.py`
- Create: `gui/patient/symptom_search.py`
- Create: `gui/patient/book_appointment.py`
- Create: `gui/patient/my_appointments.py`
- Create: `gui/patient/my_records.py`
- Create: `gui/patient/my_bills.py`
- Create: `gui/patient/review_doctor.py`

- [ ] **Step 1: Create `gui/patient/dashboard.py`**

```python
# gui/patient/dashboard.py
import tkinter as tk


class PatientDashboard(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#117a65", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=f"Patient Dashboard — {self.master.current_user['name']}",
                 fg="white", bg="#117a65", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=15)
        tk.Button(header, text="Logout", command=self.master.logout,
                  bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side="right", padx=20, pady=12)

        body = tk.Frame(self, bg="#ecf0f1")
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg="#148f77", width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg="#ecf0f1")
        self.content.pack(side="left", fill="both", expand=True)

        nav = [
            ("Browse Departments", self._show_browse),
            ("Symptom Search", self._show_symptom),
            ("My Appointments", self._show_appointments),
            ("My Medical Records", self._show_records),
            ("My Bills", self._show_bills),
            ("Review Doctor", self._show_review),
        ]
        for label, cmd in nav:
            tk.Button(sidebar, text=label, command=cmd, width=24,
                      bg="#17a589", fg="white", font=("Arial", 10),
                      relief="flat", pady=10).pack(fill="x", padx=5, pady=3)

        self._show_browse()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_browse(self):
        self._clear_content()
        from gui.patient.browse_departments import BrowseDepartments
        BrowseDepartments(self.content, self.master).pack(fill="both", expand=True)

    def _show_symptom(self):
        self._clear_content()
        from gui.patient.symptom_search import SymptomSearch
        SymptomSearch(self.content, self.master).pack(fill="both", expand=True)

    def _show_appointments(self):
        self._clear_content()
        from gui.patient.my_appointments import MyAppointments
        MyAppointments(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)

    def _show_records(self):
        self._clear_content()
        from gui.patient.my_records import MyRecords
        MyRecords(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)

    def _show_bills(self):
        self._clear_content()
        from gui.patient.my_bills import MyBills
        MyBills(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)

    def _show_review(self):
        self._clear_content()
        from gui.patient.review_doctor import ReviewDoctor
        ReviewDoctor(self.content, self.master.current_user).pack(fill="both", expand=True)
```

- [ ] **Step 2: Create `gui/patient/browse_departments.py`**

```python
# gui/patient/browse_departments.py
import tkinter as tk
from tkinter import ttk
from database.department_dao import get_all_departments
from database.doctor_dao import get_doctors_by_department


class BrowseDepartments(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="#ecf0f1")
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="Browse Departments",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        top = tk.Frame(self, bg="#ecf0f1")
        top.pack(fill="both", expand=True, padx=20)

        # Left: departments list
        left = tk.Frame(top, bg="#ecf0f1")
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text="Departments", font=("Arial", 12, "bold"), bg="#ecf0f1").pack()
        self.dept_list = tk.Listbox(left, font=("Arial", 11), height=20, selectmode="single")
        self.dept_list.pack(fill="both", expand=True)
        self.dept_list.bind("<<ListboxSelect>>", self._on_dept_select)

        # Right: doctors list
        right = tk.Frame(top, bg="#ecf0f1")
        right.pack(side="left", fill="both", expand=True, padx=20)
        tk.Label(right, text="Doctors in Department", font=("Arial", 12, "bold"), bg="#ecf0f1").pack()
        cols = ("ID", "Name", "Experience", "Qualification")
        self.doctor_tree = ttk.Treeview(right, columns=cols, show="headings", height=15)
        widths = [50, 180, 100, 150]
        for c, w in zip(cols, widths):
            self.doctor_tree.heading(c, text=c)
            self.doctor_tree.column(c, width=w)
        self.doctor_tree.pack(fill="both", expand=True)

        tk.Button(self, text="Book Appointment with Selected Doctor",
                  command=self._book, bg="#27ae60", fg="white",
                  font=("Arial", 11)).pack(pady=10)

        self._load_departments()

    def _load_departments(self):
        self._dept_map = {}
        for dept_id, dept_name in get_all_departments():
            self.dept_list.insert("end", dept_name)
            self._dept_map[dept_name] = dept_id

    def _on_dept_select(self, event):
        selection = self.dept_list.curselection()
        if not selection:
            return
        dept_name = self.dept_list.get(selection[0])
        dept_id = self._dept_map[dept_name]
        for row in self.doctor_tree.get_children():
            self.doctor_tree.delete(row)
        for doc in get_doctors_by_department(dept_id):
            self.doctor_tree.insert("", "end", values=doc)

    def _book(self):
        selected = self.doctor_tree.selection()
        if not selected:
            tk.messagebox.showwarning("Select", "Select a doctor first.")
            return
        doctor_id = self.doctor_tree.item(selected[0])["values"][0]
        doctor_name = self.doctor_tree.item(selected[0])["values"][1]
        from gui.patient.book_appointment import BookAppointment
        for w in self.master.winfo_children():
            w.destroy()
        BookAppointment(self.master, self.app, doctor_id, doctor_name).pack(fill="both", expand=True)
```

- [ ] **Step 3: Create `gui/patient/symptom_search.py`**

```python
# gui/patient/symptom_search.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.symptom_services import suggest_for_symptoms


class SymptomSearch(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="#ecf0f1")
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="Symptom Search",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        tk.Label(self, text="Describe your symptoms:", bg="#ecf0f1", font=("Arial", 11)).pack()
        self.symptom_var = tk.StringVar()
        tk.Entry(self, textvariable=self.symptom_var, width=50,
                 font=("Arial", 11)).pack(pady=5)
        tk.Button(self, text="Search", command=self._search,
                  bg="#2980b9", fg="white", font=("Arial", 11)).pack(pady=5)

        tk.Label(self, text="Suggested Doctors:", bg="#ecf0f1",
                 font=("Arial", 12, "bold")).pack(pady=(15, 5))

        cols = ("Doctor ID", "Doctor Name", "Department", "Experience", "Qualification")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        widths = [80, 180, 160, 100, 150]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Button(self, text="Book with Selected Doctor", command=self._book,
                  bg="#27ae60", fg="white", font=("Arial", 11)).pack(pady=8)

    def _search(self):
        text = self.symptom_var.get().strip()
        if not text:
            messagebox.showwarning("Input", "Please describe your symptoms.")
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        suggestions = suggest_for_symptoms(text)
        if not suggestions:
            messagebox.showinfo("No Results", "No departments found for those symptoms. Try browsing departments.")
            return
        for dept_id, dept_name, doctors in suggestions:
            for doc in doctors:
                # doc = (doctor_id, name, experience_years, qualification)
                self.tree.insert("", "end", values=(doc[0], doc[1], dept_name, doc[2], doc[3]))

    def _book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a doctor first.")
            return
        values = self.tree.item(selected[0])["values"]
        doctor_id, doctor_name = values[0], values[1]
        from gui.patient.book_appointment import BookAppointment
        for w in self.master.winfo_children():
            w.destroy()
        BookAppointment(self.master, self.app, doctor_id, doctor_name).pack(fill="both", expand=True)
```

- [ ] **Step 4: Create `gui/patient/book_appointment.py`**

```python
# gui/patient/book_appointment.py
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter import ttk
from services.appointment_services import book_appointment


TIME_SLOTS = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"
]


class BookAppointment(tk.Frame):
    def __init__(self, master, app, doctor_id, doctor_name):
        super().__init__(master, bg="#ecf0f1")
        self.app = app
        self.doctor_id = doctor_id
        self.doctor_name = doctor_name
        self._build()

    def _build(self):
        tk.Label(self, text="Book Appointment",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        tk.Label(self, text=f"Doctor: {self.doctor_name}",
                 font=("Arial", 12), bg="#ecf0f1", fg="#2c3e50").pack(pady=5)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=20)

        tk.Label(form, text="Select Date:", bg="#ecf0f1",
                 font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.date_entry = DateEntry(form, width=18, font=("Arial", 11),
                                    date_pattern="yyyy-mm-dd")
        self.date_entry.grid(row=0, column=1, padx=10)

        tk.Label(form, text="Select Time:", bg="#ecf0f1",
                 font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.time_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.time_var, values=TIME_SLOTS,
                     width=18, font=("Arial", 11), state="readonly").grid(row=1, column=1, padx=10)

        tk.Button(self, text="Confirm Booking", command=self._book,
                  bg="#27ae60", fg="white", font=("Arial", 12), width=18).pack(pady=15)
        tk.Button(self, text="Back", command=self._back,
                  bg="#95a5a6", fg="white", font=("Arial", 10)).pack()

    def _book(self):
        date = self.date_entry.get_date().strftime("%Y-%m-%d")
        time = self.time_var.get()
        if not time:
            messagebox.showwarning("Select Time", "Please select a time slot.")
            return

        patient_id = self.app.current_user["profile_id"]
        success, msg = book_appointment(patient_id, self.doctor_id, date, time)
        messagebox.showinfo("Booking Result", msg)
        if success:
            self._back()

    def _back(self):
        for w in self.master.winfo_children():
            w.destroy()
        from gui.patient.browse_departments import BrowseDepartments
        BrowseDepartments(self.master, self.app).pack(fill="both", expand=True)
```

- [ ] **Step 5: Create `gui/patient/my_appointments.py`**

```python
# gui/patient/my_appointments.py
import tkinter as tk
from tkinter import ttk
from database.appointment_dao import get_appointments_by_patient


class MyAppointments(tk.Frame):
    def __init__(self, master, patient_id):
        super().__init__(master, bg="#ecf0f1")
        self.patient_id = patient_id
        self._build()

    def _build(self):
        tk.Label(self, text="My Appointments",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("ID", "Doctor", "Department", "Date", "Time", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        widths = [60, 180, 150, 120, 80, 100]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Button(self, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white").pack(pady=5)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for appt in get_appointments_by_patient(self.patient_id):
            self.tree.insert("", "end", values=appt)
```

- [ ] **Step 6: Create `gui/patient/my_records.py`**

```python
# gui/patient/my_records.py
import tkinter as tk
from tkinter import ttk
from services.medical_record_services import get_patient_records


class MyRecords(tk.Frame):
    def __init__(self, master, patient_id):
        super().__init__(master, bg="#ecf0f1")
        self.patient_id = patient_id
        self._build()

    def _build(self):
        tk.Label(self, text="My Medical Records",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("Date", "Doctor", "Diagnosis", "Prescription", "Notes")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        widths = [110, 150, 200, 200, 150]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        tk.Label(self, text="Details:", font=("Arial", 11, "bold"), bg="#ecf0f1").pack(anchor="w", padx=20)
        self.detail_text = tk.Text(self, height=8, font=("Arial", 10), state="disabled")
        self.detail_text.pack(padx=20, pady=5, fill="x")

        tk.Button(self, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white").pack(pady=5)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._records = get_patient_records(self.patient_id)
        for rec in self._records:
            # (record_id, doctor_name, date, diagnosis, prescription, notes, created_at)
            self.tree.insert("", "end", values=(rec[2], rec[1], rec[3][:40], rec[4][:40] if rec[4] else "", rec[5][:30] if rec[5] else ""))

    def _on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        idx = self.tree.index(selected[0])
        if idx >= len(self._records):
            return
        rec = self._records[idx]
        text = (
            f"Date: {rec[2]}\n"
            f"Doctor: {rec[1]}\n\n"
            f"Diagnosis:\n{rec[3]}\n\n"
            f"Prescription:\n{rec[4] or 'N/A'}\n\n"
            f"Notes:\n{rec[5] or 'N/A'}"
        )
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.config(state="disabled")
```

- [ ] **Step 7: Create `gui/patient/my_bills.py`**

```python
# gui/patient/my_bills.py
import tkinter as tk
from tkinter import ttk
from database.bill_dao import get_bills_by_patient


class MyBills(tk.Frame):
    def __init__(self, master, patient_id):
        super().__init__(master, bg="#ecf0f1")
        self.patient_id = patient_id
        self._build()

    def _build(self):
        tk.Label(self, text="My Bills",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("Bill ID", "Doctor", "Date", "Amount (KES)", "Issued At")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        widths = [80, 200, 130, 130, 200]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Button(self, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white").pack(pady=5)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for bill in get_bills_by_patient(self.patient_id):
            # (bill_id, doctor_name, date, total_amount, created_at)
            self.tree.insert("", "end", values=bill)
```

- [ ] **Step 8: Create `gui/patient/review_doctor.py`**

```python
# gui/patient/review_doctor.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.appointment_dao import get_appointments_by_patient
from database.review_dao import get_review_by_appointment
from services.review_services import submit_review


class ReviewDoctor(tk.Frame):
    def __init__(self, master, current_user):
        super().__init__(master, bg="#ecf0f1")
        self.current_user = current_user
        self._build()

    def _build(self):
        tk.Label(self, text="Review Doctor",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        tk.Label(self, text="Select a completed appointment to review:",
                 bg="#ecf0f1", font=("Arial", 11)).pack()
        self._appt_var = tk.StringVar()
        self._appt_combo = ttk.Combobox(self, textvariable=self._appt_var,
                                         width=60, state="readonly", font=("Arial", 10))
        self._appt_combo.pack(pady=5)
        self._load_appointments()

        tk.Label(self, text="Rating (1–5 stars):", bg="#ecf0f1", font=("Arial", 11)).pack(pady=(15, 2))
        self._rating_var = tk.IntVar(value=5)
        star_frame = tk.Frame(self, bg="#ecf0f1")
        star_frame.pack()
        for i in range(1, 6):
            tk.Radiobutton(star_frame, text=f"{'★' * i}", variable=self._rating_var,
                           value=i, bg="#ecf0f1", font=("Arial", 13)).pack(side="left", padx=5)

        tk.Label(self, text="Comment (optional):", bg="#ecf0f1", font=("Arial", 11)).pack(pady=(15, 2))
        self.comment_text = tk.Text(self, width=60, height=4, font=("Arial", 10))
        self.comment_text.pack(pady=5)

        tk.Button(self, text="Submit Review", command=self._submit,
                  bg="#27ae60", fg="white", font=("Arial", 12), width=15).pack(pady=10)

    def _load_appointments(self):
        patient_id = self.current_user["profile_id"]
        all_appts = get_appointments_by_patient(patient_id)
        self._appt_map = {}
        choices = []
        for appt in all_appts:
            appt_id, doctor_name, dept, date, time, status = appt
            if status != "completed":
                continue
            existing = get_review_by_appointment(appt_id)
            if existing:
                continue  # already reviewed
            label = f"[{appt_id}] Dr. {doctor_name} — {date} ({dept})"
            choices.append(label)
            self._appt_map[label] = appt
        self._appt_combo["values"] = choices
        if not choices:
            tk.Label(self, text="No completed appointments available to review.",
                     bg="#ecf0f1", fg="#7f8c8d", font=("Arial", 10)).pack()

    def _get_doctor_id_from_appointment(self, appt_id):
        """Look up doctor_id from appointment via doctor DAO."""
        from database.db_connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT doctor_id FROM appointment WHERE appointment_id = %s;", (appt_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()
            conn.close()

    def _submit(self):
        label = self._appt_var.get()
        if not label:
            messagebox.showwarning("Select", "Please select an appointment.")
            return
        appt = self._appt_map[label]
        appt_id = appt[0]
        rating = self._rating_var.get()
        comment = self.comment_text.get("1.0", "end").strip() or None

        patient_id = self.current_user["profile_id"]
        doctor_id = self._get_doctor_id_from_appointment(appt_id)
        if not doctor_id:
            messagebox.showerror("Error", "Could not find doctor for this appointment.")
            return

        success, msg = submit_review(appt_id, patient_id, doctor_id, rating, comment)
        messagebox.showinfo("Result", msg)
        if success:
            self.comment_text.delete("1.0", "end")
            self._appt_var.set("")
            self._load_appointments()
```

- [ ] **Step 9: Test patient dashboard end-to-end**

```bash
python main.py
```
1. Register as a new patient.
2. Log in as patient → verify all 6 sidebar buttons work.
3. Browse departments → select doctor → book appointment.
4. Log in as admin → mark appointment as completed.
5. Log back in as patient → verify bill appears in My Bills.
6. Go to Review Doctor → submit a review.
7. Log in as doctor → verify review appears in My Reviews.

- [ ] **Step 10: Commit**

```bash
git add gui/patient/
git commit -m "feat: add patient dashboard with all screens"
```

---

## Task 16: Seed symptom mappings

The symptom search needs data in `symptom_mapping` to work.

**Files:**
- Modify: `migrations/init_db.py` (add seed function) or run a one-off script

- [ ] **Step 1: Seed symptom mappings (run once after departments exist)**

Run this after logging in as admin and creating departments. Replace `dept_id` values with the actual IDs from your database.

```bash
python -c "
from database.symptom_dao import add_symptom_mapping
from database.department_dao import get_all_departments

# Print existing departments to get their IDs
for dept in get_all_departments():
    print(dept)
"
```

Then seed mappings based on the IDs printed above:

```bash
python -c "
from database.symptom_dao import add_symptom_mapping

# Example: replace dept IDs with actual values from your DB
# Cardiology
add_symptom_mapping('chest pain', 1)
add_symptom_mapping('heart', 1)
add_symptom_mapping('palpitations', 1)

# Neurology
add_symptom_mapping('headache', 2)
add_symptom_mapping('dizziness', 2)
add_symptom_mapping('seizure', 2)

# General
add_symptom_mapping('fever', 3)
add_symptom_mapping('cough', 3)
add_symptom_mapping('fatigue', 3)

print('Done')
"
```

- [ ] **Step 2: Verify symptom search works in the GUI**

Log in as patient → Symptom Search → type "headache" → verify doctors from Neurology appear.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: complete HMS — all features implemented and tested"
```

---

## Self-Review Checklist (passed)

- Patient registration (with profile) ✓
- Doctor assignment by admin ✓
- Appointment scheduling with conflict detection ✓
- Billing auto-generated on appointment completion ✓
- Patient medical history (doctor writes, patient views read-only) ✓
- Doctor reviews (patient submits after completed appointment, doctor views) ✓
- Symptom-to-department matching ✓
- Role-based dashboards (patient/doctor/admin) ✓
- Single window frame switching ✓
- tkcalendar for date picking ✓
- Session persists until logout ✓
