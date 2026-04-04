# Hospital Management System — Project Report

**Project Type:** College Project  
**Date:** April 2026  
**Language:** Python 3.x  
**Interface:** Tkinter (Desktop GUI)  
**Database:** PostgreSQL 15

---

## 1. Introduction

The Hospital Management System (HMS) is a desktop application built to streamline the core operations of a hospital. It replaces manual, paper-based processes with a centralized digital platform that connects patients, doctors, and administrators through a single system.

The system supports three distinct user roles — Patient, Doctor, and Admin — each with a dedicated dashboard and set of features. It handles the full lifecycle of a hospital visit: from patient registration and appointment booking, to medical record creation, billing, and doctor reviews.

---

## 2. Objectives

- Provide patients with a self-service portal to book appointments, view records, and pay bills.
- Allow doctors to manage their appointments, write medical records, and view patient history.
- Give administrators complete control over departments, doctors, users, and appointments.
- Ensure secure authentication with hashed passwords and role-based access.
- Prevent scheduling conflicts through database-level constraints.

---

## 3. Tech Stack

| Component        | Technology                        |
|------------------|-----------------------------------|
| Language         | Python 3.x                        |
| GUI Framework    | Tkinter + tkcalendar              |
| Database         | PostgreSQL 15 (Docker)            |
| DB Driver        | psycopg2                          |
| Authentication   | bcrypt (password hashing)         |
| Infrastructure   | Docker Compose                    |

---

## 4. System Architecture

The project follows a **3-tier layered architecture**:

```
main.py
  └── gui/           (Presentation Layer — Tkinter frames)
        └── services/    (Business Logic Layer)
              └── database/    (Data Access Layer — SQL via psycopg2)
                    └── PostgreSQL (via Docker)
```

**Key design patterns:**
- Each DAO function opens a connection, executes a parameterized SQL query, and closes the connection in a `finally` block.
- No ORM is used — all SQL is written directly.
- All queries use parameterized placeholders to prevent SQL injection.
- Passwords are hashed with `bcrypt` before storage and verified with `bcrypt.checkpw()`.
- The GUI uses a single-window frame-swap pattern: `App.show_frame()` destroys the current frame and replaces it with a new one.

---

## 5. Database Schema

The database (`hms`) consists of 9 tables:

| Table            | Description                                                  |
|------------------|--------------------------------------------------------------|
| `users`          | Core authentication table; stores name, email, hashed password, and role (`patient/doctor/admin`) |
| `patient`        | Patient profile linked to `users`; stores age, gender, phone, address |
| `doctor`         | Doctor profile linked to `users`; stores department, experience, qualification |
| `department`     | Hospital departments (e.g., Cardiology, Neurology)           |
| `appointment`    | Links a patient to a doctor with date, time, and status (`scheduled/completed/cancelled`); unique constraint prevents double-booking |
| `medical_record` | Diagnosis, prescription, and notes for a completed appointment |
| `bill`           | Total bill amount tied to an appointment                     |
| `bill_item`      | Itemized line items for a bill                               |
| `symptom_mapping`| Maps symptom keywords to departments for intelligent search  |
| `review`         | Patient rating (1–5) and comment for a doctor, tied to an appointment |

---

## 6. Features Implemented

### 6.1 Authentication
- Patient self-registration (name, email, password, age, gender, phone, address)
- Login for all roles (patient, doctor, admin)
- Role-based redirect to the appropriate dashboard after login
- Passwords stored as bcrypt hashes

### 6.2 Patient Portal
| Screen             | Functionality                                                  |
|--------------------|----------------------------------------------------------------|
| Browse Departments | View all hospital departments                                  |
| Symptom Search     | Enter a symptom keyword and get the matching department        |
| Book Appointment   | Select a department, doctor, date (via calendar picker), and time slot |
| My Appointments    | View all past and upcoming appointments with status            |
| My Medical Records | View diagnoses, prescriptions, and notes from completed visits |
| My Bills           | View itemized bills linked to appointments                     |
| Review Doctor      | Submit a 1–5 star rating and comment for a completed appointment |

