import psycopg2
from psycopg2.extras import RealDictCursor

def execute_query(query, values=None, fetch_one=False):
    connection = psycopg2.connect(
        dbname="dhms_db",
        user="dhms_user",
        password="dhms_05",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(query, values)
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        connection.commit()
        return result
    except Exception as e:
        print(f"Database error: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
