from pathlib import Path

from flask.helpers import get_root_path
from werkzeug.datastructures import FileStorage

from apps.detector.models import UserImage


def test_index(client):
    rv = client.get("/")
    assert "ログイン" in rv.data.decode()
    assert "画像新規登録" in rv.data.decode()


def signup(client, username, email, password):
    """サインアップする"""
    data = dict(username=username, email=email, password=password)
    return client.post("/auth/signup", data=data, follow_redirects=True)


def test_index_signup(client):
    """サインアップを実行する"""
    rv = signup(client, "test01", "test01@gmail.com", "test01")
    assert "test01" in rv.data.decode()

    rv = client.get("/")
    assert "ログアウト" in rv.data.decode()
    assert "画像新規登録" in rv.data.decode()


def test_upload_no_auth(client):
    rv = client.get("/upload", follow_redirects=True)
    # 画像アップロード画面にはアクセスできない。
    assert "アップロード" not in rv.data.decode()
    # ログイン画面にリダイレクトされる
    assert "メールアドレス" in rv.data.decode()
    assert "パスワード" in rv.data.decode()


def test_upload_signup_get(client):
    signup(client, "test01", "test01@gmail.com", "test01")
    rv = client.get("/upload")
    assert "アップロード" in rv.data.decode()


def upload_image(client, image_path):
    """画像をアップロードする"""
    image = Path(get_root_path("tests"), image_path)

    test_file = FileStorage(
        stream=open(image, "rb"),
        filename=Path(image_path).name,
        content_type="multipart/form-data",
    )

    data = dict(
        image=test_file,
    )
    return client.post("/upload", data=data, follow_redirects=True)


def test_upload_signup_post_validate(client):
    signup(client, "test01", "test01@gmail.com", "test01")
    rv = upload_image(client, "detector/testdata/test_invalid_file.txt")
    assert "サポートされていない画像形式です。" in rv.data.decode()


def test_upload_signup_post(client):
    signup(client, "test01", "test01@gmail.com", "password")
    rv = upload_image(client, "detector/testdata/test_valid_image.jpg")
    user_image = UserImage.query.first()
    assert user_image.image_path in rv.data.decode()


def test_detect_no_user_image(client):
    signup(client, "test01", "test01@gmail.com", "test01")
    upload_image(client, "detector/testdata/test_valid_image.jpg")
    # 存在しないIDを指定する。
    rv = client.post("/detect/notexistid", follow_redirects=True)
    assert "物体検知対象の画像が存在しません。" in rv.data.decode()


def test_detect(client):
    # Signup
    signup(client, "test01", "test01@gmail.com", "test01")
    # Upload image
    upload_image(client, "detector/testdata/test_valid_image.jpg")
    user_image = UserImage.query.first()

    # execute object detection
    rv = client.post(f"/detect/{user_image.id}", follow_redirects=True)
    user_image = UserImage.query.first()
    assert user_image.image_path in rv.data.decode()
    assert "dog" in rv.data.decode()


def test_detect_search(client):
    # signup
    signup(client, "test01", "test01@gmail.com", "test01")
    # upload image
    upload_image(client, "detector/testdata/test_valid_image.jpg")
    user_image = UserImage.query.first()

    # object detection
    client.post(f"/detect/{user_image.id}", follow_redirects=True)

    # search by keyword "dog"
    rv = client.get("/images/search?search=dog")
    # recognize if dog tag exists on image
    assert user_image.image_path in rv.data.decode()
    # recognize dog tag
    assert "dog" in rv.data.decode()

    # search by keyword "test"
    rv = client.get("/images/search?search=test")
    # recognize if images with dog tag doesn't exist
    assert user_image.image_path not in rv.data.decode()
    # recognize not dog tag
    assert "dog" not in rv.data.decode()


def test_delete(client):
    signup(client, "test01", "test01@gmail.com", "test01")
    upload_image(client, "detector/testdata/test_valid_image.jpg")

    user_image = UserImage.query.first()
    image_path = user_image.image_path
    rv = client.post(f"/images/delete/{user_image.id}", follow_redirects=True)
    assert image_path not in rv.data.decode()


def test_custom_error(client):
    rv = client.get("/notfound")
    assert "404 Not Found" in rv.data.decode()
