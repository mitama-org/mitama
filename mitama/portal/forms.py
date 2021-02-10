from mitama.app.forms import Form

class LoginForm(Form):
    screen_name = Field(label="ログイン名", required)
    password = Field(label="パスワード", required)

class RegisterForm(Form):
    icon = FileField(label="プロフィール画像")
    screen_name = Field(label="ログイン名", required)
    name = Field(label="名前", required)
    password = Field(label="パスワード", required)

class InviteForm(Form):
    icon = FileField(label="プロフィール画像")
    name = Field(label="名前", required)
    screen_name = Field(label="ログイン名", required)
    editable = Field(label="プロフィールの変更を許可")

class UserUpdateForm(Form):
    icon = FileField(label="プロフィール画像")
    name = Field(label="名前")
    screen_name = Field(label="ログイン名")

class GroupCreateForm(Form):
    icon = FileField(label="プロフィール画像")
    name = Field(label="名前")
    screen_name = Field(label="ドメイン名")
    parent = Field(label="親グループ")

class GroupUpdateForm(Form):
    icon = FileField(label="プロフィール画像")
    name = Field(label="名前")
    screen_name = Field(label="ドメイン名")
    parent = Field(label="親グループ")

class AppUpdateForm(Form):
    prefix = Field(label="配信先", required)
