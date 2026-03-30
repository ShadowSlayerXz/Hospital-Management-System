# database/patient_dao.py
from database.db_connection import get_connection


def get_patient_by_user_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM patient WHERE user_id = %s;", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print("Error fetching patient:", e)
        return None
    finally:
        cursor.close()
        conn.close()


def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.patient_id, u.user_name, p.age, p.gender, p.phone
            FROM patient p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY u.user_name;
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching patients:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def create_patient(user_id, age, gender, phone, address):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO patient (user_id, age, gender, phone, address)
            VALUES (%s, %s, %s, %s, %s);
        """, (user_id, age, gender, phone, address))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating patient:", e)
        return False
    finally:
        cursor.close()
        conn.close()
