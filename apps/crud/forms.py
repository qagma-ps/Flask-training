from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, length


# Form class of creating and editing user
class UserForm(FlaskForm):
    # Set username label and validation for a form
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名は必須です。"),
            length(max=30, message="30文字以内で入力してください。"),
        ],
    )
    # Set emal label and validation for a form
    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(message="メールアドレスは必須です。"),
            Email(message="メールアドレスの形式で入力してください。"),
        ],
    )
    # Set password label and validation for a form
    password = PasswordField(
        "パスワード",
        validators=[DataRequired(message="パスワードは必須です。")],
    )
    # Set submit text for a form
    submit = SubmitField("新規作成")
