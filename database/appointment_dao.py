# database/appointment_dao.py
from database.db_connection import get_connection


def create_appointment(patient_id, doctor_id, date, time):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO appointment (patient_id, doctor_id, appointment_date, appointment_time, status)
            VALUES (%s, %s, %s, %s, 'scheduled');
        """, (patient_id, doctor_id, date, time))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating appointment:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def check_slot_availability(doctor_id, date, time):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM appointment
            WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s
            AND status != 'cancelled';
        """, (doctor_id, date, time))
        count = cursor.fetchone()[0]
        return count == 0
    except Exception as e:
        print("Error checking slot:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def get_appointments_by_patient(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT a.appointment_id, u.user_name, dep.department_name,
                   a.appointment_date, a.appointment_time, a.status
            FROM appointment a
            JOIN doctor d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            JOIN department dep ON d.department_id = dep.department_id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC;
        """, (patient_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching patient appointments:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_appointments_by_doctor(doctor_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT a.appointment_id, u.user_name, a.appointment_date,
                   a.appointment_time, a.status
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE a.doctor_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC;
        """, (doctor_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching doctor appointments:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_all_appointments():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT a.appointment_id, pu.user_name, du.user_name,
                   a.appointment_date, a.appointment_time, a.status
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            JOIN users pu ON p.user_id = pu.user_id
            JOIN doctor d ON a.doctor_id = d.doctor_id
            JOIN users du ON d.user_id = du.user_id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC;
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching all appointments:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def mark_completed(appointment_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE appointment SET status = 'completed'
            WHERE appointment_id = %s;
        """, (appointment_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error marking appointment completed:", e)
        return False
    finally:
        cursor.close()
        conn.close()
