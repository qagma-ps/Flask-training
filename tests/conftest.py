import os
import shutil

import pytest

from apps.app import create_app, db
from apps.crud.models import User
from apps.detector.models import UserImage, UserImageTag


@pytest.fixture
def app_data():
    return 3


# create fixture function
@pytest.fixture
def fixture_app():
    # Setup
    # specify "testing" for config
    app = create_app("testing")

    # Use database
    app.app_context().push()

    # create database table for testing
    with app.app_context():
        db.create_all()

    # create image upload directory for testing
    os.mkdir(app.config["UPLOAD_FOLDER"])

    # execute test
    yield app

    # cleanup procedure
    # delete records in user table
    User.query.delete()

    # delete records in user_image table
    UserImage.query.delete()

    # delete records in user_image_tags table
    UserImageTag.query.delete()

    # delete image upload directory for testing
    shutil.rmtree(app.config["UPLOAD_FOLDER"])

    db.session.commit()


# create fixture function to return Flask test client
@pytest.fixture
def client(fixture_app):
    # return flask test client
    return fixture_app.test_client()
