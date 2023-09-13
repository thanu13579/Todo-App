from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests
from flask_mysqldb import MySQL
from flask_restful import Resource, reqparse, Api

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# mysql = MySQL(app)
import pypyodbc as odbc
connection_string="Driver={ODBC Driver 18 for SQL Server};Server=tcp:todo-list-server.database.windows.net,1433;Database=todo-list;Uid=sohaib;Pwd=alpha122-;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
conn = odbc.connect(connection_string)
# Routes

@app.route('/')
def index():
    return redirect('/signup')

@app.route('/check')
def check():
    return jsonify({'msg': "mubarak ho"})

# Define the parser for request parameters
# parser = reqparse.RequestParser()
# parser.add_argument('username')
# parser.add_argument('task_id')
app.secret_key = 'uwehfewiuhiwuhewibdjuiwehiu'

# Initialize Flask-RESTful
api = Api(app)
# API endpoint to get a user's to-do list
class TodoListResource(Resource):
    def __init__(self):
        # Initialize the database connection
        connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:todo-list-server.database.windows.net,1433;Database=todo-list;Uid=sohaib;Pwd=alpha122-;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        self.conn = odbc.connect(connection_string)

    def get(self, username):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT id, todo, complete_status FROM todos WHERE user_id = (SELECT id FROM users WHERE username = ?)",
                [username]
            )
            todos = cursor.fetchall()
            cursor.close()

            # Prepare the JSON response
            todo_list = []
            for todo in todos:
                todo_list.append({
                    'id': todo[0],
                    'todo': todo[1],
                    'complete_status': bool(todo[2])
                })

            return jsonify({'todos': todo_list})

        except Exception as e:
            return jsonify({'error': 'Failed to fetch to-do list'}), 500

    def post(self):
        # This is where you can handle POST requests, if needed.
        # You can create a new to-do item here.
        pass

    def put(self):
        # This is where you can handle PUT requests, if needed.
        # You can update an existing to-do item here.
        pass

    def delete(self):
        # This is where you can handle DELETE requests, if needed.
        # You can delete a to-do item here.
        pass

# Add the resource to your API
api.add_resource(TodoListResource, '/api/todo-list/<string:username>')

class TodoListResourceId(Resource):
    def __init__(self):
        # Initialize the database connection
        connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:todo-list-server.database.windows.net,1433;Database=todo-list;Uid=sohaib;Pwd=alpha122-;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        self.conn = odbc.connect(connection_string)

    def get(self, username, task_id):
        try:

            cursor = self.conn.cursor()
            cursor.execute(
                    "SELECT id, todo, complete_status FROM todos WHERE user_id = (SELECT id FROM users WHERE username = ?) AND id = ?",
                    [username, task_id]
                )

            todos = cursor.fetchall()
            cursor.close()

            # Prepare the JSON response
            todo_list = []
            for todo in todos:
                todo_list.append({
                    'id': todo[0],
                    'todo': todo[1],
                    'complete_status': bool(todo[2])
                })

            return jsonify({'todos': todo_list})

        except Exception as e:
            return jsonify({'error': 'Failed to fetch to-do list'}), 500

    # ... (other methods for POST, PUT, DELETE)

