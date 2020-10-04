from pathlib import Path
import magic, os
from mitama.conf import get_from_project_dir
from base64 import b64encode

def load_noimage_app():
    '''アプリのNoImage画像を取得します'''
    config = get_from_project_dir()
    if (config._project_dir / "noimage_app").is_file():
        noimage_app_path = config._project_dir / "static/noimage_app.png"
    else:
        noimage_app_path = Path(os.path.dirname(__file__)) / "app/static/noimage_app.png"
    with open(noimage_app_path, "rb") as f:
        noimage_app = f.read()
    return noimage_app

def load_noimage_user():
    '''ユーザーのNoImage画像を取得します'''
    config = get_from_project_dir()
    if (config._project_dir / "noimage_user").is_file():
        noimage_user_path = (config._project_dir / "static/noimage_user.png")
    else:
        noimage_user_path = (Path(os.path.dirname(__file__)) / "app/static/noimage_user.png")

    with open(noimage_user_path, "rb") as f:
        noimage_user = f.read()
    return noimage_user

def load_noimage_group():
    '''グループのNoImage画像を取得します'''
    config = get_from_project_dir()
    if (config._project_dir / "noimage_group").is_file():
        noimage_group_path = (config._project_dir / "static/noimage_group.png")
    else:
        noimage_group_path = (Path(os.path.dirname(__file__)) / "app/static/noimage_group.png")

    with open(noimage_group_path, "rb") as f:
        noimage_group = f.read()
    return noimage_group

