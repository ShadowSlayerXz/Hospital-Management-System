# Hospital Management System — Design Spec
**Date:** 2026-03-30
**Stack:** Python 3, psycopg2, PostgreSQL 15 (Docker), Tkinter, tkcalendar, bcrypt

---

## Overview

A desktop Hospital Management System with a Tkinter GUI. Single-user-at-a-time operation. Three roles — patient, doctor, admin — each with a separate dashboard. Single window with frame switching (no multi-window clutter). Session persists until the user logs out.

---

## Architecture & File Structure

```
main.py                          ← entry point, launches App
gui/
  app.py                         ← App class, frame stack, current_user
  login_frame.py                 ← Login + Register screens
  patient/
    dashboard.py                 ← Patient main dashboard
    browse_departments.py        ← Browse dept → pick doctor
    symptom_search.py            ← Describe symptoms → suggested dept/doctor
    book_appointment.py          ← Pick date/time via tkcalendar
    my_appointments.py           ← View upcoming/past appointments
    my_records.py                ← View medical history
    my_bills.py                  ← View bills
  doctor/
    dashboard.py                 ← Doctor main dashboard
    appointments.py              ← View scheduled appointments
    write_record.py              ← Add diagnosis/prescription
    patient_history.py           ← View full patient history
  admin/
    dashboard.py                 ← Admin main dashboard
    manage_doctors.py            ← Add/remove doctors
    manage_departments.py        ← Add/remove departments
    all_appointments.py          ← View/complete appointments (triggers billing)
    all_users.py                 ← View/manage users
database/
  db_connection.py               ← (existing) get_connection → PostgreSQL
  user_dao.py                    ← (existing) get_user_by_email, create_user
  doctor_dao.py                  ← get_all_doctors, get_doctors_by_department, create_doctor, delete_doctor
  patient_dao.py                 ← get_patient_by_user_id, create_patient
  department_dao.py              ← get_all_departments, create_department, delete_department
  appointment_dao.py             ← create_appointment, get_appointments_by_patient/doctor/all, check_slot_availability, mark_completed
  medical_record_dao.py          ← create_record, get_records_by_patient, get_record_by_appointment
  bill_dao.py                    ← create_bill, get_bills_by_patient, get_all_bills
  symptom_dao.py                 ← get_departments_by_symptom
services/
  auth_services.py               ← (existing) register_user, login_user (bcrypt)
  appointment_services.py        ← check slot availability, create appointment
  billing_services.py            ← auto-generate bill on appointment completion
  medical_record_services.py     ← add and fetch medical records
  symptom_services.py            ← map symptom keywords → department → doctors
```

---

## Data Flow

### Login / Register
1. `LoginFrame` collects email + password.
2. Calls `auth_services.login_user()`.
3. On success, `App` stores `current_user` dict `{id, name, role}` and raises the matching dashboard frame (`PatientDashboard`, `DoctorDashboard`, or `AdminDashboard`).
4. Register screen calls `auth_services.register_user()` then redirects to login.

### Patient Booking Flow (Browse)
1. Patient opens **Browse Departments** → sees all departments from `department_dao`.
2. Selects a department → sees doctors from `doctor_dao.get_doctors_by_department()`.
3. Selects a doctor → opens **Book Appointment**.
4. Picks date and time via `tkcalendar`.
5. `appointment_services.check_slot_availability()` queries `appointment_dao` for conflicts.
   - If slot is free → `appointment_dao.create_appointment()` → success message.
   - If slot is taken → show "Doctor is busy at this time" message.

### Patient Booking Flow (Symptom Search)
1. Patient opens **Symptom Search** → types symptom keywords.
2. `symptom_services` queries `symptom_mapping` table for matching department.
3. Returns suggested department + list of available doctors in that department.
4. Patient selects a doctor → proceeds to **Book Appointment** (same flow as above).

