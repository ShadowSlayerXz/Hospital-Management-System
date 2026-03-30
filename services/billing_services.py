# services/billing_services.py
from database.appointment_dao import mark_completed
from database.bill_dao import create_bill

CONSULTATION_FEE = 500.00


def complete_appointment_and_bill(appointment_id):
    if not mark_completed(appointment_id):
        return False, "Failed to mark appointment as completed."
    if not create_bill(appointment_id, CONSULTATION_FEE):
        return False, "Appointment completed but billing failed."
    return True, f"Appointment completed. Bill of {CONSULTATION_FEE:.2f} generated."