# Add a new API endpoint route for getting a specific task by task_id
api.add_resource(TodoListResourceId, '/api/todo-list/<string:username>/<int:task_id>')

    
@app.route('/todo-list')
def todo_list():
    if 'username' in session:
        username = session['username']
        cur = conn.cursor()
        cur.execute("SELECT id, todo, complete_status FROM todos WHERE user_id = (SELECT id FROM users WHERE username = ?)", [username])
        todos = cur.fetchall()
        # print(todos[0][1])
        cur.close()
        return render_template('index.html', username=username, todos=todos)
    return redirect(url_for('signup'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = request.args.get("error")  # error msg

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if len(password) == 0 or len(email) == 0:
            return redirect(url_for('signin', error="Invalid Input Field Length"))

        sql = "SELECT COUNT(*) FROM users WHERE email=? AND password=?"
        sql2 = "SELECT username FROM users WHERE email=? AND password=?"

        data = (email, password)

        mycursor = conn.cursor()

        try:
            # Execute the first query
            mycursor.execute(sql, data)
            result = mycursor.fetchall()

            if result[0][0] > 0:
                # Execute the second query
                mycursor = conn.cursor()
                mycursor.execute(sql2, data)
                username = mycursor.fetchall()[0][0]

                # Update session variables
                session["email"] = email
                session["username"] = username

                # Commit the changes
                conn.commit()

                return redirect(url_for("todo_list"))
            else:
                # Invalid user, go again to sign up page with error msg
                return redirect(url_for('signin', error="Invalid login"))

        except Exception as e:
            # Handle exceptions here, if necessary
            print(e)
            conn.rollback()

        finally:
            # Always close the cursor in a finally block to ensure it's closed
            mycursor.close()

    # Render the login page with the error message
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = request.args.get("error")  # error msg

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get('email')
        password = request.form.get('password')

        if len(password) == 0 or len(email) == 0 or len(username) == 0:
            return redirect(url_for('signup', error="Invalid Input Field Length"))

        # Check if email already exists
        email_check_sql = "SELECT COUNT(*) FROM users WHERE email=?"
        email_data = (email,)
        mycursor = conn.cursor()
        mycursor.execute(email_check_sql, email_data)
        email_result = mycursor.fetchall()

        # Check if username already exists
        username_check_sql = "SELECT COUNT(*) FROM users WHERE username=?"
        username_data = (username,)
        mycursor.execute(username_check_sql, username_data)
        username_result = mycursor.fetchall()

        conn.commit()

        if email_result[0][0] > 0:
            return redirect(url_for('signup', error="Email Already Exists"))
        
        elif username_result[0][0] > 0:
            return redirect(url_for('signup', error="Username Already Exists"))

        else:
                # if user with email doesn't exist already, we store values in database
                # and make a new user
                sql = "insert into users(username,email,password) values(?,?,?)"
                data = (username, email, password)
                # following lines execute sql query
                mycursor = conn.cursor()
                mycursor.execute(sql, data)
                conn.commit()
                return render_template('login.html', error=None)
    # when redirected from get request and url_for as in case of
    # invalid login ,then we have
    # a get request and below line is executed
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))

@app.route('/add_todo', methods=['POST'])
def add_todo():
    if 'username' in session:
        todo = request.form['todo']
        username = session['username']
        cur = conn.cursor()
        cur.execute("INSERT INTO todos (todo, user_id) VALUES (?, (SELECT id FROM users WHERE username = ?))", [todo, username])
        conn.commit()
        cur.close()
    return redirect(url_for('todo_list'))

@app.route('/toggle_todo/<int:todo_id>')
def toggle_todo(todo_id):
    if 'username' in session:
        cur = conn.cursor()
        # Use a CASE statement to toggle the complete_status
        cur.execute("UPDATE todos SET complete_status = CASE WHEN complete_status = 0 THEN 1 ELSE 0 END WHERE id = ?", [todo_id])
        conn.commit()
        cur.close()
    return redirect(url_for('todo_list'))

@app.route('/delete_todo/<int:todo_id>')
def delete_todo(todo_id):
    if 'username' in session:
        cur = conn.cursor()
        cur.execute("DELETE FROM todos WHERE id = ?", [todo_id])
        conn.commit()
        cur.close()
    return redirect(url_for('todo_list'))


# Route for modifying a task
@app.route('/modify_todo/<int:task_id>', methods=['GET', 'POST'])
def modify_todo(task_id):
    if request.method == 'POST':
        new_todo = request.form['new_todo']
        cursor = conn.cursor()
        cursor.execute("UPDATE todos SET todo = ? WHERE id = ?", (new_todo, task_id))
        conn.commit()
        cursor.close()
        return redirect('/todo-list')

    # Get the task to be modified
    cursor = conn.cursor()
    cursor.execute("SELECT todo FROM todos WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.commit()
    cursor.close()

    return render_template('modify.html', task=task, task_id=task_id)

# Add this route to render the modification form
@app.route('/modify_todo/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    if request.method == 'POST':
        new_todo = request.form['new_todo']
        cursor = conn.cursor()
        cursor.execute("UPDATE todos SET todo = ? WHERE id = ?", (new_todo, task_id))
        conn.commit()
        cursor.close()
        return redirect('/todo-list')

    return render_template('modify.html', task_id=task_id)

if __name__ == '__main__':
    app.run(debug=True)
