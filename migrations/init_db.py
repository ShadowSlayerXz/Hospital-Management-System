from database.db_connection import get_connection


def initialize_database():
    conn = get_connection()
    if not conn:
        print("Failed to connect to database")
        return

    cursor = conn.cursor()

    try:
        with open("migrations/init.sql", "r") as file:
            sql_script = file.read()
            cursor.execute(sql_script)

        conn.commit()
        print("Database initialized successfully")

    except Exception as e:
        print("Error initializing database:", e)
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


from services.auth_services import register_user
from database.user_dao import get_user_by_email

def seed_admin():
    if not get_user_by_email("admin@hms.com"):
        register_user("Admin", "admin@hms.com", "admin123", "admin")
        print("Admin user created")
    else:
        print("Admin user already exists")


if __name__ == "__main__":
    initialize_database()
    seed_admin()
