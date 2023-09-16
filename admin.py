import sqlite3
import bcrypt
# Connect to the SQLite database
conn = sqlite3.connect('appointment.db')
cursor = conn.cursor()

# Insert a new username and password into the user table
username = 'admin'
password = 'admin123'


# Hash the password before storing it
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, hashed_password))

username = 'MD01'
password = 'Soulcare@05'
# Hash the password before storing it
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
cursor.execute('INSERT INTO manager (username, password) VALUES (?, ?)', (username, hashed_password))
# Commit the transaction and close the connection
conn.commit()
conn.close()