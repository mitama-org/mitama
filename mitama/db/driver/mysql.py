#!/usr/bin/python
"""sqliteのエンジン

    * プロジェクトのDBはプロジェクトのconfigから場所を取って参照する。
    * アプリのDBはアプリのフォルダ直下を参照する
"""

from sqlalchemy import create_engine


def get_engine():
    from mitama.conf import get_from_project_dir

    config = get_from_project_dir()
    return create_engine(
        "mysql://{}:{}@{}/{}?charset=utf8".format(
            config.database.user,
            config.database.password,
            config.database.host,
            config.database.db_name
        )
    )

