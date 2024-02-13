from flask import Blueprint, render_template

from apps.app import db
from apps.crud.models import User
from apps.detector.models import UserImage

# Specify template_folter ( but not static )
dt = Blueprint("detector", __name__, template_folder="templates")


# make endpoint using dt app
@dt.route("/")
def index():
    # Fetch image list by joing User and UserImage table
    user_images = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )

    return render_template("detector/index.html", user_images=user_images)
