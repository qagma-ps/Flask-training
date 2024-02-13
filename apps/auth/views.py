from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from apps.app import db
from apps.auth.forms import LoginForm, SignUpForm
from apps.crud.models import User

# generate auth using Blueprint
auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static",
)


# generate index endpoint
@auth.route("/")
def index():
    return render_template("/auth/index.html")


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    # make SignUpForm instance
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )

        # duplicate check of email address
        if user.is_duplicate_email():
            flash("指定のメールアドレスは登録済みです。")
            return redirect(url_for("auth.signup"))

        # Register user information
        db.session.add(user)
        db.session.commit()
        # store user information to session
        login_user(user)
        # Redirect to user list page if GET parameter doesn't have next key and value
        # Chage redirect enpoint into detector.index
        next_ = request.args.get("next")
        if next_ is None or not next_.startswith("/"):
            next_ = url_for("detector.index")
        return redirect(next_)
    return render_template("auth/signup.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Get user information using email address
        user = User.query.filter_by(email=form.email.data).first()

        # Allow login if user exists and password matches
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for("detector.index"))

        # Set a message when login failed
        flash("メールアドレスかパスワードが不正です。")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
