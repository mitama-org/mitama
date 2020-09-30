#!/usr/bin/python
'''sqliteのエンジン

    * プロジェクトのDBはプロジェクトのconfigから場所を取って参照する。
    * アプリのDBはアプリのフォルダ直下を参照する
'''

from sqlalchemy import create_engine

def get_engine():
    from mitama.conf import get_from_project_dir
    config = get_from_project_dir()
    return create_engine('sqlite:///'+str(config._sqlite_db_path))

def get_test_engine():
    return create_engine('sqlite://')

def get_app_engine(appname):
    from mitama.conf import get_from_project_dir
    config = get_from_project_dir()
    return create_engine('sqlite:///'+str(config._project_dir / (appname + '/db.sqlite3')))
