
-- Department Table

CREATE TABLE IF NOT EXISTS department (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
);


-- Users Table

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    user_email VARCHAR(100) NOT NULL UNIQUE,
    user_password VARCHAR(255) NOT NULL,
    user_role VARCHAR(20) NOT NULL CHECK (user_role IN ('patient', 'doctor', 'admin'))
);


-- Doctor Table

CREATE TABLE IF NOT EXISTS doctor (
    doctor_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    department_id INT NOT NULL REFERENCES department(department_id),
    experience_years INT CHECK (experience_years >= 0),
    qualification VARCHAR(100)
);


-- Patient Table

CREATE TABLE IF NOT EXISTS patient (
    patient_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    age INT CHECK (age > 0),
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    phone VARCHAR(15),
    address TEXT
);


-- Appointment Table

CREATE TABLE IF NOT EXISTS appointment (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patient(patient_id) ON DELETE CASCADE,
    doctor_id INT NOT NULL REFERENCES doctor(doctor_id) ON DELETE CASCADE,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    UNIQUE (doctor_id, appointment_date, appointment_time)
);


-- Medical Record Table

CREATE TABLE IF NOT EXISTS medical_record (
    record_id SERIAL PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE REFERENCES appointment(appointment_id) ON DELETE CASCADE,
    diagnosis TEXT NOT NULL,
    prescription TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Bill Table

CREATE TABLE IF NOT EXISTS bill (
    bill_id SERIAL PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE REFERENCES appointment(appointment_id) ON DELETE CASCADE,
    total_amount NUMERIC(10,2) NOT NULL CHECK (total_amount >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Bill Items Table

CREATE TABLE IF NOT EXISTS bill_item (
    item_id SERIAL PRIMARY KEY,
    bill_id INT NOT NULL REFERENCES bill(bill_id) ON DELETE CASCADE,
    item_name VARCHAR(100) NOT NULL,
    amount NUMERIC(10,2) NOT NULL CHECK (amount >= 0)
);


-- Symptom Mapping Table

CREATE TABLE IF NOT EXISTS symptom_mapping (
    mapping_id SERIAL PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL UNIQUE,
    department_id INT NOT NULL REFERENCES department(department_id) ON DELETE CASCADE
);


-- Doctor Review Table

CREATE TABLE IF NOT EXISTS review (
    review_id SERIAL PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE REFERENCES appointment(appointment_id) ON DELETE CASCADE,
    patient_id INT NOT NULL REFERENCES patient(patient_id) ON DELETE CASCADE,
    doctor_id INT NOT NULL REFERENCES doctor(doctor_id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Department seed data
-- ON CONFLICT DO NOTHING makes this safe to re-run on existing databases.

INSERT INTO department (department_name) VALUES ('Cardiology')         ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Neurology')          ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Orthopedics')        ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Pulmonology')        ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Gastroenterology')   ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Dermatology')        ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Pediatrics')         ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Gynecology')         ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Urology')            ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Nephrology')         ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Oncology')           ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Radiology')          ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Ophthalmology')      ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('ENT')                ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Psychiatry')         ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Endocrinology')      ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Rheumatology')       ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('General Surgery')    ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Emergency Medicine') ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Anesthesiology')     ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Hematology')         ON CONFLICT (department_name) DO NOTHING;
INSERT INTO department (department_name) VALUES ('Pathology')          ON CONFLICT (department_name) DO NOTHING;


-- Symptom seed data
-- Uses subqueries so inserts are skipped if the named department does not exist.
-- ON CONFLICT DO NOTHING makes this safe to re-run.

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'chest', department_id FROM department WHERE department_name = 'Cardiology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'heart', department_id FROM department WHERE department_name = 'Cardiology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'palpitations', department_id FROM department WHERE department_name = 'Cardiology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'angina', department_id FROM department WHERE department_name = 'Cardiology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'headache', department_id FROM department WHERE department_name = 'Neurology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'seizure', department_id FROM department WHERE department_name = 'Neurology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'stroke', department_id FROM department WHERE department_name = 'Neurology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'dizziness', department_id FROM department WHERE department_name = 'Neurology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'migraine', department_id FROM department WHERE department_name = 'Neurology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'bone', department_id FROM department WHERE department_name = 'Orthopedics'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'fracture', department_id FROM department WHERE department_name = 'Orthopedics'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'joint', department_id FROM department WHERE department_name = 'Orthopedics'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'knee', department_id FROM department WHERE department_name = 'Orthopedics'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'spine', department_id FROM department WHERE department_name = 'Orthopedics'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'cough', department_id FROM department WHERE department_name = 'Pulmonology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'asthma', department_id FROM department WHERE department_name = 'Pulmonology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'breathing', department_id FROM department WHERE department_name = 'Pulmonology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'lung', department_id FROM department WHERE department_name = 'Pulmonology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'wheeze', department_id FROM department WHERE department_name = 'Pulmonology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'stomach', department_id FROM department WHERE department_name = 'Gastroenterology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'nausea', department_id FROM department WHERE department_name = 'Gastroenterology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'vomiting', department_id FROM department WHERE department_name = 'Gastroenterology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'ulcer', department_id FROM department WHERE department_name = 'Gastroenterology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'diarrhea', department_id FROM department WHERE department_name = 'Gastroenterology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'skin', department_id FROM department WHERE department_name = 'Dermatology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'rash', department_id FROM department WHERE department_name = 'Dermatology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'acne', department_id FROM department WHERE department_name = 'Dermatology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'allergy', department_id FROM department WHERE department_name = 'Dermatology'
ON CONFLICT (keyword) DO NOTHING;

INSERT INTO symptom_mapping (keyword, department_id)
SELECT 'itch', department_id FROM department WHERE department_name = 'Dermatology'
ON CONFLICT (keyword) DO NOTHING;
