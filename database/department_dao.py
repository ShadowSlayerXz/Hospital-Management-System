# database/department_dao.py
from database.db_connection import get_connection


def get_all_departments():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT department_id, department_name FROM department ORDER BY department_name;")
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching departments:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def create_department(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO department (department_name) VALUES (%s);",
            (name,)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error creating department:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def delete_department(department_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM department WHERE department_id = %s;", (department_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error deleting department:", e)
        return False
    finally:
        cursor.close()
        conn.close()