### Appointment Completion & Auto-Billing
1. Admin views **All Appointments** → clicks "Mark as Completed" on an appointment.
2. `appointment_dao.mark_completed()` updates status to `completed`.
3. `billing_services.generate_bill()` automatically creates a `bill` record linked to that appointment.
4. Patient can view the bill from their **My Bills** screen.

### Medical Records
1. Doctor opens **My Appointments** → selects a patient appointment.
2. Opens **Write Medical Record** → enters diagnosis and prescription.
3. `medical_record_services.add_record()` saves to `medical_record` table linked to the appointment.
4. Doctor can also open **Patient History** → search a patient → view all past records.
5. Patients can view (read-only) their records from **My Medical Records**.

### Session Management
- `App.current_user` holds the logged-in user for the full session.
- Every dashboard has a **Logout** button that clears `current_user` and raises `LoginFrame`.

---

## DAOs & Services

### DAOs (all follow existing `user_dao.py` pattern: open connection → parameterized SQL → close in `finally`)

| DAO | Key Functions |
|---|---|
| `doctor_dao` | `get_all_doctors`, `get_doctors_by_department`, `create_doctor`, `delete_doctor` |
| `patient_dao` | `get_patient_by_user_id`, `create_patient` |
| `department_dao` | `get_all_departments`, `create_department`, `delete_department` |
| `appointment_dao` | `create_appointment`, `get_appointments_by_patient`, `get_appointments_by_doctor`, `get_all_appointments`, `check_slot_availability`, `mark_completed` |
| `medical_record_dao` | `create_record`, `get_records_by_patient`, `get_record_by_appointment` |
| `bill_dao` | `create_bill`, `get_bills_by_patient`, `get_all_bills` |
| `symptom_dao` | `get_departments_by_symptom` |

### Services

| Service | Responsibility |
|---|---|
| `appointment_services` | Validate slot availability, create appointment |
| `billing_services` | Auto-generate bill when appointment marked completed |
| `medical_record_services` | Add and fetch medical records |
| `symptom_services` | Match symptom keywords → department → list of doctors |

---

## GUI Screens per Role

### Patient Dashboard
| Screen | Description |
|---|---|
| Browse Departments | List all departments → select → see doctors → book |
| Symptom Search | Type symptoms → get suggested dept/doctor → book |
| My Appointments | List upcoming and past appointments |
| My Medical Records | View diagnoses and prescriptions (read-only) |
| My Bills | View bills tied to completed appointments |

### Doctor Dashboard
| Screen | Description |
|---|---|
| My Appointments | List of scheduled appointments with patient name, date/time |
| Write Medical Record | Select appointment → enter diagnosis + prescription |
| Patient History | Search patient → view all past records |

### Admin Dashboard
| Screen | Description |
|---|---|
| Manage Doctors | Add or remove doctors (linked to a department) |
| Manage Departments | Add or remove departments |
| All Appointments | View all appointments, mark as completed (triggers auto-bill) |
| All Users | View all registered users |

---

## Database Schema (Reference)

Defined in `migrations/init.sql`. Key tables:

| Table | Purpose |
|---|---|
| `users` | Core auth — `user_role` is `patient/doctor/admin` |
| `doctor` | Doctor profile linked to `users.user_id` and `department` |
| `patient` | Patient profile linked to `users.user_id` |
| `department` | Hospital departments |
| `appointment` | Links patient ↔ doctor with date, time, status |
| `medical_record` | Diagnosis/prescription tied to an `appointment` |
| `bill` / `bill_item` | Billing tied to an `appointment` |
| `symptom_mapping` | Maps symptom keywords to departments |

---

## GUI Framework

- **Tkinter** — single window, frame switching via `tkraise()`
- **tkcalendar** — date picker for appointment scheduling
- **App class** (`gui/app.py`) — owns the window, holds `current_user`, manages frame stack
- Each screen is a `tk.Frame` subclass instantiated once and stacked; navigation raises the correct frame
