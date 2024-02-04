# Import Flask class
import logging
import os

from email_validator import EmailNotValidError, validate_email
from flask import (
    Flask,
    current_app,
    flash,
    g,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message

# Make Flask class Instance
app = Flask(__name__)
# Secret keyを追加
app.config["SECRET_KEY"] = "2AZZSMss3p50PbcY2hBsJ"
# ログレベルを設定
app.logger.setLevel(logging.DEBUG)
# リダイレクトを中断しないようにする。
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# DebugToolbarExtensionにアプリケーションをセットする。
toolbar = DebugToolbarExtension(app)

# Mailクラスのコンフィグを追加する。
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

# flask-mail拡張を登録する。
mail = Mail(app)

# クッキーの設定
# keyを指定する。
username = request.cookies.get("username")


# Mapping URL and function
@app.route("/", methods=["GET", "POST"])
def index():
    return "Hello, Flaskbook!"


@app.route("/hello/<name>", methods=["GET", "POST"], endpoint="hello-endpoint")
def hello(name):
    return f"Hello, {name}"


@app.route("/name/<name>")
def show_name(name):
    return render_template("index.html", name=name)


with app.test_request_context():
    # /
    print(url_for("index"))
    # /hello/world
    print(url_for("hello-endpoint", name="world"))
    # /name/Yuichiro?page=1
    print(url_for("show_name", name="Yuichiro", page="1"))

# current_app, gのテスト
ctx = app.app_context()
ctx.push()

print(current_app.name)

g.connection = "connection"
print(g.connection)

# requestのテスト
with app.test_request_context("/users?updated=true"):
    print(request.args.get("updated"))


# request formのテスト
@app.route("/contact")
def contact():
    # レスポンスオブジェクトを取得する
    response = make_response(render_template("contact.html"))
    # クッキーを設定する。
    response.set_cookie("flask-training key", "flask-training value")
    # セッションを設定する
    session["username"] = "Yuichiro"
    # レスポンスオブジェクトを返す
    return response


@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        # form属性を使ってフォームの値を取得する。
        username = request.form["username"]
        email = request.form["email"]
        description = request.form["description"]

        # 入力チェック
        is_valid = True

        if not username:
            flash("ユーザー名は必須です。")
            is_valid = False

        if not email:
            flash("メールアドレスは必須です。")
            is_valid = False

        try:
            validate_email(email)
        except EmailNotValidError:
            flash("メールアドレスの形式で入力してください。")
            is_valid = False

        if not description:
            flash("問い合わせ内容は必須です。")
            is_valid = False

        if not is_valid:
            return redirect(url_for("contact"))

        # メールを送る
        send_email(
            email,
            "問い合わせありがとうございました。",
            "contact_mail",
            username=username,
            description=description,
        )

        # contact エンドポイントへリダイレクトする
        flash(
            "問い合わせ内容はメールにて送信しました。問い合わせありがとうございます。"
        )
        return redirect(url_for("contact_complete"))

    return render_template("contact_complete.html")


def send_email(to, subject, template, **kwargs):
    """メールを送信する関数"""
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)
