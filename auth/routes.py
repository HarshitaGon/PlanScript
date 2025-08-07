from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash
from models import db
from models.user import User
from .forms import RegisterForm

auth_bp = Blueprint("auth", __name__)

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


# ✅ ADD THIS PLACEHOLDER LOGIN ROUTE TO FIX BuildError
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return "Login page coming soon"