### 6.3 Doctor Portal
| Screen              | Functionality                                                  |
|---------------------|----------------------------------------------------------------|
| My Appointments     | View all scheduled appointments                                |
| Write Medical Record| Select a completed appointment and enter diagnosis, prescription, notes |
| Patient History     | Look up a patient and view their full medical history          |
| My Reviews          | View all patient reviews and ratings                           |

### 6.4 Admin Portal
| Screen              | Functionality                                                  |
|---------------------|----------------------------------------------------------------|
| Manage Departments  | Add and view hospital departments                              |
| Manage Doctors      | Register doctor accounts and assign them to departments        |
| All Appointments    | View all appointments across the hospital                      |
| All Users           | View all registered users by role                              |

---

## 7. Project Structure

```
Hospital-Management-System/
├── main.py                    # Entry point
├── requirements.txt
├── docker-compose.yml
├── migrations/
│   ├── init.sql               # Full DB schema
│   └── init_db.py             # Schema initializer script
├── database/
│   ├── db_connection.py
│   ├── user_dao.py
│   ├── patient_dao.py
│   ├── doctor_dao.py
│   ├── department_dao.py
│   ├── appointment_dao.py
│   ├── medical_record_dao.py
│   ├── bill_dao.py
│   ├── review_dao.py
│   └── symptom_dao.py
├── services/
│   ├── auth_services.py
│   ├── appointment_services.py
│   ├── billing_services.py
│   ├── medical_record_services.py
│   ├── review_services.py
│   └── symptom_services.py
└── gui/
    ├── app.py                 # Root Tk window + frame manager
    ├── login_frame.py         # Login + patient registration
    ├── patient/
    │   ├── dashboard.py
    │   ├── browse_departments.py
    │   ├── symptom_search.py
    │   ├── book_appointment.py
    │   ├── my_appointments.py
    │   ├── my_records.py
    │   ├── my_bills.py
    │   └── review_doctor.py
    ├── doctor/
    │   ├── dashboard.py
    │   ├── appointments.py
    │   ├── write_record.py
    │   ├── patient_history.py
    │   └── my_reviews.py
    └── admin/
        ├── dashboard.py
        ├── manage_departments.py
        ├── manage_doctors.py
        ├── all_appointments.py
        └── all_users.py
```

---

## 8. How to Run

**Prerequisites:** Python 3.x, Docker Desktop

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Start PostgreSQL database
docker-compose up -d

# 3. Initialize the database schema (first time only)
python migrations/init_db.py

# 4. Run the application
python main.py

# To stop the database
docker-compose down
```

---

## 9. Security Considerations

- **Password hashing:** All passwords are hashed with `bcrypt` before being stored. Plain-text passwords are never saved.
- **Parameterized queries:** All SQL statements use `%s` placeholders with psycopg2, preventing SQL injection.
- **Role-based access:** Login redirects users to their role-specific dashboard. There is no cross-role access within the GUI.
- **Double-booking prevention:** A `UNIQUE(doctor_id, appointment_date, appointment_time)` constraint at the database level prevents conflicting appointments.

---

## 10. Limitations & Future Scope

| Limitation                        | Possible Improvement                              |
|-----------------------------------|---------------------------------------------------|
| No automated test suite           | Add pytest-based unit and integration tests       |
| No connection pooling             | Use psycopg2 connection pool or SQLAlchemy        |
| Admin cannot register via GUI     | Add admin creation script or seeding              |
| No appointment cancellation by patient | Add cancel button in My Appointments screen  |
| No email notifications            | Integrate SMTP for appointment confirmations      |
| Single-machine desktop app        | Convert to a web app (Flask/Django + HTML)        |
| Billing is admin/doctor-generated | Add automated billing on appointment completion  |

---

## 11. Conclusion

The Hospital Management System successfully demonstrates a working multi-role desktop application built with Python and PostgreSQL. It covers the core hospital workflows — registration, appointment booking, medical records, billing, and reviews — within a clean 3-tier architecture. The codebase is structured to be easy to extend, with each entity following the same DAO → Service → GUI pattern.
