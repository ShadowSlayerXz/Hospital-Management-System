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
