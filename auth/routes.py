from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash
from models import db
from models.user import User
from .forms import RegisterForm, LoginForm
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint("auth", __name__)

# ------------------- REGISTER ------------------- #

@auth_bp.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        print("✅ Form validated successfully")

        existing_user = User.query.filter_by(email = form.email.data).first()

        if existing_user:
            flash('Email already exists. Try logging in.', 'danger')
            return redirect(url_for('auth.register'))


        new_user = User(
            username = form.username.data,
            email = form.email.data
        )

        new_user.set_password(form.password.data)  # Hashing password

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful ! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    else:
        print("❌ Form NOT validated")
        print("Form Errors:", form.errors)  # 🪵 DEBUG THIS


    return render_template('register.html', form = form)


# ------------------- LOGIN ------------------- #

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        print("✅ Login Form validated")

        user = User.query.filter_by(username = form.username.data).first()

        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            login_user(user)  # 👈 important: tells Flask-Login the user is authenticated
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))         # Change to your actual dashboard route

        else:
            flash("Invalid username or password.", "danger")

    else:
        print("❌ Login Form NOT validated")
        print("Form Errors:", form.errors)

    return render_template('login.html', form=form)

# ------------------- LOGOUT ------------------- #

@auth_bp.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

