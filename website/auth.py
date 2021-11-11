from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("Logged in successfully.", category="success")
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        is_email_existed = User.query.filter_by(email=email).first()
        is_username_existed = User.query.filter_by(username=username).first()

        if is_email_existed:
            flash("Email is already used.", category="error")
        elif is_username_existed:
            flash("Username is already used.", category="error")
        elif len(username) < 2:
            flash("Username must be at least 2 characters.", category="error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.", category="error")
        elif password != confirm_password:
            flash("Passwords don't match", category="error")
        else:
            new_user = User()
            new_user.email = email
            new_user.username = username
            new_user.password = generate_password_hash(password, method="sha256")
            db.session.add(new_user)
            db.session.commit()
            flash("User created", category="success")
            login_user(new_user, remember=True)
            return redirect(url_for("views.home"))

    return render_template("sign-up.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))
