# Hospital Management System

A comprehensive Hospital Management System designed to streamline hospital operations and improve patient care delivery.

## About the Project

The Hospital Management System is a modern solution that helps hospitals efficiently manage their day-to-day operations. It brings together multiple departments, healthcare professionals, and patients into one integrated platform.

## Core Purpose

This system enables:

- **Patients** to register, manage their profiles, and book appointments with doctors
- **Doctors** to manage their schedules, view patient appointments, and maintain medical records
- **Administrators** to oversee hospital operations, manage departments, and generate reports

## Key Features

### User Management
- Support for multiple user roles (Patients, Doctors, Administrators)
- Secure authentication and registration system
- Individual user profiles with role-specific information

### Appointment System
- Schedule appointments between patients and doctors
- Real-time appointment tracking with status updates
- Prevents scheduling conflicts and double-bookings
- Appointment status management (scheduled, completed, cancelled)

### Patient Management
- Detailed patient profiles with personal information
- Track patient demographics and contact information
- Maintain patient medical history

### Doctor Management
- Manage doctor profiles with specializations and experience
- Organize doctors by departments
- Track doctor qualifications and expertise

### Medical Records
- Maintain comprehensive medical records for each appointment
- Document diagnoses, prescriptions, and clinical notes
- Automatic tracking of record creation dates

### Billing & Payments
- Generate itemized bills for appointments and services
- Track billing amounts and payment dates
- Support for multiple billing line items per appointment

### Department Organization
- Organize hospital staff and services by departments
- Intelligent symptom-to-department mapping system
- Direct patients to appropriate departments based on their symptoms

## How to Run

### Prerequisites
- Python 3.x
- MySQL database server

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Hospital-Management-System
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```


5. **Run the application**
   ```bash
   docker-compose up -d
   python main.py
   ```

   On first run, the app automatically initializes the database schema, creates the admin account, and seeds all departments and doctors — no separate setup command needed.

### Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@hms.com | admin123 |
| Doctor (any) | doctor.`<department>`.1@hms.com | doctor123 |
| Patient | Register via the app | — |

> See `credentials.md` for the full list of seeded doctor emails.

---

## Intended Users

- **Patients**: Easy access to doctor appointments and medical history
- **Doctors**: Streamlined schedule management and patient record viewing
- **Hospital Administrators**: Complete oversight of operations and resource management
- **Hospital Staff**: Department coordination and patient flow management

---

**Project Type**: College Project  
**Last Updated**: March 2026
