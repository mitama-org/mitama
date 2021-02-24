import os
from base64 import b64encode
from pathlib import Path

import magic


def load_noimage_app():
    """アプリのNoImage画像を取得します"""
    noimage_app_path = (
        Path(os.path.dirname(__file__)) / "app/static/noimage_app.png"
    )
    with open(noimage_app_path, "rb") as f:
        noimage_app = f.read()
    return noimage_app


def load_noimage_user():
    """ユーザーのNoImage画像を取得します"""
    noimage_user_path = (
        Path(os.path.dirname(__file__)) / "app/static/noimage_user.png"
    )

    with open(noimage_user_path, "rb") as f:
        noimage_user = f.read()
    return noimage_user


def load_noimage_group():
    """グループのNoImage画像を取得します"""
    noimage_group_path = (
        Path(os.path.dirname(__file__)) / "app/static/noimage_group.png"
    )

    with open(noimage_group_path, "rb") as f:
        noimage_group = f.read()
    return noimage_group
