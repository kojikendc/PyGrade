from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from mysql.connector import Error  # Ensure we import Error class from mysql.connector
from flask import session  # Assuming you're using Flask for session management
import mysql.connector



app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root123'
MYSQL_DB = 'new_pygrade'

# Function to get a database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# function to check credentials
def check_credentials(username, password):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, password, role, full_name FROM users WHERE username = %s
        UNION
        SELECT id, password, role, full_name FROM admins WHERE username = %s
    """, (username, username))

    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        stored_password = result[1]  # The password field is at index 1
        if stored_password == password:
            # Return id (student_id), role, and full_name if credentials are valid
            return result  # Returns (id, password, role, full_name)

    return None


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if username or password is missing
        if not username or not password:
            return render_template('login.html', error_message="Please fill in all fields")

        # Check user credentials
        user_data = check_credentials(username, password)

        if user_data:
            # Set session variables upon successful login
            session['username'] = username
            session['role'] = user_data[2]  # user_data[2] is the role
            session['name'] = user_data[3]  # user_data[3] is the full name
            session['student_id'] = user_data[0]  # user_data[0] is the id (student_id)

            # Redirect based on the role
            if user_data[2] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user_data[2] == 'faculty':
                return redirect(url_for('faculty_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            return render_template('login.html', error_message="Invalid username or password")

    # Render the login page for GET requests
    return render_template('login.html')



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("You have been logged out.", 'info')
    return redirect(url_for('login'))



""""=====================================ROUTES AND FUNCTIONS FOR ADMINS ACCOUNTS================================================"""

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        flash("Unauthorized access. Please log in.", 'error')
        return redirect(url_for('login'))
    return render_template('MIS.html', username=session['username'])

@app.route('/faculty_dashboard')
def bacToDashboard():
    return render_template ('/faculty_dashboard.html')

@app.route ('/create_acount')
def create_account():
    return render_template('/admin_create_account.html')

#route for creating account
@app.route('/admin_create_account')
def sign_up():
    return render_template('/admin_create_account.html')

#route for viewing accounts
@app.route('/view_accounts')
def viewing_accounts():
   return render_template("admin_view_accounts.html")


# route to register an account
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('admin_create_account.html')

    full_name = request.form['fullName']
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    student_id = request.form.get('studentId')
    department = request.form.get('department')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if '@' not in username or '.' not in username.split('@')[-1]:
            flash("Error: Please enter a valid email address.", "error")
            return redirect(url_for('register'))

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_username = cursor.fetchone()

        cursor.execute("SELECT * FROM users WHERE full_name = %s", (full_name,))
        existing_full_name = cursor.fetchone()

        if existing_username:
            flash("Error: An account with this username already exists.", "error")
            return redirect(url_for('register'))
        
        if existing_full_name:
            flash("Full Name already exists. Please choose a different one.", "error")
            return redirect(url_for('register'))

        # Store password in plain text (not recommended for production)
        if role == 'faculty':
            if not department:
                flash("Error: Department is required for faculty accounts.", "error")
                return redirect(url_for('register'))
            sql = "INSERT INTO users (full_name, username, password, role, department) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (full_name, username, password, role, department))
        else:
            if not student_id:
                flash("Error: Student ID is required for student accounts.", "error")
                return redirect(url_for('register'))
            sql = "INSERT INTO users (full_name, username, password, role, student_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (full_name, username, password, role, student_id))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Account created successfully!", "success")
        return redirect(url_for('register'))

    except Exception as e:
        flash(f"An unexpected error occurred: {e}", "error")
        return redirect(url_for('register'))


# route to fetch accounts from database
@app.route('/fetchAccounts', methods=['GET'])
def fetch_users():
    search = request.args.get('search', '').lower()
    user_type = request.args.get('type', 'all')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT id, full_name, username, role, student_id, department FROM users WHERE full_name LIKE %s OR username LIKE %s"
        search_query = f"%{search}%"

        if user_type != 'all':
            query += " AND role = %s"
            cursor.execute(query, (search_query, search_query, user_type))
        else:
            cursor.execute(query, (search_query, search_query))

        result = []
        while True:
            users = cursor.fetchmany(1000)
            if not users:
                break

            for user in users:
                user_data = {
                    'full_name': user[1],
                    'username': user[2],
                    'role': user[3],
                }

                if user[3] == 'student':
                    user_data['student_id'] = user[4] if user[4] else None
                elif user[3] == 'faculty':
                    user_data['department'] = user[5] if user[5] else None

                result.append(user_data)

        cursor.close()
        connection.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500



