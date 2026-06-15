import os
import pymysql

def get_db_connection():
    # Looks for Render environment variables first; falls back to your local settings if not found
    host = os.environ.get("DB_HOST", "localhost")
    user = os.environ.get("DB_USER", "root")
    password = os.environ.get("DB_PASSWORD", "mummypapa")
    database = os.environ.get("DB_NAME", "mood_system")
    port = int(os.environ.get("DB_PORT", 3306))

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        cursorclass=pymysql.cursors.DictCursor
    )

# TEST
if __name__ == "__main__":
    print("START")
    try:
        db = get_db_connection()
        print("CONNECTED SUCCESSFULLY!")
        db.close()
    except Exception as e:
        print(f"CONNECTION FAILED: {e}")
