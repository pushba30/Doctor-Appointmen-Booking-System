from flask import Flask, render_template, request, session, redirect, url_for, flash , jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3 as sql
import os
import bcrypt
import random
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from twilio.rest import Client
from datetime import datetime, date




app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a secret key for session
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.static_folder = 'static'



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



# Function to verify hashed password
def verify_password(hashed_password, input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)


#Welcome page
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/home1')
def home1():
    return render_template('home.html')


#Login page 
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = "Welcome to Our Website"  # Initialize the message variable
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sql.connect("appointment.db") as con:
            cur = con.cursor()

            cur.execute("SELECT password FROM admins WHERE username = ?", (username,))
            hashed_password = cur.fetchone()
            if hashed_password and verify_password(hashed_password[0], password):
                session['username'] = username
                return redirect(url_for('admin_dashboard'))
            
            cur.execute("SELECT password FROM users WHERE username = ?", (username,))
            hashed_password = cur.fetchone()
            if hashed_password and verify_password(hashed_password[0], password):
                session['username'] = username
                return redirect(url_for('user_dashboard'))
            
            cur.execute("SELECT password FROM doctors WHERE username = ?", (username,))
            hashed_password = cur.fetchone()
            if hashed_password and verify_password(hashed_password[0], password):
                session['username'] = username
                return redirect(url_for('doctor_dashboard'))
            
            cur.execute("SELECT password FROM manager WHERE username = ?", (username,))
            hashed_password = cur.fetchone()
            if hashed_password and verify_password(hashed_password[0], password):
                session['username'] = username
                return redirect(url_for('manager_dashboard'))
            message="Invalid username or password"

    return render_template('login.html', message=message)




#Function to send email and SMS
def send_notification(subject, email_message, to_email, to_phone, sms_message):
    # Email part
    from_email = "suganthi.cs21@bitsathy.ac.in"  # Replace with your email
    from_password = "Suganthi@10"  # Replace with your email password
    to_email = to_email

    msg = MIMEText(email_message)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    #Sending Email Message
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()

        # Send SMS using Twilio
        account_sid = 'AC5721ff047c2b77fb32dc516c0e366460'
        auth_token = '3bdda0a97695d61c5d52d1bf172b7c3d'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=sms_message,
            from_='+16188449558',
            to=to_phone
        )
        print("SMS:", sms_message)

        return True
    except Exception as e:
        print("Error sending notification:", str(e))
        return False



# Function to send a password reset email
def send_reset_email(email, token):
    subject = "Password Reset for Your Appointment Booking Account"
    message = f"Click the link below to reset your password:\n\n{url_for('reset_password', token=token, _external=True)}"

    # Configure the SMTP server
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "suganthi.cs21@bitsathy.ac.in"
    smtp_password = "Suganthi@10"

    # Create a secure connection to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Create and send the email
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        server.send_message(msg)

# Route for the "Forgot Password" page
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        with sql.connect("appointment.db") as con:
            cur = con.cursor()
            cur.execute("SELECT username FROM users WHERE email = ?", (email,))
            user = cur.fetchone()

            if user:
                # Generate a random token
                token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
                
                # Update the user's token in the database
                cur.execute("UPDATE users SET reset_token = ? WHERE username = ?", (token, user[0]))
                con.commit()

                # Send the password reset email
                send_reset_email(email, token)

                flash("Password reset email sent. Please check your inbox.", "success")
            else:
                flash("No user with that email address found.", "error")
    
    return render_template('forgot_password.html')

# Route for the password reset page
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        password = request.form['pwd']

        with sql.connect("appointment.db") as con:
            cur = con.cursor()
            cur.execute("SELECT username FROM users WHERE reset_token = ?", (token,))
            user = cur.fetchone()

            if user:
                # Hash the new password and update it in the database
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cur.execute("UPDATE users SET password = ?, reset_token = NULL WHERE username = ?", (hashed_password, user[0]))
                con.commit()

                flash("Password reset successfully. You can now login with your new password.", "success")
                return redirect(url_for('login'))
            else:
                flash("Invalid or expired token. Please request a new password reset.", "error")
    
    return render_template('reset_password.html', token=token)



#Admin Dashboard

    


    
@app.route('/doctor')
def doctor():
    if 'username' in session:
        username = session['username']

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT username, first_name, email, age, gender, specialization, mobile FROM doctors")
            doctor_details = cur.fetchall()
            print(doctor_details)  # Add this line to debug
        return render_template('doctor.html', username=username, doctor_details=doctor_details)
    else:
        return redirect(url_for('login'))
    

@app.route('/patient')
def patient():
    if 'username' in session:
        username = session['username']

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT username, first_name, email, age, gender, mobile FROM users")
            patient_details = cur.fetchall()
            print(patient_details)  # Add this line to debug
        return render_template('patient.html', username=username, patient_details=patient_details)
    else:
        return redirect(url_for('login'))
    


