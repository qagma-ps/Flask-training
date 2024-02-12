from flask import Blueprint, redirect, render_template, url_for

from apps.app import db
from apps.crud.forms import UserForm
from apps.crud.models import User

# create crud app using Blueprint
crud = Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static",
)


# return index.html via index endpoint
@crud.route("/")
def index():
    return render_template("crud/index.html")


@crud.route("/sql")
def sql():
    db.session.query(User).filter_by(id=2, username="admin").all()
    return "コンソールログを確認してください。"


@crud.route("/users/new", methods=["GET", "POST"])
def create_user():
    # UserForm instance
    form = UserForm()
    # Validate form value
    if form.validate_on_submit():
        # Create user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        # Register user and commit
        db.session.add(user)
        db.session.commit()
        # Redirect to user list screen
        return redirect(url_for("crud.users"))
    return render_template("crud/create.html", form=form)


@crud.route("/users")
def users():
    """ユーザーの一覧を取得する。"""
    users = User.query.all()
    return render_template("crud/index.html", users=users)


@crud.route("/users/<user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    form = UserForm()

    # Get user data using User model
    user = User.query.filter_by(id=user_id).first()

    # Update user if a form is submitted, adn redirect to user list screen
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.users"))

    # In case of GET, return html
    return render_template("crud/edit.html", user=user, form=form)


@crud.route("/users/<user_id>/delete", methods=["POST"])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("crud.users"))
