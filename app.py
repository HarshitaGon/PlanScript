import os
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import login_required, current_user
from models import db  # 👈 import User model for authentication
from models.user import User  # ✅ User model
from models.todo import Todo    # ✅ Todo model
from auth.routes import auth_bp   # ✅ import the Blueprint#
from flask_migrate import Migrate

app = Flask(__name__)

# Absolute path for DB
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "database.db")

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SECRET_KEY'] = 'key'  # ✅ moved to standard config pattern
db.init_app(app)

app.register_blueprint(auth_bp)

migrate = Migrate(app, db)


# ✅ Setup Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # If unauthorized, redirect to this route
login_manager.init_app(app)

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
            todo = Todo(title=title, status=status, user_id = current_user.id)
            db.session.add(todo)
            db.session.commit()
            flash('Todo item added successfully', 'success')
        else:
            todo = Todo.query.get(todo_id)
            if todo and todo.user_id == current_user.id:
                todo.title = title
                todo.status = status
                db.session.commit()
                flash('Todo item updated successfully', 'success')

            else:
                flash('Unauthorized', 'danger')

        return redirect(url_for('index'))

    todo = None
    if todo_id is not None:
        todo = Todo.query.get(todo_id)
        if todo and todo.user_id != current_user.id:        # ✅ restrict access
            flash("Not authorized", "danger")
            return redirect(url_for('index'))

    # ✅ Show only logged-in user's todos
    todos = Todo.query.filter_by(user_id = current_user.id).order_by(Todo.id.desc()).all()

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
    todo = Todo.query.get_or_404(todo_id)

    # Step 1: Check if todo belongs to current user
    if todo.user_id != current_user.id:
        flash("⚠️ You are not authorized to delete this task.", "danger")
        return redirect(url_for('index'))

    # Step 2: If valid, proceed to delete
    db.session.delete(todo)
    db.session.commit()
    flash('Todo item deleted successfully', 'success')

    return redirect(url_for('index'))


@app.route('/update_status/<int:todo_id>', methods=['POST'])
@login_required
def update_status(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    # ✅ Step 1: Check ownership
    if todo.user_id != current_user.id:
        flash("⚠️ You are not authorized to update this task.", "danger")
        return redirect(url_for('index'))

    # ✅ Step 2: Update only if status is valid
    new_status = request.form.get('status')
    if new_status in ['todo', 'progress', 'completed']:
        todo.status = new_status
        db.session.commit()
        flash('Task status updated!', 'success')

    else:
        flash("Invalid status update.", "danger")
    return redirect(url_for('index'))

# ✅ Import authentication routes from routes.py
from auth.routes import *  # 👈 This pulls in /login, /register, /logout

# ✅ Start the app
if __name__ == '__main__':
    app.run(debug=True)