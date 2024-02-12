from pathlib import Path

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from apps.config import config

# Make SQLAlchemy instance
db = SQLAlchemy()

# countermeasure for CSRF
csrf = CSRFProtect()


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

    return app
