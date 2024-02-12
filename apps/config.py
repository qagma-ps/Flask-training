from pathlib import Path

basedir = Path(__file__).parent.parent


# BaseConfigクラスを作成する
class BaseConfig:
    SECRET_KEY = "WRK24LD2OoxiHPT"


# BaseConfigクラスを継承してLocalCongigクラスを作成する
class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path(__file__).parent.parent/'local.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATION = False
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path(__file__).parent.parent/'local.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATION = False
    WTF_CSRF_ENABLED = False


# config辞書にマッピングする
config = {
    "testing": TestingConfig,
    "local": LocalConfig,
}
