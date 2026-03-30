# services/medical_record_services.py
from database.medical_record_dao import create_record, get_records_by_patient, get_record_by_appointment


def add_record(appointment_id, diagnosis, prescription, notes=""):
    if get_record_by_appointment(appointment_id):
        return False, "A record already exists for this appointment."
    if create_record(appointment_id, diagnosis, prescription, notes):
        return True, "Medical record saved."
    return False, "Failed to save record."


def get_patient_records(patient_id):
    return get_records_by_patient(patient_id)
