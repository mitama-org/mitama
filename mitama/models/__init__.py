#!/usr/bin/python
"""ノード定義

    * UserとGroupのモデル定義を書きます。
    * 関係テーブルのモデル実装は別モジュールにしようかと思ってる
    * sqlalchemyのベースクラスを拡張したNodeクラスに共通のプロパティを載せて、そいつらをUserとGroupに継承させてます。

Todo:
    * sqlalchemy用にUser型とGroup型を作って、↓のクラスをそのまま使ってDB呼び出しできるようにしたい
"""

from .core_db import db
from .nodes import (
    User,
    Group,
    Node,
    UserGroup,
    UserInvite,
    AuthorizationError,
    Role,
    InnerRole,
    PushSubscription
)
from .permissions import permission, inner_permission


Permission = permission(db, [
    {
        "name": "権限管理",
        "screen_name": "admin"
    },
    {
        "name": "グループ作成",
        "screen_name": "create_group",
    },
    {
        "name": "グループ更新",
        "screen_name": "update_group",
    },
    {
        "name": "グループ削除",
        "screen_name": "delete_group",
    },
    {
        "name": "ユーザー作成",
        "screen_name": "create_user",
    },
    {
        "name": "ユーザー更新",
        "screen_name": "update_user",
    },
    {
        "name": "ユーザー削除",
        "screen_name": "delete_user",
    }
])

InnerPermission = inner_permission(db, [
    {
        "name": "グループ管理",
        "screen_name": "admin"
    },
    {
        "name": "ユーザー追加",
        "screen_name": "add_user",
    },
    {
        "name": "ユーザー削除",
        "screen_name": "remove_user"
    },
    {
        "name": "グループ追加",
        "screen_name": "add_group"
    },
    {
        "name": "グループ削除",
        "screen_name": "remove_group"
    }
])


def is_admin(node):
    return Permission.is_accepted('admin', node)


db.create_all()


__all__ = [
    User,
    Group,
    Node,
    UserGroup,
    UserInvite,
    AuthorizationError,
    Role,
    InnerRole,
    Permission,
    InnerPermission,
    PushSubscription,
    permission,
    inner_permission,
]
