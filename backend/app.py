from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'Secret*9'  # Change this to a strong secret key
jwt = JWTManager(app)

# MySQL Configuration
app.config.from_pyfile('config.py')
mysql = MySQL(app)

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = mysql.connect
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except:
        return jsonify({"message": "Username already exists!"}), 400

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = mysql.connect
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user[1], password):
        access_token = create_access_token(identity=str(user[0]))
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid credentials!"}), 401

# Protected Route: Get Tasks
@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = int(get_jwt_identity())

    conn = mysql.connect
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
    tasks = cursor.fetchall()
    task_list = []
    for task in tasks:
        task_list.append({
            "id": task[0],
            "title": task[1],
            "description": task[2],
            "status": task[3],
            "created_at": task[4].strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(task_list)

# Protected Route: Create Task
@app.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data['title']
    description = data.get('description', '')

    conn = mysql.connect
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, description, user_id) VALUES (%s, %s, %s)", (title, description, user_id))
    conn.commit()
    return jsonify({"message": "Task created successfully!"}), 201

# Protected Route: Update Task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    status = data.get('status')

    conn = mysql.connect
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks 
        SET title = %s, description = %s, status = %s
        WHERE id = %s AND user_id = %s
    """, (title, description, status, task_id, user_id))
    conn.commit()
    return jsonify({"message": "Task updated successfully!"})

# Protected Route: Delete Task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()

    conn = mysql.connect
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
    conn.commit()
    return jsonify({"message": "Task deleted successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
