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


if __name__ == "__main__":
    initialize_database()
