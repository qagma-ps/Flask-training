# from pathlib import Path

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from apps.config import config

# Make SQLAlchemy instance
db = SQLAlchemy()

# countermeasure for CSRF
csrf = CSRFProtect()

# Make LoginManager instance
login_manager = LoginManager()
# specify endpoint to redirect to login_view attribute when not logged in.
login_manager.login_view = "auth.signup"
# specify message shown after logged in of login_message attribute
# Firstly set void
login_manager.login_message = ""


# コンフィグのキーを渡す
# create_app function
def create_app(config_key):
    # Flask instance
    app = Flask(__name__)
    # config_keyにマッチする環境のコンフィグクラスを読み込む
    app.config.from_object(config[config_key])
    """
    # Configuration of app
    app.config.from_mapping(
        SECRET_KEY="WRK24LD2OoxiHPT",
        SQLALCHEMY_DATABASE_URI="sqlite:///"
        + f"{Path(__file__).parent.parent/'local.sqlite'}",
        SQLALCHEMY_TRACK_MODIFICATION=False,
        # Output sql text in a console log
        SQLALCHEMY_ECHO=True,
        # CSRF
        WTF_CSRF_SECRET_KEY="XEbaapDxteILMeL",
    )
    """
    # Register custom error screen
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    # connect SQLAlchemy and app
    db.init_app(app)
    # connect Migrate and app
    Migrate(app, db)
    # CSRF
    csrf.init_app(app)

    # import views from crud package
    from apps.crud import views as crud_views

    # register crud views using register_blueprint
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    # import views from auth package
    from apps.auth import views as auth_views

    # register auth views using register_blueprint
    app.register_blueprint(auth_views.auth, url_prefix="/auth")

    # connect login_manager with app
    login_manager.init_app(app)

    # import views from detector package
    from apps.detector import views as dt_views

    # register views dt using register_blueprint
    app.register_blueprint(dt_views.dt)

    return app


def page_not_found(e):
    """404 Not Found"""
    return render_template("404.html"), 404


def internal_server_error(e):
    """500 Internal Server Error"""
    return render_template("500.html"), 500
