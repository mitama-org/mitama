from mitama.app.forms import Form, FileField, Field, DictField, empty_error, format_error
from mitama.noimage import load_noimage_group, load_noimage_user


class SetupForm(Form):
    email = Field(label="メールアドレス", required=True)


class SettingsForm(Form):
    welcome_message = Field(label="ウェルカムボード", required=True)
    role_name = Field(label='役割名')
    permission = DictField(listed=True)
    inner_role_name = Field(label='グループ役割名')
    inner_permission = DictField(listed=True)


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
    roles = Field(label="役割", listed=True)
    screen_name = Field(label="ログイン名")
    editable = Field(label="プロフィールの変更を許可", initial=False)


class UserUpdateForm(Form):
    icon = FileField(label="プロフィール画像")
    name = Field(label="名前", required=True)
    screen_name = Field(label="ログイン名")
    roles = Field(label="役割", listed=True)


class SubscriptionForm(Form):
    action = Field(required=True)
    subscription = Field()


class UserPasswordUpdateForm(Form):
    password = Field(label="パスワード", required=True)
    password_ = Field(label="確認用パスワード", required=True)


class GroupCreateForm(Form):
    icon = FileField(label="プロフィール画像", initial=load_noimage_group())
    name = Field(label="名前", required=True)
    screen_name = Field(label="ドメイン名", required=True)
    parent = Field(label="親グループ")


class GroupUpdateForm(Form):
    icon = FileField(label="プロフィール画像")
    name = Field(label="名前", required=True)
    screen_name = Field(label="ドメイン名", required=True)
    parent = Field(label="親グループ")
    roles = Field(label="役割", listed=True)
    users = Field(listed=True)
    inner_roles = DictField(listed=True)
    new_user = Field()


class AppUpdateForm(Form):
    prefix = DictField(label="配信先", required=True)
