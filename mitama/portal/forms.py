from mitama.app.forms import Form, FileField, Field
from mitama.noimage import load_noimage_group, load_noimage_user


class LoginForm(Form):
    screen_name = Field(label="ログイン名", required=True)
    password = Field(label="パスワード", required=True)


class RegisterForm(Form):
    icon = FileField(label="プロフィール画像", initial=load_noimage_user())
    screen_name = Field(label="ログイン名", required=True)
    name = Field(label="名前", required=True)
    password = Field(label="パスワード", required=True)


class InviteForm(Form):
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
    admin = Field(initial=False)
    user_create = Field(initial=False)
    user_update = Field(initial=False)
    user_delete = Field(initial=False)
    group_create = Field(initial=False)
    group_update = Field(initial=False)
    group_delete = Field(initial=False)


class AppUpdateForm(Form):
    prefix = Field(label="配信先", required=True)
