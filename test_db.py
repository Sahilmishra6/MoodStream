import mysql.connector

print("START")

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mummypapa",
    database="mood_system",
    auth_plugin="mysql_native_password",
    connection_timeout=5
)

print("CONNECTED")
db.close()
