import psycopg2


def get_connection():
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5433,
            database="hms",
            user="postgres",
            password="postgres",
        )
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None
