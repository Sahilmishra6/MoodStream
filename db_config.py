import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="mummypapa",
        database="mood_system",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )

# TEST
if __name__ == "__main__":
    print("START")
    db = get_db_connection()
    print("CONNECTED")
    db.close()