@app.route('/fetchAccounts', methods=['GET'])
def fetch_accounts():
    try:
        search = request.args.get('search', '')
        user_type = request.args.get('type', 'all')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT full_name, username, role, student_id, department
            FROM users
            WHERE (full_name ILIKE %s OR username ILIKE %s)
        """
        params = [f'%{search}%', f'%{search}%']

        # Apply explicit filters for user types
        if user_type == 'student':
            query += " AND role = 'student'"
        elif user_type == 'faculty':
            query += " AND role = 'faculty'"

        query += " ORDER BY full_name ASC"

        cursor.execute(query, params)
        users = cursor.fetchall()

        user_list = []
        for user in users:
            user_list.append({
                'full_name': user[0],
                'username': user[1],
                'role': user[2],
                'student_id': user[3],
                'department': user[4]
            })

        cursor.close()
        connection.close()

        return jsonify(user_list), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
    


#helper function for fetching account
@app.route('/fetchStudents', methods=['GET'])
def fetch_students():
    return fetch_users_by_role('student')

@app.route('/fetchFaculty', methods=['GET'])
def fetch_faculty():
    return fetch_users_by_role('faculty')

def fetch_users_by_role(role):
    try:
        search = request.args.get('search', '')
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT full_name, username, role, student_id, department
            FROM users
            WHERE (LOWER(full_name) LIKE %s OR LOWER(username) LIKE %s)
            AND LOWER(role) = %s
            ORDER BY full_name ASC
        """
        params = [f'%{search.lower()}%', f'%{search.lower()}%', role.lower()]

        # Log the query and parameters
        print("Executing Query:", query)
        print("With Parameters:", params)

        cursor.execute(query, params)
        users = cursor.fetchall()

        user_list = []
        for user in users:
            user_list.append({
                'full_name': user[0],
                'username': user[1],
                'role': user[2],
                'student_id': user[3],
                'department': user[4]
            })

        cursor.close()
        connection.close()

        return jsonify(user_list), 200
    
    except Exception as e:
        print("Error fetching users by role:", str(e))  # Log the exact error
        return jsonify({'message': f'Error: {str(e)}'}), 500



