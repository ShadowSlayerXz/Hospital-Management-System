from database.db_connection import get_connection


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT * FROM users WHERE user_email = %s;"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        return user

    except Exception as e:
        print("Error fetching user:", e)
        return None

    finally:
        cursor.close()
        conn.close()


def create_user(name, email, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO users (user_name, user_email, user_password, user_role)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (name, email, password, role))
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print("Error creating user:", e)
        return False

    finally:
        cursor.close()
        conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT user_id, user_name, user_email, user_role FROM users ORDER BY user_role, user_name;"
        )
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching users:", e)
        return []
    finally:
        cursor.close()
        conn.close()
