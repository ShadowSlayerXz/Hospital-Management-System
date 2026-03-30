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