#User Registration
@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    message = ""
    if request.method == 'POST':
        try:            
            nm = request.form['un']
            pwd = request.form['pwd']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date()
            gender = request.form['gender']
            blood = request.form['blood']
            country_code = request.form['country_code']
            mobile = request.form['mobile']
            address = request.form['address']


            

            if 'file' not in request.files:
                return redirect(request.url)

            file = request.files['file']

            if file.filename == '':
                return redirect(request.url)

            if file and allowed_file(file.filename):
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{nm}.{file_extension}"  # Construct the filename using the username and the file extension
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                hashed_password = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

                full_mobile_number = country_code + mobile

                today = datetime.today().date()
                age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

                with sql.connect("appointment.db") as con:
                    cur = con.cursor()

                    cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", (nm,))
                    user_count = cur.fetchone()[0]
                    print(user_count)

                    if user_count > 0:
                        message = 'Username Already Exists'
                    else:
                        # Save the image format along with the username in the database
                        cur.execute("INSERT INTO users (filename, username, password, first_name, last_name, email, birthdate, age, gender, blood, mobile, address) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (filename, nm, hashed_password, first_name, last_name, email, birthdate, age, gender, blood, full_mobile_number, address))
                        con.commit()
                        message = "Successfully Registered"
        except Exception as e:
            message = "Error: " + str(e)               
     
    return render_template('user_register.html', message=message)





@app.route('/user_dashboard')
def user_dashboard():
    if 'username' in session:
        username = session['username']

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT username , first_name, last_name, email, age, gender,blood, mobile, address, filename FROM users WHERE  username = ? ", (username,))
            user_details = cur.fetchall()
            print(user_details)  # Add this line to debug
        return render_template('user_dashboard.html', username=username, user_details=user_details)
    else:
        return redirect(url_for('login'))


@app.route('/user_appointment')
def user_appointment():
    if 'username' in session:
        username = session['username']

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM appointments WHERE username = ? AND appointment = 'Pending'", (username,))
            user_appointments = cur.fetchall()
            print(user_appointments)  # Add this line to debug
        return render_template('user_appointment.html', username=username, user_appointments=user_appointments)
    else:
        return redirect(url_for('login'))

    

#For  If user wants to delete Purpose deletions
@app.route('/cancel_appointment', methods=['POST'])
def cancel_appointment():
    data = request.json
    appointment_id = data['appointmentId']

    with sql.connect("appointment.db") as conn:
        cur = conn.cursor()

        # Retrieve appointment details before deleting it
        cur.execute("SELECT doctor_id, date, from_time, to_time FROM appointments WHERE appointment_id = ?", (appointment_id,))
        appointment_details = cur.fetchone()

        # Check if the appointment is in 'Pending' status
        cur.execute("SELECT appointment FROM appointments WHERE appointment_id = ?", (appointment_id,))
        status = cur.fetchone()[0]

        if status == 'Pending':
            # Delete the appointment from the appointments table
            cur.execute("DELETE FROM appointments WHERE appointment_id = ?", (appointment_id,))
            conn.commit()

            # Add the canceled appointment back to the availability table
            doctor_id, date, from_time, to_time = appointment_details
            cur.execute("INSERT INTO availability (doctor_id, date, from_time, to_time) VALUES (?, ?, ?, ?)",
                        (doctor_id, date, from_time, to_time))
            conn.commit()

            print("Canceled appointment added back to availability table:", doctor_id, date, from_time, to_time)

            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Cannot cancel appointment with status other than Pending'})

#For user can delete their accepted appointment
@app.route('/cancel_accepted_appointment', methods=['GET','POST'])
def cancel_accepted_appointment():
    data = request.json
    appointment_id = data['appointmentId']

    # Fetch the appointment details
    conn = sql.connect("appointment.db")
    cur = conn.cursor()
    cur.execute("SELECT doctor_id, date, from_time, to_time FROM appointments WHERE appointment_id = ?", (appointment_id,))
    appointment_data = cur.fetchone()

    if appointment_data:
        doctor_id, date, from_time, to_time = appointment_data

        # Insert the canceled appointment data into the availability table
        cur.execute("INSERT INTO availability (doctor_id, date, from_time, to_time) VALUES (?, ?, ?, ?)",
                    (doctor_id, date, from_time, to_time))

        # Delete the appointment from the appointments table
        cur.execute("DELETE FROM appointments WHERE appointment_id = ?", (appointment_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    else:
        return jsonify({'success': False})


#Display accepted appointment in user_appointments_accpeted
@app.route('/user_appointments_accepted')
def user_appointments_accepted():
    if 'username' in session:
        username = session['username']


    with sql.connect("appointment.db") as conn:
        cur = conn.cursor()
        
    # Fetch the user_id for the logged-in user
        cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user_id = cur.fetchone()[0]

        cur.execute("SELECT * FROM appointments WHERE user_id = ? AND appointment = 'Accepted'", (user_id,))
        accepted_appointments = cur.fetchall()

    return render_template('user_appointments_accepted.html', username=username, accepted_appointments=accepted_appointments)



@app.route('/book')
def book_appointment():
    if 'username' in session:
        username = session['username']
    return render_template('book.html',username=username)

#Manager Dashboard
@app.route('/manager_dashboard')
def manager_dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('manager_dashboard.html', username=username)
    else:
        return redirect(url_for('login'))



#Docter Dashboard
@app.route('/doctor_dashboard')
def doctor_dashboard():
   if 'username' in session:
        username = session['username']

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT username, first_name,last_name, email, age, gender,blood, mobile, filename FROM doctors WHERE  username = ? ", (username,))
            doctor_details = cur.fetchall()
            print(doctor_details)  # Add this line to debug
        return render_template('doctor_dashboard.html', username=username, doctor_details=doctor_details)
   else:
    return redirect(url_for('login'))
    

@app.route('/doctor_appointment')
def doctor_appointment():
    if 'username' in session:
        username = session['username']

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()

            # Fetch the doctor_id for the logged-in doctor
            cur.execute("SELECT docter_id FROM doctors WHERE username = ?", (username,))
            doctor_id = cur.fetchone()[0]
            status='Pending'

            # Fetch appointments based on doctor_id
            cur.execute("SELECT * FROM appointments WHERE doctor_id= ? AND appointment = ?", (doctor_id,status))
            pending_appointments = cur.fetchall()
            print(pending_appointments)  # Add this line to debug
        return render_template('doctor_appointment.html', username=username, pending_appointments=pending_appointments)
    else:
        return redirect(url_for('doctor_login'))

# Route to display accepted appointments for Doctor
@app.route('/accepted_appointment')
def accepted_appointment():
    # Fetch and display the list of accepted appointments
    if 'username' in session:
        username = session['username']

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()

            # Fetch the doctor_id for the logged-in doctor
            cur.execute("SELECT docter_id FROM doctors WHERE username = ?", (username,))
            doctor_id = cur.fetchone()[0]
    
            cur.execute("SELECT * FROM appointments WHERE appointment = 'Accepted' AND doctor_id = ? ",(doctor_id,))
            accepted_appointments = cur.fetchall()

    return render_template('accepted_appointment.html', username=username, accepted_appointments=accepted_appointments)



@app.route('/update_or_delete')
def update_or_delete():
    if 'username' in session:
        username = session['username']

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()

            # Fetch the doctor_id for the logged-in doctor
            cur.execute("SELECT docter_id FROM doctors WHERE username = ?", (username,))
            doctor_id = cur.fetchone()[0]

            # Fetch appointments based on doctor_id
            cur.execute("SELECT date , from_time , to_time FROM availability WHERE doctor_id = ?", (doctor_id,))
            rows = cur.fetchall()
            print(rows)  # Add this line to debug
        return render_template('update_or_delete.html', username=username, rows=rows)
    else:
        return redirect(url_for('doctor_login'))



@app.route('/delete_doctor', methods=['GET', 'POST'])
def delete_doctor():
    if request.method == 'POST':
        username = request.form['username']
        current_datetime = datetime.now().date()
        message = ""

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()
            
            print(current_datetime)
            cur.execute("UPDATE doctors_history SET resign_date = ? WHERE username = ?", (current_datetime, username))
            conn.commit()
                
            # Delete the doctor from the main database
            cur.execute("DELETE FROM doctors WHERE username = ?", (username,))
            conn.commit()

            message = f"Doctor with username {username} has been deleted."

        return render_template('delete_doctor.html', message=message)

    return render_template('delete_doctor.html', message="")



    
# Database initialization and utility functions
def create_connection():
    return sql.connect("appointment.db")



@app.route('/get_available_doctors', methods=['GET'])
# Update or Delete Doctor Timing
def get_available_doctors():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT first_name FROM doctors")
    doctors = [row[0] for row in cur.fetchall()]
    conn.close()
    return doctors

# For Doctor Updation
def update_availability(doctor, date, from_time, to_time):
    conn = create_connection()
    cur = conn.cursor()

    # Get doctor_id from doctors table
    cur.execute("SELECT docter_id FROM doctors WHERE first_name = ?", (doctor,))
    doctor_id = cur.fetchone()[0]

    # Check if the availability entry already exists
    cur.execute("SELECT id FROM availability WHERE doctor_id = ? AND date = ? AND from_time = ? AND to_time = ?",
                (doctor_id, date, from_time, to_time))
    existing_entry = cur.fetchone()

    if existing_entry is None:
        # If entry does not exist, insert it
        cur.execute("INSERT INTO availability (doctor_id, date, from_time, to_time) VALUES (?, ?, ?, ?)",
                    (doctor_id, date, from_time, to_time))
        conn.commit()
        conn.close()
        return False  # Indicate that a new entry was inserted
    else:
        # If entry already exists with the same data, display message
        conn.close()
        return True  # Indicate that the update was not performed



@app.route('/update_delete_doctor', methods=['POST'])
def update_delete_doctor():
    data = request.form
    doctor = data['doctor']
    date = data['date']
    from_time = data['from_time']
    to_time = data['to_time']
    operation = data['operation']

    try:
        if operation == 'update':
            updated = update_availability(doctor, date, from_time, to_time)
            if updated:
                message = 'Availability already exists and was not updated.'
            else:
                message = 'Availability updated successfully.'
        elif operation == 'delete':
            deleted = delete_availability(doctor, date, from_time, to_time)
            if deleted:
                message = 'Availability deleted successfully.'
            else:
                message = 'No matching availability found for deletion.'
        else:
            message = 'Invalid operation.'

        return jsonify({'success': True, 'message': message})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'Failed to perform operation.'})


def delete_availability(doctor, date, from_time, to_time):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT docter_id FROM doctors WHERE first_name = ?", (doctor,))
    doctor_id = cur.fetchone()[0]
    cur.execute("DELETE FROM availability WHERE doctor_id = ? AND date = ? AND from_time = ? AND to_time= ?",
                (doctor_id, date, from_time, to_time))
    conn.commit()
    conn.close()
    return cur.rowcount > 0  # Return True if at least one row was deleted, otherwise False



@app.route('/update_doctor')
def update_doctor_page():
    return render_template('update_doctor.html')



@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session:
        username = session['username']

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()
            
            #upcoming appointments
            cur.execute("SELECT appointment_id ,name, doctor_name, date FROM appointments")
            appointments = cur.fetchall()
            
            #upcoming Sessions
            cur.execute("SELECT d.specialization, a.doctor_id , d.first_name , a.date  FROM availability a JOIN doctors d ON a.doctor_id = d.docter_id ")
            events = cur.fetchall()

            cur.execute("SELECT docter_id, first_name, email, specialization FROM doctors")
            doctor_details = cur.fetchall()

            # Get the current date
            today_date = datetime.now().date()

            # SQL query to count available appointments for today
            sql_query = "SELECT COUNT(*) FROM appointments WHERE date = ?"
            cur.execute(sql_query, (today_date,))
            count = cur.fetchone()[0]

            # SQL query to count available users
            sql_query = "SELECT COUNT(*) FROM users"
            cur.execute(sql_query)
            count_available_users = cur.fetchone()[0]

            # SQL query to count available doctors
            sql_query = "SELECT COUNT(*) FROM doctors"
            cur.execute(sql_query)
            count_available_doctors = cur.fetchone()[0]

            # SQL query to fetch future user appointments
            sql_query = "SELECT COUNT(*) FROM appointments WHERE date >= ?"
            cur.execute(sql_query, (today_date,))
            future_appointments = cur.fetchone()[0]


            print(appointments)  # Add this line to debug
        return render_template('admin_dashboard.html', username=username, appointments=appointments,events=events,doctor_details=doctor_details,count=count,count_available_doctors=count_available_doctors,count_available_users=count_available_users,future_appointments=future_appointments)
    else:
        return redirect(url_for('login'))
    



    

@app.route('/user_change_password', methods=['GET', 'POST'])
def user_change_password():
    if 'username' in session:
        username_1 = session['username']

    if request.method == 'POST':
        username = request.form.get('username')
        current_password = request.form.get('current_password')
        new_username = request.form.get('new_username')
        new_password = request.form.get('pwd')
        confirm_new_password = request.form.get('confirm_pwd')

        # Connect to the SQLite database
        conn = sql.connect('appointment.db')
        cursor = conn.cursor()

        cursor.execute("SELECT username, password FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()

        if user_data and bcrypt.checkpw(current_password.encode('utf-8'), user_data[1]):
            if new_password == confirm_new_password:
                hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("UPDATE users SET username = ?, password = ? WHERE username = ?", (new_username, hashed_new_password, user_data[0]))
                
                cursor.execute("UPDATE appointments SET username = ? WHERE username = ? ",(new_username,user_data[0]))
                conn.commit()
                flash("Username and password changed successfully!", 'success')
            else:
                flash("New password and confirm password do not match.", 'error')
        else:
            flash("Incorrect username or current password.", 'error')

    return render_template('user_settings.html',username=username_1)

    

@app.route('/doctor_change_password', methods=['GET', 'POST'])
def doctor_change_password():
    if 'username' in session:
        username_1 = session['username']
        
    if request.method == 'POST':
        username = request.form.get('username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('pwd')
        confirm_new_password = request.form.get('confirm_pwd')

        # Connect to the SQLite database
        conn = sql.connect('appointment.db')
        cursor = conn.cursor()


        cursor.execute("SELECT password FROM doctors WHERE username = ?", (username,))
        stored_hashed_password = cursor.fetchone()

        if stored_hashed_password and bcrypt.checkpw(current_password.encode('utf-8'), stored_hashed_password[0]):
            if new_password == confirm_new_password:
                hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("UPDATE doctors SET password = ? WHERE username = ?", (hashed_new_password, username))
                conn.commit()
                flash("Password changed successfully!", 'success')
            else:
                flash("New password and confirm password do not match.", 'error')
        else:
            flash("Incorrect username or current password.", 'error')

    return render_template('doctor_settings.html',username=username_1)



    
@app.route('/doctor_edit_profile', methods=['GET', 'POST'])
def doctor_edit_profile():
        if 'username' in session:
            username = session['username']
        
            with sql.connect("appointment.db") as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM doctors WHERE username = ?", (username,))
                user_data = cur.fetchone()

            if request.method == 'POST':
                try:
                    # Get form data
                    first_name = request.form['first_name']
                    last_name = request.form['last_name']
                    email = request.form['email']
                    birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date()
                    gender = request.form['gender']
                    blood = request.form['blood']
                    country_code = request.form['country_code']
                    mobile = request.form['mobile']
                    

                    # Check if a new image is uploaded
                
                    if 'file' in request.files:
                        file = request.files['file']
                        if file.filename != '' and allowed_file(file.filename):
                            filename = f"{username}.{file.filename.rsplit('.', 1)[1].lower()}"
                            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            file.save(filepath)

                            # Update the filename in the database
                            cur.execute('UPDATE doctors SET filename = ? WHERE username = ?', (filename, username))
                            conn.commit()
                            print(" file uploaded.")
                        else:
                            print("Invalid or no file uploaded.")

                    full_mobile_number = country_code + mobile

                    # Calculate age
                    today = datetime.today().date()
                    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

                    with sql.connect("appointment.db") as con:
                        cur = con.cursor()
                        cur.execute('UPDATE doctors SET first_name = ?, last_name = ?, email = ?, birthdate = ?, age = ?, gender = ?, blood = ?, mobile = ? WHERE username = ?', 
                               (first_name, last_name, email, birthdate, age, gender, blood, full_mobile_number, username))
                        con.commit()

                    return redirect(url_for('doctor_profile'))

                except Exception as e:
                    print("Error:", e)

        return render_template('doctor_edit_profile.html')



@app.route('/user_edit_profile', methods=['GET', 'POST'])
def user_edit_profile():
    if 'username' in session:
        username = session['username']
        
        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_data = cur.fetchone()

        if request.method == 'POST':
            try:
                # Get form data
                first_name = request.form['first_name']
                last_name = request.form['last_name']
                email = request.form['email']
                birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date()
                gender = request.form['gender']
                blood = request.form['blood']
                country_code = request.form['country_code']
                mobile = request.form['mobile']
                address = request.form['address']

                # Check if a new image is uploaded
                
                if 'file' in request.files:
                    file = request.files['file']
                    if file.filename != '' and allowed_file(file.filename):
                        filename = f"{username}.{file.filename.rsplit('.', 1)[1].lower()}"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)

                        # Update the filename in the database
                        cur.execute('UPDATE users SET filename = ? WHERE username = ?', (filename, username))
                        conn.commit()
                        print(" file uploaded.")
                    else:
                        print("Invalid or no file uploaded.")

                full_mobile_number = country_code + mobile

                # Calculate age
                today = datetime.today().date()
                age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

                with sql.connect("appointment.db") as con:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET first_name = ?, last_name = ?, email = ?, birthdate = ?, age = ?, gender = ?, blood = ?, mobile = ?, address = ? WHERE username = ?', 
                               (first_name, last_name, email, birthdate, age, gender, blood, full_mobile_number, address, username))
                    con.commit()

                return redirect(url_for('user_dashboard'))

            except Exception as e:
                print("Error:", e)

        return render_template('user_edit_profile.html', user_data=user_data)
    
    return redirect(url_for('login'))



#Appointment Booking
@app.route('/get_doctors', methods=['GET'])
def get_doctors():
    conn = sql.connect("appointment.db")
    cur = conn.cursor()
    current_datetime = datetime.now()
    cur.execute("DELETE FROM  availability WHERE datetime(date || ' ' || from_time) < ?", (current_datetime,))
    # Commit the changes and close the connection
    conn.commit()

    cur.execute("SELECT first_name FROM doctors")
    available_doctors = cur.fetchall()
    conn.close()
    return jsonify(available_doctors)


@app.route('/get_available_specialists', methods=['GET'])
def get_available_specialists():
    conn = sql.connect("appointment.db")
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT specialization FROM doctors")
    specialists = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify(specialists)

@app.route('/get_available_doctors_by_specialist', methods=['POST'])
def get_available_doctors_by_specialist():
    data = request.json
    selected_specialist = data['specialist']
    
    with sql.connect("appointment.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT first_name FROM doctors WHERE specialization = ?", (selected_specialist,))
        doctors = [row[0] for row in cur.fetchall()]
        return jsonify(doctors)

@app.route('/get_available_slots', methods=['POST'])
def get_available_slots():
    data = request.json
    doctor = data['doctor']
    conn = sql.connect("appointment.db")
    cur = conn.cursor()
    cur.execute("SELECT date, from_time, to_time FROM availability WHERE doctor_id = (SELECT docter_id FROM doctors WHERE first_name = ?)", (doctor,))
    available_slots = cur.fetchall()
    conn.close()

    formatted_slots = [f"{slot[0]} - {slot[1]} - {slot[2]}" for slot in available_slots]
    return jsonify({'slots': formatted_slots})



@app.route('/check_availability', methods=['POST'])
def check_availability():
    data = request.json
    doctor = data['doctor']
    slot = data['slot'].split(' - ')  # Split the slot into date, from_time, and to_time

    conn = sql.connect("appointment.db")
    cur = conn.cursor()

    cur.execute("SELECT docter_id FROM doctors WHERE first_name = ?", (doctor,))
    doctor_id = cur.fetchone()

    if doctor_id:
        cur.execute("SELECT id FROM availability WHERE doctor_id = ? AND date = ? AND from_time = ? AND to_time = ?", (doctor_id[0], slot[0], slot[1], slot[2]))
        availability = cur.fetchone()

        conn.close()

        if availability:
            return jsonify({'available': True})
    return jsonify({'available': False})


@app.route('/book_appointment', methods=['POST'])
def register_appointment():
    data = request.json
    doctor = data['doctor']
    slot = data['slot'].split(' - ')
    date = slot[0]
    from_time = slot[1]
    to_time = slot[2]
    username = session['username']

    with sql.connect("appointment.db") as conn:
        cur = conn.cursor()

        cur.execute("SELECT docter_id FROM doctors WHERE first_name = ?", (doctor,))
        doctor_id = cur.fetchone()

        if doctor_id:
            cur.execute("SELECT id FROM availability WHERE doctor_id = ? AND date = ? AND from_time = ? AND to_time = ? ", (doctor_id[0], date, from_time, to_time))
            availability_id = cur.fetchone()

            if availability_id:
                # Get the user_id from the users table using the username
                cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
                user_id = cur.fetchone()[0]

                # Get the user_id from the users table using the username
                cur.execute("SELECT first_name FROM users WHERE username = ?", (username,))
                name = cur.fetchone()[0]

                # Get the doctor's name from the doctors table using doctor_id
                cur.execute("SELECT first_name FROM doctors WHERE docter_id = ?", (doctor_id[0],))
                doctor_name = cur.fetchone()[0]

                cur.execute("DELETE FROM availability WHERE id = ?", (availability_id[0],))

                # Insert appointment into appointments table
                cur.execute("INSERT INTO appointments (user_id, doctor_id, username, name, doctor_name, date, from_time, to_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (user_id, doctor_id[0], username, name, doctor_name, date, from_time, to_time))

                conn.commit()
                return jsonify({'success': True})

    return jsonify({'success': False})

#For doctor update status of user 
@app.route('/update_appointment_status', methods=['POST'])
def update_appointment_status():
    data = request.json
    appointment_id = data['appointmentId']
    new_status = data['newStatus']

    with sql.connect("appointment.db") as conn:
        cur = conn.cursor()

        # Update the status in the appointments table
        cur.execute("UPDATE appointments SET appointment = ? , status = ?  WHERE appointment_id = ?", (new_status,'Not Visited', appointment_id))
        conn.commit()

        # Fetch appointment details
        cur.execute("SELECT a.doctor_id, a.date, a.from_time, a.to_time, u.email, u.mobile, d.first_name FROM appointments a JOIN users u ON a.user_id = u.user_id JOIN doctors d ON a.doctor_id = d.docter_id WHERE a.appointment_id = ?", (appointment_id,))
        appointment_details = cur.fetchone()
        doctor_id, date, from_time, to_time, user_email, user_mobile, doctor_name = appointment_details

        # Send email and SMS notifications
        if new_status in ['Accepted', 'Rejected']:
            subject = f"Appointment {new_status}"
            email_message = f"Your appointment with Dr. {doctor_name} on {date} from {from_time} to {to_time} has been {new_status.lower()}."
            sms_message = f"Your appointment with Dr. {doctor_name} on {date} from {from_time} to {to_time} has been {new_status.lower()}."

            send_notification(subject, email_message, user_email, user_mobile, sms_message)

        return jsonify({'success': True})





#Doctor Registration
@app.route('/doctor_register', methods=['GET', 'POST'])
def doctor_register():

    current_datetime = datetime.now().date()

    message = ""
    
    if request.method == 'POST':
        try:
            nm = request.form['un']
            pwd = request.form['pwd']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date()
            gender = request.form['gender']
            special= request.form['special']
            blood = request.form['blood']
            country_code = request.form['country_code']
            mobile = request.form['mobile']

            if 'file' not in request.files:
                return redirect(request.url)

            file = request.files['file']

            if file.filename == '':
                return redirect(request.url)

            if file and allowed_file(file.filename):
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{nm}.{file_extension}"  # Construct the filename using the username and the file extension
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                 # Hash the password before storing it
                hashed_password = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

                full_mobile_number = country_code + mobile

                # Calculate age
                today = datetime.today().date()
                age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


                with sql.connect("appointment.db") as con:
                    cur = con.cursor()

                    # Check if the username already exists
                    cur.execute("SELECT COUNT(*) FROM doctors WHERE username = ?", (nm,))
                    user_count = cur.fetchone()[0]

                    if user_count > 0:
                        message = 'Username Already Exists'
                    else:
                        cur.execute("INSERT INTO doctors (filename, username, password, first_name , last_name , email, birthdate, age, gender, blood, specialization, mobile) VALUES (?, ?, ?, ?, ?, ?,?, ?, ?, ?,?,? )",
                                (filename, nm, hashed_password, first_name,last_name, email,birthdate, age,gender,blood,special, full_mobile_number))
                        con.commit()
                        cur.execute("INSERT INTO doctors_history (filename, username, password, first_name , last_name , email, birthdate, age, gender, blood, specialization, mobile , join_date) VALUES (?, ?, ?, ?, ?, ?,?, ?, ?, ?,?,?,? )",
                                (filename, nm, hashed_password, first_name,last_name, email,birthdate, age,gender,blood,special, full_mobile_number,current_datetime))
                        con.commit()

                        message = "Successfully Registered"
        except Exception as e:
            message = "Error: " + str(e)

    return render_template('doctor_register.html', message=message)


#Manager Registration
@app.route('/manager_register', methods=['GET', 'POST'])
def manager_register():
    message = ""
    if request.method == 'POST':
        try:
            nm = request.form['un']
            pwd = request.form['pwd']

            # Hash the password before storing it
            hashed_password = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

            with sql.connect("appointment.db") as con:
                cur = con.cursor()

                # Check if the username already exists
                cur.execute("SELECT COUNT(*) FROM manager WHERE username = ?", (nm,))
                user_count = cur.fetchone()[0]

                if user_count > 0:
                    message = 'Username Already Exists'
                else:
                    cur.execute("INSERT INTO manager (username, password) VALUES (?, ?)",
                                (nm, hashed_password))
                    con.commit()
                    message = "Successfully Registered"
        except Exception as e:
            message = "Error: " + str(e)

    return render_template('manager_register.html', message=message)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/appointment')
def appointment():
    if 'username' in session:
        username = session['username']

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT appointment_id ,name, doctor_name, date, from_time, to_time , appointment , status FROM appointments")
            appointments = cur.fetchall()
            print(appointments)  # Add this line to debug
        return render_template('Appointment.html', username=username, appointments=appointments)
    else:
        return redirect(url_for('login'))

@app.route('/new_booking')
def new_booking():
    if 'username' in session:
        username = session['username']

        current_datetime = datetime.now()

        with sql.connect("appointment.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT appointment_id ,name, doctor_name, date, from_time, to_time , appointment FROM appointments WHERE datetime(date || ' ' || from_time) > ?", (current_datetime,))
            appointments = cur.fetchall()
            print(appointments)  # Add this line to debug
        return render_template('new_booking.html', username=username, appointments=appointments)
    else:
        return redirect(url_for('login'))

@app.route('/sessions')
def sessions():
    
    current_datetime = datetime.now()

    with sql.connect("appointment.db") as conn:
        cur = conn.cursor()

        cur.execute("DELETE FROM  availability WHERE datetime(date || ' ' || from_time) < ?", (current_datetime,))
        # Commit the changes and close the connection
        conn.commit()
         
        cur.execute("SELECT d.specialization, a.doctor_id , d.first_name , a.date, a.from_time, a.to_time  FROM availability a JOIN doctors d ON a.doctor_id = d.docter_id ")
        appointments = cur.fetchall()
        print(appointments)  # Add this line to debug
    return render_template('session.html', appointments=appointments)


@app.route('/today_sessions')
def today_sessions():
    current_date = date.today()


    with sql.connect("appointment.db") as conn:  
        cur = conn.cursor()
    
        # Fetch rows that are valid for today
        cur.execute("SELECT appointment_id,name,doctor_name,date,from_time,to_time ,appointment,status FROM appointments WHERE date = ? ", (current_date,))
        today = cur.fetchall()
    
    return render_template('today_session.html', today=today)


#blood Donates form 
@app.route("/blood")
def blood():
    return render_template("blood.html")


@app.route('/admin_blood_status')
def admin_blood_status():
    conn = sql.connect('appointment.db')
    submissions = conn.execute('SELECT id, name, email, phone, address, blood_group, status , action FROM submissions').fetchall()
    conn.close()
    return render_template('admin_blood_status.html', submissions=submissions)

@app.route('/manager_blood_status')
def manager_blood_status():
    conn = sql.connect('appointment.db')
    submissions = conn.execute('SELECT id, name, email, phone, address, blood_group, status , action FROM submissions').fetchall()
    conn.close()
    return render_template('manager_blood_status.html', submissions=submissions)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    blood_group = request.form['blood_group']

    conn = sql.connect('appointment.db')
    conn.execute('INSERT INTO submissions (name, email, phone, address, blood_group, status) VALUES (?, ?, ?, ?, ?, ?)',
                 (name, email, phone, address, blood_group, 'pending'))
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/update_action/<int:submission_id>', methods=['POST'])
def update_action(submission_id):
    conn = sql.connect('appointment.db')
    submission = conn.execute('SELECT name, email, phone FROM submissions WHERE id = ?', (submission_id,)).fetchone()

    if submission:
        name, email,mobile = submission
        conn.execute('UPDATE submissions SET action = ? WHERE id = ?', ('donated', submission_id))
        conn.commit()
        print(mobile)
        subject = 'Blood Donation Form Status Update'
        email_message = f'Hello {name}, thank you for your donation.'
        sms_message = f'Hello {name}, thank you for your donation.'
        to_email = submission[1]  # Replace with recipient's email address

        send_notification(subject, email_message, to_email, mobile, sms_message)
        

    return redirect(url_for('manager_blood_status'))


@app.route('/update_status/<int:submission_id>', methods=['POST'])
def update_status(submission_id):
    conn = sql.connect('appointment.db')
    submission = conn.execute('SELECT name, email, phone FROM submissions WHERE id = ?', (submission_id,)).fetchone()

    if submission:
        name, email, mobile = submission
        conn.execute('UPDATE submissions SET status = ?, action = ? WHERE id = ?', ('accepted', 'not_Donate', submission_id))
        conn.commit()
        # Rest of your notification code
        print(mobile)
        subject = 'Blood Donation Form Status Update'
        email_message = f'Hello {name}, your form has been accepted and your donation has been received.'
        sms_message = f'Hello {name}, your form has been accepted and your donation has been received.'
        to_email = submission[1]  # Replace with recipient's email address

        send_notification(subject, email_message, to_email, mobile, sms_message)

    return redirect(url_for('manager_blood_status'))


@app.route('/patient_status/<int:appointment_id>', methods=['POST'])
def patient_status(appointment_id):
    conn = sql.connect('appointment.db')
    #appointment = conn.execute('SELECT name, email, number FROM appointments WHERE id = ?', (appointment_id,)).fetchone()

    if appointment:
        #name, email, to_phone = appointment
       conn.execute('UPDATE appointments SET status = ? WHERE appointment_id = ?', ('Visited', appointment_id))
       conn.commit()
    
    return redirect(url_for('accepted_appointment'))


@app.route('/doctor_list')
def doctor_list():
    return render_template('doctor_list.html')


@app.route('/health_tips')
def health_tips():
    return render_template('health_tips.html')




@app.route('/make_presription')
def make_presription():
    if 'username' in session:
        username = session['username']
    # Retrieve prescriptions from the database
    conn = sql.connect('appointment.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients')
    prescriptions = cursor.fetchall()

    cursor.execute('SELECT DISTINCT medicine_type FROM medicine')
    medicine_types = cursor.fetchall()

    cursor.execute('SELECT * FROM medicine_temp')
    medicine_temp  = cursor.fetchall()

    conn.close()

    return render_template('doctor_make_prescription.html',username=username, prescriptions=prescriptions, medicine_types=medicine_types, medicine_temp=medicine_temp)


@app.route('/add_medication', methods=['POST'])
def add_medication():
    medicine_type = request.form['medicine_type']
    company = request.form['company']
    medicine_name = request.form['medicine_name']
     #Insert the new patient into the database
    conn = sql.connect('appointment.db')
    conn.execute('INSERT INTO medicine (Medicine_Type,Company,Medicine) VALUES (? , ? , ?)', (medicine_type,company,medicine_name))
    conn.commit()
    conn.close()
    return redirect(url_for('make_presription'))


@app.route('/fetch_medicine_names', methods=['POST'])
def fetch_medicine_names():
    # Your code to query the database and return medicine names goes here
    selected_medicine_type = request.form['selected_medicine_type']

    conn = sql.connect('appointment.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT Medicine FROM medicine WHERE Medicine_type = ?', (selected_medicine_type,))
    medicine_names = cursor.fetchall()
    conn.close()

    return jsonify({'medicine_names': [name[0] for name in medicine_names]})




# Route to add a patient and their medicines
@app.route('/add', methods=['POST'])
def add():
    # Extract patient data from the form
    patient_name = request.form['patient_name']
    appointment_id = request.form['appointment_id']
    date_of_birth = request.form['date_of_birth']
    blood_group = request.form['blood_group']
    gender = request.form['gender']

    # Retrieve medicine data from the form as a list
    conn = sql.connect('appointment.db')
    cursor = conn.cursor()
    cursor.execute('SELECT medicine_Type,Company,medicine_name,Morning , Noon , Night , Duration , Quantity FROM medicine_temp')
    medicines = cursor.fetchall()
    conn.close()


    # Connect to the database
    conn = sql.connect('appointment.db')
    cursor = conn.cursor()

    # Insert patient details into the 'patients' table
    cursor.execute('INSERT INTO patients (patient_name, appointment_id, date_of_birth, blood_group, gender) VALUES (?, ?, ?, ?, ?)',
                   (patient_name, appointment_id, date_of_birth, blood_group, gender))
    patient_id = cursor.lastrowid  # Get the ID of the newly inserted patient

    # Insert medicine details into the 'medicines' table
    for medicine in medicines:
        # Split the medicine data (modify as per your form structure)
        

        medicine_type, company, medicine_name, morning_check, noon_check, night_check, duration, quantity = medicine

        cursor.execute('INSERT INTO medicines (medicine_type, company, medicine_name, morning_check, noon_check, night_check, duration, quantity, patient_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (medicine_type, company, medicine_name, morning_check, noon_check, night_check, duration, quantity, patient_id))

    
    conn.commit()
    conn.close()

    conn = sql.connect('appointment.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM medicine_temp')
    conn.commit()
    conn.close()
   

    return redirect(url_for('make_presription'))

@app.route('/submit', methods=['POST','GET'])
def submit():
    # Check if each checkbox was submitted and set a default value of 0 if not checked
    medicine_type = request.form['selected_medicine_type']
    company = request.form['company']
    medicine_name = request.form['selected_medicine_name']
    morning_check = request.form.get('frequencyMorningCheck', '0')
    noon_check = request.form.get('frequencyNoonCheck', '0')
    night_check = request.form.get('frequencyNightCheck', '0')
    duration = request.form['duration']
    quantity = request.form['quantity']
    print("hai")

    conn = sql.connect('appointment.db')
    conn.execute('INSERT INTO medicine_temp (medicine_Type,Company,medicine_name,Morning , Noon , Night , Duration , Quantity) VALUES (? , ? , ?, ? , ?,?, ? , ?)', (medicine_type,company,medicine_name,morning_check,noon_check,night_check,duration,quantity))
    conn.commit()
    conn.close()

    return redirect(url_for('make_presription'))

@app.route('/delete_medicine/<int:medicine_id>', methods=['GET'])
def delete_medicine(medicine_id):
    try:
        conn = sql.connect('appointment.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM medicine_temp WHERE ID = ?', (medicine_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('make_presription'))
    except Exception as e:
        return redirect(url_for('make_presription'))



if __name__ == '__main__':
    app.run(debug=True)


