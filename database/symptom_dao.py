# database/symptom_dao.py
from database.db_connection import get_connection


def get_departments_by_symptom(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT DISTINCT dep.department_id, dep.department_name
            FROM symptom_mapping sm
            JOIN department dep ON sm.department_id = dep.department_id
            WHERE sm.keyword ILIKE %s;
        """, (f"%{keyword}%",))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching departments by symptom:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def add_symptom_mapping(keyword, department_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO symptom_mapping (keyword, department_id) VALUES (%s, %s);
        """, (keyword, department_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error adding symptom mapping:", e)
        return False
    finally:
        cursor.close()
        conn.close()


def get_all_symptom_mappings():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT sm.mapping_id, sm.keyword, dep.department_name
            FROM symptom_mapping sm
            JOIN department dep ON sm.department_id = dep.department_id
            ORDER BY sm.keyword;
        """)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching symptom mappings:", e)
        return []
    finally:
        cursor.close()
        conn.close()


def delete_symptom_mapping(mapping_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM symptom_mapping WHERE mapping_id = %s;", (mapping_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error deleting symptom mapping:", e)
        return False
    finally:
        cursor.close()
        conn.close()
