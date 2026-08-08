#Test data if needed

from database.database import connect_database

conn = connect_database()
cursor = conn.cursor()

cursor.execute("DELETE FROM Reports")

conn.commit()
conn.close()

print("Old reports cleared.")