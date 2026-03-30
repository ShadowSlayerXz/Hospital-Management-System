# services/appointment_services.py
from database.appointment_dao import check_slot_availability, create_appointment


def book_appointment(patient_id, doctor_id, date, time):
    if not check_slot_availability(doctor_id, date, time):
        return False, "Doctor is busy at this time slot. Please choose another."
    if create_appointment(patient_id, doctor_id, date, time):
        return True, "Appointment booked successfully."
    return False, "Failed to book appointment. Please try again."
