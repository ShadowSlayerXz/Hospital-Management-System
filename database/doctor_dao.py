# database/doctor_dao.py
from database.db_connection import get_connection


def get_all_doctors():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT d.doctor_id, u.user_name, dep.department_name,
                   d.experience_years, d.qualification
            FROM doctor d
            JOIN users u ON d.user_id = u.user_id
            JOIN department dep ON d.department_id = dep.department_id
            ORDER BY u.user_name;
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching doctors:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_doctors_by_department(department_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT d.doctor_id, u.user_name, d.experience_years, d.qualification
            FROM doctor d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.department_id = %s
            ORDER BY u.user_name;
        """, (department_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching doctors by department:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def get_doctor_by_user_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM doctor WHERE user_id = %s;", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print("Error fetching doctor:", e)
        return None
    finally:
        cursor.close()
        conn.close()


def create_doctor(user_id, department_id, experience_years, qualification):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO doctor (user_id, department_id, experience_years, qualification)
            VALUES (%s, %s, %s, %s);
        """, (user_id, department_id, experience_years, qualification))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating doctor:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def delete_doctor(doctor_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM doctor WHERE doctor_id = %s;", (doctor_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error deleting doctor:", e)
        return False
    finally:
        cursor.close()
        conn.close()
