from flask import Flask, jsonify, render_template, request, redirect, session, url_for
import mysql.connector
import os, re

app = Flask(__name__)
app.secret_key = os.urandom(24)

conn = mysql.connector.connect(
    host="localhost", user="root", password="", database="loan_db")
cursor = conn.cursor()

# Route for HomePage
@app.route('/')
def home():
    return render_template('index.html')

# Route for Register
@app.route('/register')
def register():
    return render_template('register.html')

# Route For Login
@app.route('/login')
def login():
    if 'user_id' not in session:
        return render_template('login.html')
    else:
        return redirect('/dashboard')

# Logout A User
@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

# Route for dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        return redirect('/login')

# VALIDATE AND LOGIN USER
@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    # Perform email validation using regular expression
    email_regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if not re.match(email_regex, email):
        return jsonify({'status': 'failure', 'message': 'Please enter a valid email address!'})

    # Perform registration logic and check if email and password match in database
    cursor.execute(""" SELECT * FROM `users` where `email` LIKE '{}' AND BINARY `password` LIKE '{}' """
                   .format(email, password))
    users = cursor.fetchall()
    if len(users) > 0:
        session['user_id'] = users[0][0]
        return jsonify({'status': 'success', 'message': 'Login successful!'})  # Return success status and message as JSON response
    else:
        return jsonify({'status': 'failure', 'message': 'Email or password is incorrect!'})  # Return failure status and message as JSON response

# REGISTER A USER
@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')

    cursor.execute("SELECT `email` FROM `users`")
    users = cursor.fetchall()
    print(users)
    print(email)

    if any(user[0] == email for user in users):
        print('Email already exists!')
        return "fail"
    else:
        cursor.execute("""INSERT INTO `users` (`user_id`, `name`, `email`, `password`) VALUES (NULL, '{}', '{}', '{}')""".format(name, email, password))
        conn.commit()
        print('Registration successful!')
        return "success"
    
# FETCH USER NAME
@app.route('/get_user_name')
def get_user_name():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor.execute("SELECT name FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            name = row[0]
            return jsonify({'success': True, 'name': name})
        else:
            return jsonify({'success': False, 'message': 'User not found'})
    else:
        return jsonify({'success': False, 'message': 'User not logged in'})    

# Route for admin dashboard
@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Fetch Users from Database
@app.route('/user_details', methods=['GET'])
def user_details():
    # Fetch only the latest 6 rows from the database, ordered by a specific column in descending order
    cursor.execute("SELECT * FROM users ORDER BY user_id DESC LIMIT 6")
    rows = cursor.fetchall()
    print(rows)
    users = []
    for row in rows:
        user = {
            'user_id': row[0],
            'user_name': row[1],
            'email': row[2],
            'password': row[3],
        }
        users.append(user)
    return jsonify(users=users)

#Reset Password
@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    password = request.form.get('password')

    email_regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if not re.match(email_regex, email):
        return jsonify({'status': 'failure', 'message': 'Please enter a valid email address!'})

    # Update password in the database using parameterized query
    cursor.execute("UPDATE users SET password = %s WHERE email = %s", (password, email))
    conn.commit()

    # Check if the update was successful
    if cursor.rowcount > 0:
        return jsonify({'status': 'success', 'message': 'Password updated successfully!'})
    else:
        return jsonify({'status': 'failure', 'message': 'Failed to update password. User not found or invalid email!'})


@app.route('/reset')
def reset():
    return render_template('forgot.html')

if __name__ == "__main__":
    app.run(debug=True)