#route to edit users info
@app.route('/editUser', methods=['POST'])
def edit_user():
    try:
        data = request.json  # Capture the incoming data
        old_username = data.get('username')  # The existing username
        new_username = data.get('new_username')  # The new username
        full_name = data.get('full_name')  # Full name
        role = data.get('role')  # Role (student or faculty)
        student_id = data.get('student_id', None)  # Student ID (if role is student)
        department = data.get('department', None)  # Department (if role is faculty)

        # Validate the input
        if not full_name or not old_username or not new_username or not role:
            return jsonify({'message': 'Missing required fields'}), 400

        # Open a database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the user exists with the current username
        cursor.execute("SELECT * FROM users WHERE username = %s", (old_username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Check if the new username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (new_username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({'message': 'Username already exists'}), 400

        # Update the user's information based on their role
        if role == 'student':
            query = """
                UPDATE users
                SET full_name = %s, username = %s, role = %s, student_id = %s
                WHERE username = %s
            """
            cursor.execute(query, (full_name, new_username, role, student_id, old_username))
        elif role == 'faculty':
            query = """
                UPDATE users
                SET full_name = %s, username = %s, role = %s, department = %s
                WHERE username = %s
            """
            cursor.execute(query, (full_name, new_username, role, department, old_username))
        else:
            return jsonify({'message': 'Invalid role'}), 400

        # Commit the transaction
        connection.commit()

        # Close the database connection
        cursor.close()
        connection.close()

        return jsonify({'message': 'User updated successfully'}), 200
    
    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({'message': f'Error: {str(e)}'}), 500



# route to edit users passwords
@app.route('/editPassword', methods=['POST'])
def edit_password():
    try:
        data = request.json  # Capture the incoming data
        username = data.get('username')
        new_password = data.get('password')

        if not username or not new_password:
            return jsonify({'message': 'Username and password are required'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        # Update the password for the specified username
        query = """
            UPDATE users
            SET password = %s
            WHERE username = %s
        """
        cursor.execute(query, (new_password, username))  # Store plain text password
        connection.commit()

        # Close cursor and connection
        cursor.close()
        connection.close()

        return jsonify({'message': 'Password updated successfully'})
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


#route to delete users accounts
@app.route('/deleteUser', methods=['DELETE'])
def delete_user():
    try:
        data = request.json  # Capture the incoming data
        username = data.get('username')  # Get the username to delete

        if not username:
            return jsonify({'message': 'Username is required'}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if the user exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Proceed with deletion
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        connection.commit()

        # Close cursor and connection
        cursor.close()
        connection.close()

        return jsonify({'message': 'User deleted successfully'})
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

    
"""===================================ROUTES AND FUNCTIONS FOR FACULTY ACCOUNTS============================================="""

@app.route('/faculty_dashboard')
def faculty_dashboard():
    """Faculty dashboard with their specific subjects."""
    if 'username' not in session or session.get('role') != 'faculty':
        flash("Unauthorized access. Please log in.", 'error')
        return redirect(url_for('login'))
    app.logger.debug(f"Fetched Subjects: {subjects}")

    
    username = session['username']
    # Fetch only the subjects for the logged-in faculty
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subject WHERE faculty_username = %s", (username,))
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()

    # Log the subjects data to check if it contains any content
    app.logger.debug(f"Fetched Subjects: {subjects}")

    return render_template('faculty_dashboard.html', username=username, subjects=subjects)




@app.route('/add-subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        # Get form data
        year = request.form.get('year')
        subject_type = request.form.get('subjectType')
        subject_code = request.form.get('subjectCode')
        subject_name = request.form.get('subjectName')
        units = request.form.get('units')
        section = request.form.get('section')  # Get the new section field

        # Get the logged-in faculty username
        faculty_username = session['username']

        # Log the received data (for debugging purposes)
        app.logger.debug(f"Received Data: Year: {year}, Subject Type: {subject_type}, "
                         f"Subject Code: {subject_code}, Subject Name: {subject_name}, Units: {units}, Section: {section}")

        # Check if required fields are filled
        if subject_name and subject_code:
            try:
                # Get a database connection
                conn = get_db_connection()
                cursor = conn.cursor()

                # Query to get the user ID based on the faculty username
                cursor.execute('SELECT id FROM users WHERE username = %s', (faculty_username,))
                user_id = cursor.fetchone()

                # Ensure user exists
                if not user_id:
                    flash("User not found.", 'error')
                    return redirect(url_for('add_subject'))

                user_id = user_id[0]  # Extract the user ID

                # Check if a subject with the same name and section already exists
                cursor.execute(''' 
                    SELECT COUNT(*) FROM subject 
                    WHERE subject_name = %s AND section = %s
                ''', (subject_name, section))
                existing_subject = cursor.fetchone()

                # If a subject with the same name and section already exists, raise an error
                if existing_subject[0] > 0:
                    flash('You are trying to create a subject with the same name and section. Please choose a different section.', 'error')
                    return redirect(url_for('add_subject'))

                # Insert the new subject into the database, including the section
                cursor.execute(''' 
                    INSERT INTO subject (year, subject_name, subject_code, subject_type, units, faculty_username, section)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (year, subject_name, subject_code, subject_type, units, faculty_username, section))

                # Get the subject id of the newly inserted subject (to use in the subject_logs table)
                subject_id = cursor.lastrowid

                # Insert a log entry into the subject_logs table
                cursor.execute(''' 
                    INSERT INTO subject_logs (subject_id, modified_by, action)
                    VALUES (%s, %s, %s)
                ''', (subject_id, user_id, 'create'))  # Use user_id instead of faculty_username

                # Commit the transaction
                conn.commit()

                # Close the cursor and connection
                cursor.close()
                conn.close()

                # Flash a success message
                flash('Subject added successfully!', 'success')
                return redirect(url_for('faculty_dashboard'))  # Redirect to the faculty dashboard

            except mysql.connector.Error as err:
                # Log the error if it occurs
                app.logger.error(f"Error occurred: {err}")
                flash(f"An error occurred while inserting the data: {err}", 'error')

        else:
            # If required fields are missing, show an error
            flash("Subject name and code are required.", 'error')

    # If GET request, render the form
    return render_template('Add subject.html')



@app.route('/subject-list')
def subject_list():
    """Display the list of subjects for the logged-in faculty."""
    if 'username' not in session or session.get('role') != 'faculty':
        flash("Unauthorized access. Please log in.", 'error')
        return redirect(url_for('login'))
    
    username = session['username']
    # Fetch the subjects associated with the logged-in faculty
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subject WHERE faculty_username = %s", (username,))
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('subject_list.html', subjects=subjects)
    
@app.route('/get_subjects', methods=['GET'])
def get_subjects():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, subject_code, subject_name FROM subject")
    subjects = cursor.fetchall()

    # Return subjects as a JSON response
    return jsonify({'subjects': [{'id': subject[0], 'subject_code': subject[1], 'subject_name': subject[2]} for subject in subjects]})

    
# Get students enrolled in a subject
@app.route('/get_enrolled_students', methods=['GET'])
def get_enrolled_students():
    subject_code = request.args.get('subject_code')  # Get subject code from URL
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the subject ID based on the subject code
    cursor.execute("SELECT id FROM subject WHERE subject_code = %s", (subject_code,))
    subject = cursor.fetchone()

    if not subject:
        flash("Subject not found.", 'error')
        return redirect(url_for('login'))

    subject_id = subject[0]

    # Fetch all students enrolled in the subject
    cursor.execute('''
        SELECT users.username, users.id
        FROM student_subjects
        JOIN users ON student_subjects.student_id = users.id
        WHERE student_subjects.subject_id = %s
    ''', (subject_id,))
    enrolled_students = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'students': enrolled_students})

@app.route('/search_students')
def search_students():
    search_query = request.args.get('query', '')
    if not search_query:
        return jsonify({'students': []})
    
    # Create a database connection
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Search query (adjust as needed for your database)
    query = "SELECT id, username FROM users WHERE username LIKE %s AND role = 'student'"
    cursor.execute(query, ('%' + search_query + '%',))
    students = cursor.fetchall()
    
    # Close connection
    cursor.close()
    connection.close()

    return jsonify({'students': students})

@app.route('/enroll_student', methods=['POST'])
def enroll_student():
    student_id = request.form.get('student_id')
    subject_code = request.form.get('subject_code')

    if not student_id or not subject_code:
        return jsonify({'message': 'Student ID and Subject Code are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the student exists
        cursor.execute("SELECT id FROM users WHERE id = %s AND role = 'student'", (student_id,))
        student = cursor.fetchall()  # Fetch all results
        print("Student Found:", student)

        if not student:
            return jsonify({'message': 'Student not found'}), 404
        
        student_id = student[0][0]  # Extract student ID from the first result

        # Check if the subject exists
        cursor.execute("SELECT id FROM subject WHERE subject_code = %s", (subject_code,))
        subject = cursor.fetchall()  # Fetch all results
        print("Subject Found:", subject)

        if not subject:
            return jsonify({'message': 'Subject not found'}), 404

        subject_id = subject[0][0]  # Extract subject ID from the first result

        # Check for duplicate enrollment
        cursor.execute("SELECT * FROM student_subjects WHERE student_id = %s AND subject_id = %s",
                       (student_id, subject_id))
        duplicate = cursor.fetchall()  # Fetch all results
        print("Duplicate Enrollment Check:", duplicate)

        if duplicate:
            return jsonify({'message': 'Student already enrolled in this subject'}), 400

        # Enroll the student
        cursor.execute("INSERT INTO student_subjects (student_id, subject_id) VALUES (%s, %s)",
                       (student_id, subject_id))
        connection.commit()
        print("Enrollment Successful")

        return jsonify({'message': 'Student enrolled successfully!'})

    except mysql.connector.Error as err:
        connection.rollback()
        print("MySQL Error:", err)
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        connection.close()


# Remove a student from a subject
@app.route('/remove_student', methods=['POST'])
def remove_student():
    student_id = request.form.get('student_id')
    subject_code = request.form.get('subject_code')

    # Get the subject ID based on the subject code
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM subject WHERE subject_code = %s", (subject_code,))
    subject = cursor.fetchone()

    if not subject:
        flash("Subject not found.", 'error')
        return redirect(url_for('login'))

    subject_id = subject[0]

    # Remove the student from the student_subjects table
    cursor.execute('''
        DELETE FROM student_subjects
        WHERE student_id = %s AND subject_id = %s
    ''', (student_id, subject_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Student removed successfully!'})

# Edit grades for a student
@app.route('/edit_grade', methods=['POST'])
def edit_grade():
    student_id = request.form.get('student_id')
    subject_code = request.form.get('subject_code')
    quiz_grade = request.form.get('quiz_grade')
    exam_grade = request.form.get('exam_grade')

    # Get the subject ID based on the subject code
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM subject WHERE subject_code = %s", (subject_code,))
    subject = cursor.fetchone()

    if not subject:
        flash("Subject not found.", 'error')
        return redirect(url_for('login'))

    subject_id = subject[0]

    # Update the grades in the student_subjects table
    cursor.execute('''
        UPDATE student_subjects
        SET grade = %s
        WHERE student_id = %s AND subject_id = %s
    ''', (exam_grade, student_id, subject_id))  # Adjust for both quiz and exam grades if needed
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Grade updated successfully!'})




#route to update grades 
@app.route('/quiz_scores/<subject_code>')
def quiz_scores(subject_code):
    """Fetch and display quiz scores for the selected subject."""
    # Query the database to fetch quiz data based on subject_code
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT quiz_name, student_name, score, date FROM quiz_scores WHERE subject_code = %s", [subject_code])
    quiz_scores = cursor.fetchall()
    cursor.close()

    # Pass the quiz scores and subject code to the template
    return render_template('scores.html', subject_code=subject_code, quiz_scores=quiz_scores)

@app.route('/save-quiz-scores/<subject_code>', methods=['POST'])
def save_quiz_scores(subject_code):
    cursor = mysql.connection.cursor()

    for key, value in request.form.items():
        if key.startswith('score_'):
            quiz_id = key.split('_')[1]  # Extract the quiz ID from 'score_<id>'
            try:
                score = int(value)
                cursor.execute("""
                    UPDATE quiz_scores
                    SET score = %s
                    WHERE id = %s AND subject_code = %s
                """, (score, quiz_id, subject_code))
            except ValueError:
                flash("Invalid score input.", 'error')

    mysql.connection.commit()
    cursor.close()

    flash("Scores updated successfully.", 'success')
    return redirect(url_for('quiz_scores', subject_code=subject_code))

@app.route('/enrolled')
def enrolled_student():
    return render_template('/enrolled_students.html')

# For managing subjects
@app.route('/manage_subjects')
def manage_subjects():
    """Display the manage subjects page with subjects belonging to the logged-in faculty."""
    if 'username' not in session or session.get('role') != 'faculty':
        flash("Unauthorized access. Please log in.", 'error')
        return redirect(url_for('login'))
    
    username = session['username']
    
    # Fetch the subjects associated with the logged-in faculty
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subject WHERE faculty_username = %s", (username,))
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()

    # Render the manage subject page with the subjects
    return render_template('manage_subject.html', subjects=subjects)

# Test with dummy data
subjects = [
    (1, 'CHEM 111', 'CHEMISTRY FOR ENGINEERS', 'Lecture', 4, '1st Year'),
    (5, 'ELEC 111', 'FUNDAMENTAL IN ELECTRIC CIRCUITS', 'Lecture', 3, '1st Year')
]

@app.route('/update_subject/<subject_code>/<section>', methods=['GET', 'POST'])
def update_subject(subject_code, section):
    if 'username' not in session or session.get('role') != 'faculty':
        flash("Unauthorized access. Please log in.", 'error')
        return redirect(url_for('login'))

    # Fetch the subject to be updated using subject_code and section
    conn = get_db_connection()
    cursor = conn.cursor()

    # Modify query to handle NULL section explicitly
    if section == 'NULL':
        cursor.execute("SELECT * FROM subject WHERE subject_code = %s AND section IS NULL AND faculty_username = %s", 
                       (subject_code, session['username']))
    else:
        cursor.execute("SELECT * FROM subject WHERE subject_code = %s AND section = %s AND faculty_username = %s", 
                       (subject_code, section, session['username']))

    subject = cursor.fetchone()

    if not subject:
        cursor.close()
        flash("Subject not found or unauthorized.", 'error')
        return redirect(url_for('manage_subjects'))

    # Fetch the user_id based on the logged-in faculty's username
    cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
    user_id = cursor.fetchone()

    if not user_id:
        cursor.close()
        flash("User not found.", 'error')
        return redirect(url_for('manage_subjects'))

    user_id = user_id[0]  # Extract the user ID from the result

    if request.method == 'POST':
        # Get form data
        new_subject_code = request.form.get('subjectCode')
        subject_name = request.form.get('subjectName')
        subject_type = request.form.get('subjectType')
        units = request.form.get('units')
        year = request.form.get('year')
        new_section = request.form.get('section')  # Add a field for section if needed

        # Validate inputs (ensure none are empty)
        if not all([new_subject_code, subject_name, subject_type, units, year, new_section]):
            flash("All fields are required.", 'error')
            return render_template('update_subject.html', subject=subject)

        try:
            # Update the subject in the database
            if new_section == 'NULL':
                cursor.execute(''' 
                    UPDATE subject
                    SET subject_code = %s, subject_name = %s, subject_type = %s, units = %s, year = %s, section = NULL
                    WHERE subject_code = %s AND section IS NULL AND faculty_username = %s
                ''', (new_subject_code, subject_name, subject_type, units, year, subject_code, session['username']))
            else:
                cursor.execute(''' 
                    UPDATE subject
                    SET subject_code = %s, subject_name = %s, subject_type = %s, units = %s, year = %s, section = %s
                    WHERE subject_code = %s AND section = %s AND faculty_username = %s
                ''', (new_subject_code, subject_name, subject_type, units, year, new_section, subject_code, section, session['username']))
            conn.commit()

            # Log the update action
            cursor.execute(''' 
                INSERT INTO subject_logs (subject_id, modified_by, action)
                VALUES (%s, %s, %s)
            ''', (subject[0], user_id, 'update'))  # Use the correct user_id
            conn.commit()

            flash("Subject updated successfully!", 'success')
            return redirect(url_for('manage_subjects'))

        except Exception as e:
            conn.rollback()
            flash(f"Error updating subject: {str(e)}", 'error')
            return render_template('update_subject.html', subject=subject)

        finally:
            cursor.close()
            conn.close()

    return render_template('update_subject.html', subject=subject)


@app.route('/delete_subject/<subject_code>/<section>', methods=['POST'])
def delete_subject(subject_code, section):
    if 'username' not in session or session.get('role') != 'faculty':
        flash("Unauthorized access. Please log in.", 'error')
        return redirect(url_for('login'))

    # Establish database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the subject exists for this faculty, including section (handling NULL)
        if section == 'NULL':
            cursor.execute("SELECT * FROM subject WHERE subject_code = %s AND section IS NULL AND faculty_username = %s", 
                           (subject_code, session['username']))
        else:
            cursor.execute("SELECT * FROM subject WHERE subject_code = %s AND section = %s AND faculty_username = %s", 
                           (subject_code, section, session['username']))
        
        subject = cursor.fetchone()

        if not subject:
            flash("Subject not found or unauthorized.", 'error')
            return redirect(url_for('manage_subjects'))

        # Fetch the user_id based on the logged-in faculty's username
        cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
        user_id = cursor.fetchone()

        if not user_id:
            flash("User not found.", 'error')
            return redirect(url_for('manage_subjects'))

        user_id = user_id[0]  # Extract the user ID from the result

        # Log the delete action before deleting the subject
        cursor.execute(''' 
            INSERT INTO subject_logs (subject_id, modified_by, action)
            VALUES (%s, %s, %s)
        ''', (subject[0], user_id, 'delete'))  # Insert 'delete' action in logs
        conn.commit()  # Ensure the log is committed to the database

        # Now, delete the logs for this subject before deleting the subject itself
        cursor.execute("DELETE FROM subject_logs WHERE subject_id = %s", (subject[0],))
        conn.commit()

        # Now, delete the subject from the subject table using subject_code and section
        if section == 'NULL':
            cursor.execute("DELETE FROM subject WHERE subject_code = %s AND section IS NULL AND faculty_username = %s", 
                           (subject_code, session['username']))
        else:
            cursor.execute("DELETE FROM subject WHERE subject_code = %s AND section = %s AND faculty_username = %s", 
                           (subject_code, section, session['username']))
        conn.commit()

        flash("Subject deleted successfully!", 'success')
        return redirect(url_for('manage_subjects'))

    except Exception as e:
        conn.rollback()
        flash(f"Error deleting subject: {str(e)}", 'error')
        return redirect(url_for('manage_subjects'))

    finally:
        cursor.close()
        conn.close()



# Route for the Enrolled Students page
@app.route('/enrollment')
def enrollment():
    return render_template('enrolled_students.html')


# Route for the Enrolled Students page
@app.route('/enrolled_students')
def enrolled_students():
    subject_code = request.args.get('subject_code')  # Get the subject code from URL parameter
    return render_template('enrolled_students.html', subject_code=subject_code)

# Route to handle viewing enrolled students (redirects with subject code)
@app.route('/view_enrolled_students/<subject_code>')
def view_enrolled_students_redirect(subject_code):
    # Redirect to the enrolled students page with the subject_code as a URL parameter
    return redirect(url_for('viewing_enrolled_students', subject_code=subject_code))

@app.route('/viewing_enrolled_students/<subject_code>', methods=['GET'])
def view_enrolled_students(subject_code):
    # Get database connection
    conn = get_db_connection()
    if conn is None:
        return "Failed to connect to the database.", 500

    cursor = conn.cursor(dictionary=True)

    # Ensure only the logged-in faculty's students are shown
    faculty_username = session.get('username')  # Assuming the username is stored in session

    # Query to fetch data from student_subjects table based on subject_code and faculty
    cursor.execute("""
    SELECT
     users.full_name, 
     subject.subject_code, 
     subject.subject_name, 
     subject.faculty_username, 
     student_subjects.grade,
     users.id AS user_id
     FROM student_subjects 
     JOIN users ON student_subjects.student_id = users.id
     JOIN subject ON student_subjects.subject_id = subject.id 
    WHERE subject.subject_code = %s
      AND subject.faculty_username = %s
    """, (subject_code, faculty_username))

    enrolled_data = cursor.fetchall()

    # Close connection
    cursor.close()
    conn.close()

    # Pass data to HTML template
    return render_template('view_enrolled_students.html', students=enrolled_data, subject_code=subject_code)

@app.route('/edit_student/<int:student_id>/<subject_code>', methods=['GET', 'POST'])
def edit_student(student_id, subject_code):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch the student enrollment details including 'id'
    cursor.execute("""
    SELECT
        users.id AS user_id,
        users.full_name,
        subject.subject_code,
        subject.subject_name,
        subject.faculty_username,
        student_subjects.grade
    FROM student_subjects
    JOIN users ON student_subjects.student_id = users.id
    JOIN subject ON student_subjects.subject_id = subject.id
    WHERE subject.subject_code = %s AND users.id = %s
    """, (subject_code, student_id))

    enrollment = cursor.fetchone()  # Fetch a single row of the data
    cursor.close()

    if enrollment is None:
        flash("Enrollment not found.")
        return redirect(url_for('view_enrolled_students', subject_code=subject_code))
    
    if request.method == 'POST':
        new_grade = request.form['grade']  # Getting the new grade from the form
        
        # Update the student's enrollment grade in the database
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE student_subjects
        SET grade = %s
        WHERE student_id = %s AND subject_id = (SELECT id FROM subject WHERE subject_code = %s)
        """, (new_grade, student_id, subject_code))
        
        conn.commit()
        cursor.close()
        
        flash("Student enrollment updated successfully!")
        return redirect(url_for('view_enrolled_students', subject_code=subject_code))
    
    return render_template('edit_student.html', enrollment=enrollment)

@app.route('/delete_student/<int:student_id>', methods=['GET'])
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch the enrollment record using student_id and subject_code to get the enrollment record
        cursor.execute("""
            SELECT id FROM student_subjects
            WHERE student_id = %s AND subject_id = (SELECT id FROM subject WHERE subject_code = %s)
        """, (student_id, request.args.get('subject_code')))

        enrollment_id = cursor.fetchone()  # Use fetchone() to get a single result

        if enrollment_id:
            # Delete the student's enrollment from the database using student_subjects.id
            cursor.execute("DELETE FROM student_subjects WHERE id = %s", (enrollment_id[0],))  # Use the correct index
            conn.commit()
            flash("Student enrollment deleted successfully!")
        else:
            flash("Enrollment not found.")
    except Exception as e:
        conn.rollback()
        flash(f"Error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_enrolled_students', subject_code=request.args.get('subject_code')))

# function to view grade for faculty depends on subject type and year
def get_subject_by_code(subject_code):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM subject WHERE subject_code = %s"
            cursor.execute(query, (subject_code,))
            subject = cursor.fetchall()
            cursor.close()
            connection.close()
            return subject
        except Error as e:
            print(f"Error fetching subject: {e}")
            return None
    return None

@app.route('/view_grades_for_faculty/<subject_code>')
def view_grades_for_faculty(subject_code):
    subjects = get_subject_by_code(subject_code)  # Fetch all matching subjects

    if subjects:
        for subject in subjects:  # Iterate over each matching subject
            if isinstance(subject, (tuple, list)) and len(subject) > 5:
                subject_type = subject[3].strip().lower()
                year = subject[5].replace(" ", "").strip().lower()

                print(f"Subject Type: {subject_type}, Year: {year}")

                if '1st' in year:
                    if subject_type == 'lecture':
                        print("Rendering 1LEC.html")
                        return render_template('1LEC.html', subject=subject)
                    elif subject_type == 'laboratory':
                        print("Rendering 1lab.html")
                        return render_template('1lab.html', subject=subject)
                    elif subject_type == 'lecture/laboratory':
                        print("Rendering 1lec/lab.html")
                        return render_template('1leclab.html', subject=subject)
                elif '2nd' in year:
                    if subject_type == 'lecture':
                        print("Rendering 2lec.html")
                        return render_template('2lec.html', subject=subject)
                    elif subject_type == 'laboratory':
                        print("Rendering 2lab.html")
                        return render_template('2lab.html', subject=subject)
                    elif subject_type == 'lecture/laboratory':
                        print("Rendering 2leclab.html")
                        return render_template('2leclab.html', subject=subject)
                elif '3rd' in year:
                    if subject_type == 'lecture':
                        print("Rendering 3lec.html")
                        return render_template('3lec.html', subject=subject)
                    elif subject_type == 'laboratory':
                        print("Rendering 3lab.html")
                        return render_template('3lab.html', subject=subject)
                    elif subject_type == 'lecture/laboratory':
                        print("Rendering 3leclab.html")
                        return render_template('3leclab.html', subject=subject)
                elif '4rth' in year:
                    if subject_type == 'lecture':
                        print("Rendering 4lec.html")
                        return render_template('4lec.html', subject=subject)
                    elif subject_type == 'laboratory':
                        print("Rendering 4lab.html")
                        return render_template('4lab.html', subject=subject)
                    elif subject_type == 'lecture/laboratory':
                        print("Rendering 4leclab.html")
                        return render_template('4leclab.html', subject=subject)
    else:
        print(f"Unexpected result from get_subject_by_code: {subjects}")
        return jsonify({'error': 'Subject not found or invalid result'})

    return jsonify({'error': 'No matching subject type or year'})




# Fetch students by subject
@app.route('/get_students_by_subject', methods=['GET'])
def get_students_by_subject():
    subject_id = request.args.get('subject_id')  # Get subject ID from the request
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Query to fetch student names based on the subject_id
    query = """
        SELECT users.name 
        FROM users 
        JOIN student_subjects ON users.id = student_subjects.student_id
        WHERE student_subjects.subject_id = %s
    """
    cursor.execute(query, (subject_id,))
    students = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return jsonify(students)

# Sample route for the grading system form
@app.route('/')
def index():
    conn = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Fetch students from 'users' table
            cursor.execute("SELECT id, name FROM users WHERE role = 'student'")
            students = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return render_template('1lab.html', students=students)
        except Error as e:
            print(f"Error during query execution: {e}")
            return "Error fetching data from the database."
    else:
        return "Failed to connect to the database."



# Route for faculty password change
@app.route('/change_password_faculty')
def change_password_faculty():
    return render_template('/faculty_change_password.html')


@app.route('/update-password', methods=['POST'])
def update_password_api():
    # Get data from the request
    data = request.json

    current_password = data.get('current_password')
    new_password = data.get('new_password')

    # Ensure passwords are provided
    if not current_password or not new_password:
        return jsonify({'message': 'Current and new password are required'}), 400

    # Debugging: Print session info
    print(f"Session Info: {session}")

    # Check if the user is logged in and is a faculty
    if 'username' not in session or session.get('role') not in ['faculty', 'student']:
        return jsonify({'message': 'Unauthorized'}), 403

    username = session['username']
    
    # Retrieve the user's data from the database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        stored_password = result[0]

        # Verify if the current password matches the stored plain text
        if stored_password != current_password:
            return jsonify({'message': 'Current password is incorrect'}), 400

        # Update the password in the database (plain text)
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Password updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


"""ROUTES AND FUNCTIONS FOR STUDENTS ACCOUNTS"""

@app.route('/student_dashboard')
def student_dashboard():
    """Student dashboard."""
    if 'username' not in session or session.get('role') != 'student':
        flash("Unauthorized access. Please log in.", 'error')
        return redirect(url_for('login'))
    return render_template('student_dashboard.html', username=session['username'])

"=========================================================================================================================="
import traceback
@app.route('/view_enrolled_subjects')
def view_enrolled_subjects():
    # Get the username from the session
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))  # Redirect to login if no username in session

    # Debug: Check the username
    print("Using username:", username)

    # Connect to MySQL database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Query to fetch subjects with numerical rating first
        cursor.execute("""
            SELECT 
                sub.subject_name, 
                ss.midterm_grade, 
                ss.tentative_grade, 
                ss.semestral_grade,
                ss.numerical_rating,
                ss.descriptive_rating,
                ss.remarks_rating
            FROM student_subjects ss
            JOIN subject sub ON ss.subject_id = sub.id
            JOIN users u ON u.id = ss.student_id
            WHERE u.username = %s
        """, (username,))
        
        subjects = cursor.fetchall()  # Fetch the results
        print("Query result:", subjects)  # Debug: Show subjects found
        
    except Exception as e:
        print(f"Error occurred: {e}")
        subjects = []
    finally:
        cursor.close()
        conn.close()

    # Pass the subjects to the template
    return render_template('view_grades_student.html', subjects=subjects)


@app.route('/success')
def success():
    return "Grades saved successfully!"

@app.route('/save_grades', methods=['POST'])
def save_grades():
    data = request.json
    subject_code = data.get('subjectCode')
    grades = data.get('grades', [])

    print('Received grades data:', grades)  # Log received data

    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(buffered=True)

        # Fetch subject_id based on subject code
        cursor.execute("SELECT id FROM subject WHERE subject_code = %s", (subject_code,))
        subject_id = cursor.fetchone()
        if not subject_id:
            print(f"Subject not found: {subject_code}")  # Log missing subject
            return jsonify({'message': f'Subject not found: {subject_code}'}), 400
        subject_id = subject_id[0]

        for grade in grades:
            student_name = grade['studentName']
            midterm_grade = grade['midtermTransmuted']
            final_term_grade = grade['finalTransmuted']
            final_grade = grade['finalGrade']
            numerical_rating = grade['numericalRating']
            descriptive_rating = grade['descriptiveRating']
            remarks_rating = grade['remarksRating']

            # Fetch student_id based on student name
            cursor.execute("SELECT id FROM users WHERE full_name = %s", (student_name,))
            student_id = cursor.fetchone()
            if not student_id:
                print(f"Student not found: {student_name}")  # Log missing student
                continue  # Skip if student not found
            student_id = student_id[0]

            print(f"Inserting/updating grade for student_id {student_id}, subject_id {subject_id}")

            # Check if the student is already enrolled in the subject
            cursor.execute("SELECT id FROM student_subjects WHERE student_id = %s AND subject_id = %s", (student_id, subject_id))
            enrollment = cursor.fetchone()

            if enrollment:
                # Update the existing enrollment
                cursor.execute("""
                    UPDATE student_subjects
                    SET midterm_grade = %s, tentative_grade = %s, semestral_grade = %s, numerical_rating = %s, descriptive_rating = %s, remarks_rating = %s
                    WHERE student_id = %s AND subject_id = %s
                """, (midterm_grade, final_term_grade, final_grade, numerical_rating, descriptive_rating, remarks_rating, student_id, subject_id))
            else:
                # Insert a new enrollment (fixed VALUES mismatch)
                cursor.execute("""
                    INSERT INTO student_subjects (student_id, subject_id, midterm_grade, tentative_grade, semestral_grade, numerical_rating, descriptive_rating, remarks_rating)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (student_id, subject_id, midterm_grade, final_term_grade, final_grade, numerical_rating, descriptive_rating, remarks_rating))

        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Grades saved successfully'}), 200
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Failed to save grades: {str(e)}")  # Log the error
        return jsonify({'message': f'Failed to save grades: {str(e)}'}), 500

    

@app.route('/update-password-student')
def update_password_page():
    return render_template('change-password.html')

@app.route('/student_dashboard')
def back():
    return render_template ('/student_dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',
    'database': 'new_pygrade'
}

# Function to get database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

@app.route('/get_enrollment_data')
def get_enrollment_data():
    subject_code = request.args.get('subject_code')  # Get the subject code from the query parameters
    
    # Query to get student names and associated subjects
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT
            users.full_name AS student_name,
            subjects.subject_code,
            subjects.subject_name
        FROM student_subjects
        JOIN users ON student_subjects.student_id = users.id
        JOIN subjects ON student_subjects.subject_id = subjects.id
        WHERE subjects.subject_code = %s AND users.role = 'student'
    """, (subject_code,))
    
    # Fetch all the results
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Return the data as JSON
    return jsonify(students)

@app.route('/')
def index():
    subject_code = 'CS101'  # You can dynamically get this value based on the context
    
    return render_template('index.html', subject_code=subject_code)

if __name__ == '__main__':
    app.run(debug=True)

