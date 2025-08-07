from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import login_required, current_user
from models import db  # 👈 import User model for authentication
from models.user import User  # ✅ User model
from auth.routes import auth_bp   # ✅ import the Blueprint#
from flask_migrate import Migrate



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'key'  # ✅ moved to standard config pattern
db.init_app(app)
# db = SQLAlchemy(app)

app.register_blueprint(auth_bp)


migrate = Migrate(app, db)


# ✅ Setup Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # If unauthorized, redirect to this route
login_manager.init_app(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='todo')  # ✅ New field

# ✅ Initialize database tables
with app.app_context():
    db.create_all()

# ✅ User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------
# Main Todo App Routes
# -----------------------

@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def index(todo_id=None):
    if request.method == 'POST':
        title = request.form.get('title')
        status = request.form.get('status') or 'todo'

        if todo_id is None:
            todo = Todo(title=title, status=status)  # 👈 default status
            db.session.add(todo)
            db.session.commit()
            flash('Todo item added successfully', 'success')
        else:
            todo = Todo.query.get(todo_id)
            if todo:
                todo.title = title
                todo.status = status
                db.session.commit()
                flash('Todo item updated successfully', 'success')

        return redirect(url_for('index'))

    todo = None
    if todo_id is not None:
        todo = Todo.query.get(todo_id)

    todos = Todo.query.order_by(Todo.id.desc()).all()

    # 👇 group by status
    todo_tasks = [t for t in todos if t.status == 'todo']
    progress_tasks = [t for t in todos if t.status == 'progress']
    completed_tasks = [t for t in todos if t.status == 'completed']

    return render_template(
        'index.html',
        user=current_user,
        todos=todos,
        todo=todo,
        todo_tasks=todo_tasks,
        progress_tasks=progress_tasks,
        completed_tasks=completed_tasks
    )


@app.route('/todo-delete/<int:todo_id>', methods=["POST"])
@login_required
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash('Todo item deleted successfully', 'success')

    return redirect(url_for('index'))


@app.route('/update_status/<int:todo_id>', methods=['POST'])
@login_required
def update_status(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    new_status = request.form.get('status')
    if new_status in ['todo', 'progress', 'completed']:
        todo.status = new_status
        db.session.commit()
        flash('Task status updated!', 'success')
    return redirect(url_for('index'))

# ✅ Import authentication routes from routes.py
from auth.routes import *  # 👈 This pulls in /login, /register, /logout

# ✅ Start the app
if __name__ == '__main__':
    app.run(debug=True)