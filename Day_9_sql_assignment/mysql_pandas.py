import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bharani@20",
    database="university_db"
)

query = "SELECT * FROM students"

df = pd.read_sql(query, conn)

print("Student Records:")
print(df)

conn.close()