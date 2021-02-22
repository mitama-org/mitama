==================
コマンド
==================

mitama debug [port]
=========================
デバッグモードでサーバーを起動します。

デバッグモードでは、プロジェクトディレクトリ下でファイルの変更があった場合、自動的にアプリのパッケージをリロードします。

例
-----

.. code-block:: bash

    $ mitama debug 8080


mitama help
=========================
ヘルプを表示します。

例
-----

.. code-block:: bash

    $ mitama help

mitama mkapp [app_name]
=========================
アプリパッケージのテンプレートからアプリディレクトリを生成します。

例
-----

.. code-block:: bash

    $ mitama mkapp MyAppName
    $ ls MyAppName
    templates/  static/  __init__.py  controller.py  main.py  model.py

mitama init
=========================
カレントディレクトリをプロジェクトディレクトリとして初期化します。

例
-----

.. code-block:: bash

    $ mitama init
    $ ls mitama.json
    mitama.json

mitama new [project_name]
=========================
新しいプロジェクトを作成します。

例
----

.. code-block:: bash

    $ mitama new myproject
    $ ls myproject
    mitama.json

mitama run [port]
=========================
サーバーを起動します。

例
-----

.. code-block:: bash

    $ mitama run 8080


mitama version
=========================
バージョンを確認します。

例
-----

.. code-block:: bash

    $ mitama version
    2.0.0

