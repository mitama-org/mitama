from mitama.app.forms import Form, FileField, Field, empty_error, format_error
from mitama.noimage import load_noimage_group, load_noimage_user

class SetupForm(Form):
    email = Field(label="メールアドレス", required=True)

class WelcomeMessageForm(Form):
    welcome_message = Field(label="ウェルカムボード", required=True)

class LoginForm(Form):
    screen_name = Field(label="ログイン名", required=True)
    password = Field(label="パスワード", required=True)


class RegisterForm(Form):
    icon = FileField(label="プロフィール画像", initial=load_noimage_user())
    screen_name = Field(label="ログイン名", required=True)
    name = Field(label="名前", required=True)
    password = Field(label="パスワード", required=True)


class InviteForm(Form):
    email = Field(label="メールアドレス", required=True)
    icon = FileField(label="プロフィール画像", initial=load_noimage_user())
    name = Field(label="名前")
    screen_name = Field(label="ログイン名")
    editable = Field(label="プロフィールの変更を許可", initial=False)


class UserUpdateForm(Form):
    icon = FileField(label="プロフィール画像", initial=load_noimage_user())
    name = Field(label="名前", required=True)
    screen_name = Field(label="ログイン名")


class GroupCreateForm(Form):
    icon = FileField(label="プロフィール画像", initial=load_noimage_group())
    name = Field(label="名前", required=True)
    screen_name = Field(label="ドメイン名", required=True)
    parent = Field(label="親グループ")


class GroupUpdateForm(Form):
    icon = FileField(label="プロフィール画像", initial=load_noimage_group())
    name = Field(label="名前", required=True)
    screen_name = Field(label="ドメイン名", required=True)
    parent = Field(label="親グループ")
    roles = Field(label="役割", listed=True)


class AppUpdateForm(Form):
    prefix = Field(label="配信先", required=True)
