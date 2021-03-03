<h1 align="center">
  <img src='https://user-images.githubusercontent.com/48381296/109426356-b1816c00-7a30-11eb-988c-1928b0ab8a42.png' height="178" width="485" alt='Mitama'/>
</h1>

<p align="center">
  <img src='https://img.shields.io/github/license/mitama-org/mitama'>
  <img src='https://badge.fury.io/py/mitama.svg'>
  <img src="https://img.shields.io/circleci/build/gh/mitama-org/mitama/master">
  <img src='https://img.shields.io/github/stars/mitama-org/mitama.svg'>
</p>

[ [English](README.en.md) | [日本語](README.md) ]

## Mitamaとは

Mitamaは、Webベースの社内システムを構築するためのPython製フレームワークです。

## 要件

macOSから利用する場合、以下のライブラリを追加でインストールする必要があります。

- libmagic

## インストール

MitamaはPythonパッケージとして開発されているので、pipでインストールすることができます。

```bash
$ pip install mitama
```

下記のコマンドでバージョンが出てきたら、インストール成功です。Mitamaデビューおめでとうございます。

```bash
$ mitama version
4.3.0
```

## 使い方

無事インストールができたら、「プロジェクト」を作成してみましょう。プロジェクトとは、Mitamaを稼働させる時の単位で、プロジェクトごとにユーザーや組織の情報が生成されたり、アプリをインストールすることができます。アプリ内で使用するデータやリソースファイルもプロジェクトのフォルダ内に生成・設置されます。

```bash
$ mitama new myfirstproject
$ ls myfirstproject
project.py
```

コマンドを叩くとディレクトリが作成され、中に**project.py**というファイルが置いてあると思います。

### サーバーを起動してみる

ローカルで試しにサーバーを起動してみましょう。

```bash
$ python project.py run
```

デフォルトでは8080番ポートにサーバーが起動しますので、ブラウザで開いてみてください。

#### uWSGIを使って起動する

uwsgiを使ってnginxなどで配信する場合は、次のような設定ファイルを作成し、起動します。

```uwsgi.ini
[uwsgi]
chdir=/path/to/project.py
socket=127.0.0.1:8080
master=true
vacuum=true
pidfile=/tmp/uwsgi.pid
module=project:application
```

```bash
$ uwsgi --ini /path/to/uwsgi.ini
```

### MySQLやPostgreSQLを用いる場合

project.pyを編集し、DatabaseManagerの引数に指定している*type*を*"mysql"*または*"postgresql"*に変更してください。

```python
## project.py

...

DatabaseManager({
    "type":"mysql",
    "host":"localhost",
    "name":"mitama",
    "user":"mitama",
    "password":"mitama",
})

...

```

### Dockerで起動する

対応しているデータベースそれぞれに対応したDockerイメージが存在します。

- SQLite3: *mitamaorg/mitama:latest*
- MySQL: *mitamaorg/mitama:latest-mysql*
- PostgreSQL: *mitamaorg/mitama:latest-postgresql*

利用したいデータベース似合わせてイメージを選択してください。

また、これらのイメージは自動的にPoetryによる依存解決を試みますので、サードパーティ製のMitamaアプリケーションを利用する場合などはpyproject.tomlを設置しておくと良いかもしれません。

```bash
$ poetry init
$ poetry add izanami
$ ls
pyproject.toml poetry.lock project.py
```

プロジェクトが準備できたら、ディレクトリをコンテナの/projectにマウントして起動してください。

```bash
$ docker run -itd --name mitama_project \
  -v "./:/project" \
  -p 127.0.0.1:8080:80 \
  mitamaorg/mitama:latest
```

docker-composeを使うと、データベースなどの接続が楽にできます。

```docker-compose.yml
version: "3"
services:
  mitama:
    image: mitamaorg/mitama:latest-mysql
    ports:
      - 8080:80
    volumes:
      - ./:/project
  mysql:
    image: mysql:latest
    ports:
      - 3306:3306
    volumes:
      - ./data:/var/lib/mysql
    environment:
      - MYSQL_RANDOM_ROOT_PASSWORD=yes
      - MYSQL_USER=mitama
      - MYSQL_PASSWORD=mitama
      - MYSQL_DATABASE=mitama
```

## 設定

### アプリケーションの配信

project.pyの中に設定を記述することで、自作、またはサードパーティ製のアプリケーションを配信できます。

#### pipでアプリケーションをインストールして用いる場合

以下のように*include("パッケージ名", path="配信先サブディレクトリ")*を記述してください。

```python
## project.py
#!/usr/bin/python

import os

from mitama.project import Project, include
from mitama.db import DatabaseManager

project_dir = os.path.dirname(os.path.abspath(__file__))

DatabaseManager({
    "type":"sqlite",
    "path": project_dir+'/db.sqlite3',
})

project = Project(
    include("mitama.portal", path="/"),
    include("thirdpartyapp", path="/thirdpartyapp"),
    project_dir = project_dir
)
application = project.wsgi


if __name__ == "__main__":
    project.command()
```

#### 自作のアプリケーションを配信する場合

自作のアプリケーションの場合、project.pyと同じディレクトリにPythonパッケージを設置することでもインストールが可能です。

```
.
├── madebyme/
├── db.sqlite3
└── project.py
```

```python
## project.py
#!/usr/bin/python

import os

from mitama.project import Project, include
from mitama.db import DatabaseManager

project_dir = os.path.dirname(os.path.abspath(__file__))

DatabaseManager({
    "type":"sqlite",
    "path": project_dir+'/db.sqlite3',
})

project = Project(
    include("mitama.portal", path="/"),
    include("madebyme", path="/"),
    project_dir = project_dir
)
application = project.wsgi


if __name__ == "__main__":
    project.command()
```


## その他
リファレンス、アプリ作成、その他詳細は[公式ドキュメント](https://mitama-docs.netlify.app/index.html)をご参照ください。

## 作者

- [@boke_0](https://twitter.com/boke_0)
- [@takuan517](https://twitter.com/takuan517)
- [@1105tigery](https://twitter.com/1105tigery)

### Special thanks!

- Seisuke Ito様

## ライセンス

MIT License
