import sqlite3

# Connect to the database
conn = sqlite3.connect('appointment.db')

# Create a cursor
cursor = conn.cursor()

# Create users table
cursor.execute('''
   CREATE TABLE IF NOT EXISTS users (
       user_id INTEGER PRIMARY KEY AUTOINCREMENT,
       filename TEXT NOT NULL,
       username TEXT NOT NULL,
       password TEXT NOT NULL,
       first_name TEXT NOT NULL,
       last_name TEXT NOT NULL,
       birthdate DATE NOT NULL,               
       age INTEGER NOT NULL ,
       gender TEXT NOT NULL,
       blood TEXT NOT NULL,
       email TEXT NOT NULL,
       mobile TEXT NOT NULL,
       address TEXT NOT NULL,
       reset_token TEXT
       
   )
''')



# Create admins table
cursor.execute('''
   CREATE TABLE IF NOT EXISTS admins (
       admins_id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT NOT NULL,
       password TEXT NOT NULL
   )
''')

# Create manager table
cursor.execute('''
   CREATE TABLE IF NOT EXISTS manager (
       manager_id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT NOT NULL,
       password TEXT NOT NULL
   )
''')

# Create doctors table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        docter_id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        birthdate DATE NOT NULL,
        age INTEGER NOT NULL ,
        gender TEXT NOT NULL,
        blood TEXT NOT NULL,
        specialization TEXT NOT NULL, 
        email TEXT NOT NULL,
        mobile TEXT NOT NULL
    )
''')

# Create doctors table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors_history (
        docter_id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        birthdate DATE NOT NULL,
        age INTEGER NOT NULL ,
        gender TEXT NOT NULL,
        blood TEXT NOT NULL,
        specialization TEXT NOT NULL, 
        email TEXT NOT NULL,
        mobile TEXT NOT NULL,
        join_date DATE NOT NULL,
        resign_date DATE
    )
''')

#Creating Availability Table
cursor.execute('''CREATE TABLE IF NOT EXISTS availability (
                    id INTEGER PRIMARY KEY,
                    doctor_id INTEGER,
                    date TEXT NOT NULL,
                    from_time TEXT NOT NULL,
                    to_time TEXT NOT NULL,
                    FOREIGN KEY (doctor_id) REFERENCES doctors(docter_id)
                )''')

# Create appointments table
cursor.execute('''
   CREATE TABLE IF NOT EXISTS appointments (
       appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       doctor_id INTEGER NOT NULL,
       username TEXT NOT NULL,
       name TEXT NOT NULL,
       doctor_name TEXT NOT NULL,
       date TEXT NOT NULL,
       from_time TEXT NOT NULL,
       to_time TEXT NOT NULL,
       appointment TEXT NOT NULL DEFAULT 'Pending',
       status TEXT ,
       FOREIGN KEY (doctor_id) REFERENCES doctors(docter_id),
       FOREIGN KEY (user_id) REFERENCES users(user_id)
   )
''')

# Create a table to store form submissions
cursor.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        status TEXT NOT NULL,
        action TEXT

    );
''')


# Create the patients table if it doesn't exist
conn.execute('''CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_name TEXT,
                        appointment_id TEXT,
                        date_of_birth TEXT,
                        blood_group TEXT,
                        gender TEXT
                    )''')
    
# Create the medicines table if it doesn't exist
conn.execute('''CREATE TABLE IF NOT EXISTS medicines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        medicine_type TEXT,
                        company TEXT,
                        medicine_name TEXT,
                        morning_check TEXT,
                        noon_check TEXT,
                        night_check TEXT,
                        duration TEXT,
                        quantity INTEGER,
                        patient_id INTEGER,
                        FOREIGN KEY (patient_id) REFERENCES patients (id)
                    )''')


conn.execute('''
    CREATE TABLE IF NOT EXISTS medicine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Medicine_Type TEXT NOT NULL,
        Company TEXT NOT NULL,
        Medicine TEXT NOT NULL
    )
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS medicine_temp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_type TEXT NOT NULL,
        Company TEXT NOT NULL,
        medicine_name TEXT NOT NULL,
        Morning  INTEGER  NOT NULL,
        Noon INTEGER  NOT NULL,
        Night INTEGER  NOT NULL,
        Duration INTEGER  NOT NULL,
        Quantity INTEGER  NOT NULL
)
''')




# Commit changes and close the cursor
conn.commit()
cursor.close()

# Close the connection
conn.close()
