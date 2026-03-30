# database/bill_dao.py
from database.db_connection import get_connection


def create_bill(appointment_id, total_amount):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO bill (appointment_id, total_amount)
            VALUES (%s, %s);
        """, (appointment_id, total_amount))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating bill:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def get_bills_by_patient(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.bill_id, u.user_name, a.appointment_date,
                   b.total_amount, b.created_at
            FROM bill b
            JOIN appointment a ON b.appointment_id = a.appointment_id
            JOIN doctor d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE a.patient_id = %s
            ORDER BY b.created_at DESC;
        """, (patient_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching bills:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_all_bills():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.bill_id, pu.user_name, du.user_name,
                   a.appointment_date, b.total_amount, b.created_at
            FROM bill b
            JOIN appointment a ON b.appointment_id = a.appointment_id
            JOIN patient p ON a.patient_id = p.patient_id
            JOIN users pu ON p.user_id = pu.user_id
            JOIN doctor d ON a.doctor_id = d.doctor_id
            JOIN users du ON d.user_id = du.user_id
            ORDER BY b.created_at DESC;
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching all bills:", e)
        return []
    finally:
        cursor.close()
        conn.close()
