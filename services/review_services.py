# services/review_services.py
from database.review_dao import create_review, get_reviews_by_doctor, get_review_by_appointment


def submit_review(appointment_id, patient_id, doctor_id, rating, comment=None):
    if get_review_by_appointment(appointment_id):
        return False, "You have already reviewed this appointment."
    if not (1 <= rating <= 5):
        return False, "Rating must be between 1 and 5."
    if create_review(appointment_id, patient_id, doctor_id, rating, comment):
        return True, "Review submitted. Thank you!"
    return False, "Failed to submit review."


def get_doctor_reviews(doctor_id):
    return get_reviews_by_doctor(doctor_id)
