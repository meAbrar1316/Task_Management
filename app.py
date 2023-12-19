from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import logging


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=2)
db = SQLAlchemy(app)
jwt = JWTManager(app)

log_file_path = 'app.log'
logging.basicConfig(filename=log_file_path, level=logging.DEBUG)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, nullable=False)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    logging.debug(f"Attempting login for user: {username}")

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        access_token = create_access_token(identity=user.id)
        logging.info(f"User {username} logged in successfully")
        return jsonify(access_token=access_token), 200
    else:
        logging.warning(f"Login failed for user: {username}")
        return jsonify(message='Invalid credentials'), 401
        

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    current_user = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=current_user).all()
    task_list = []
    for task in tasks:
        task_list.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
        })
    logging.info(f"Tasks fetched successfully")
    return jsonify(tasks=task_list), 200

@app.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    task = Task.query.get(task_id)

    if task is None:
        logging.warning(f"Task not found")
        return jsonify({'error': 'Task not found'}), 404
    logging.info(f"Task details fetched successfully")
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
    }), 200

@app.route('/tasks', methods=['POST'])
@jwt_required()
def add_task():
    current_user = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    new_task = Task(title=title, description=description, user_id=current_user)
    db.session.add(new_task)
    db.session.commit()
    logging.info(f"Task added successfully")
    return jsonify(message='Task added successfully'), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def edit_task(task_id):
    current_user = get_jwt_identity()
    task = Task.query.get(task_id)

    if task.user_id != current_user:
        logging.warning(f"Unauthorized access")  
        return jsonify(message='Unauthorized'), 401

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    task.title = title
    task.description = description
    db.session.commit()
    logging.info(f"Task updated successfully")
    return jsonify(message='Task updated successfully'), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user = get_jwt_identity()
    task = Task.query.get(task_id)

    if task.user_id != current_user:
        logging.warning(f"Unauthorized access")  
        return jsonify(message='Unauthorized'), 401

    db.session.delete(task)
    db.session.commit()
    logging.info(f"Task deleted successfully")
    return jsonify(message='Task deleted successfully'), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(Exception)
def handle_error(e):
    logging.error(f"An error occurred: {str(e)}")
    return jsonify(error=str(e)), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='testuser').first():
            dummy_user = User(username='testuser', password='testpassword')
            db.session.add(dummy_user)
            db.session.commit()
    app.run(debug=True, host='0.0.0.0', port=8001)