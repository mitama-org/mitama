=======================
アプリ開発の手ほどき
=======================

Mitamaは簡単にアプリを配信するサーバーがメインの機能ですが、同時にそのサーバーで稼働するアプリを開発するためのWebアプリケーションフレームワークでもあります。Mitamaに用意された人材管理のための豊富なインターフェースを活かし、手軽に社内システムなどを内製することができます。

このページで簡単なTodoアプリの開発をしながら、Mitamaでアプリを開発する方法を覚えてみましょう。

準備
=======================

ひとまず、テスト用のプロジェクトディレクトリを作成し、その中でアプリのパッケージフォルダを作成してください。

今回はmyfirstappというパッケージ名で作成をすすめていきます。

.. code-block:: bash

    $ mitama new myfirstproject
    $ cd myfirstproject
    $ mkdir myfirstapp
    $ cd myfirstapp
    $ touch __init__.py

プロジェクトの設定ファイルを変更し、myfirstappが配信されるようにしましょう。

.. code-block:: json

    {
        "apps": {
            "mitama.portal": {
                "path": "/"
            },
            "myfirstapp": {
                "path": "/todo"
            }
        }
    }

これで、 http://localhost\:8080/todo でアプリが配信されるようになります。（まだアプリを作り込んでいないので配信されていません。）

なにか表示してみる
======================

では、次のコードを__init__.pyに書き込んでみましょう。これはおまじないですので、覚えなくていいです。後々紹介する :command:`mitama mkapp` コマンドを使えば、勝手に生成してくれます。

.. code-block:: python

    from mitama.app import Builder
    from .main import App

    class AppBuilder(Builder):
        app = App

次に、パッケージ内に :file:`main.py` を作成しましょう。この中の処理が最初に実行されます。

.. code-block:: bash

   $ touch main.py
   $ ls
   __init__.py  main.py

ひとまず、「Hello, world!」と表示するようにしてみましょう。main.pyに次のコードを書いてみてください。

.. code-block:: python

    from mitama.app import App, Router, Controller
    from mitama.app.method import view
    from mitama.http import Response

    class HomeController(Controller):
        def handle(self, request):
            return Response(text='Hello, world!')

    class App(App):
        router = Router([
            view('/', HomeController)
        ])

できたら、サーバーを起動し、ブラウザで表示を確認してみてください。「Hello, world!」が表示されていれば成功です。

細かく解説しましょう。まず、最初の2行ではアプリに必要なクラスを読み込んでいます。今回はあくまで表示に必要最低限のものだけを読み込みました。

.. code-block:: python
   
    from mitama.app import App, Router, Controller
    from mitama.app.method import view
    from mitama.http import Response

読み込んだControllerを使って早速あたらしいクラスを作っていきます。Controllerはリクエストの処理を司るクラスです。MVCモデルという概念に馴染みのある方には理解しやすいかもしれません。Routerによってルーティングされた場合に実行される様々な挙動をここで定義します。

今回は単純に「Hello, world!」という文字を含んだレスポンスが得られればいいので、*Response(text='Hello, world')* を返しています。

.. code-block:: python

    class HomeController(Controller):
        def handle(self, request):
            return Response(text='Hello, world!')


最後に、Appクラスを定義します。

.. code-block:: python

    class App(App):
        router = Router([
            view('/', HomeController)
        ])

Appはこのアプリの中核となるクラスです。この中に登録された情報に基づき、アプリが配信されます。
Routerはルーティングエンジンです。アクセスされたパスと実行する処理の対応を定義します。この場合、 :file:`/` にアクセスすると、:samp:`HomeController.handle` が実行されます。

アクセスを制限する
==========================

社内システムなどでは、外部の人がすべてのページにアクセスすることができるという状態は好ましくありません。必要に応じてアクセス制限をつけてみましょう。

アクセス制限をかけたいときには、Mitamaに内蔵されているSessionMiddlewareを使うと簡単にできます。

.. code-block:: python

    from mitama.app import App, Router, Controller
    from mitama.app.method import view
    from mitama.app.middlewares import SessionMiddleware
    from mitama.http import Response

    ...

    class App(App):
        router = Router([
            view('/', HomeController)
        ], middlewares = [SessionMiddleware])

サーバーを再起動し、試しにログインしていない状態でアクセスしてみてください。ログインページへ飛ばされれば成功です。
飛ばされたら、ログインして戻ってみましょう。そうすると、もとの通り表示されるかと思います。

このようなMiddlewareは自前で実装することも可能です。

Todoを実装してみる
===================

次に、Todoアプリを実現するための「モデル」を定義してみましょう。モデルとは、アプリ内で扱うデータの塊だと思ってください。

.. code-block:: python

    from mitama.app import App, Router, Controller
    from mitama.app.method import view
    from mitama.app.middlewares import SessionMiddleware
    from mitama.http import Response
    from mitama.db import BaseDatabase
    from mitama.db.types import *

    class Database(BaseDatabase):
        pass

    db = Database()

    class Todo(db.Model):
        title = Column(String)
        description = Column(String)
        deadline = Column(DateTime)
        user = Column(User)

    db.create_all()
    ...

サーバーを再起動し、パッケージフォルダ内にdb.sqlite3があるか確認してみてください。SQLiteを扱える人は、中身をみてテーブルが作成されていることを確認してみるといいかもしれません。このファイルの中にTodoのデータが溜まっていきます。

では、このTodoについて、

1. 作る
2. 見る
3. 消す

といった操作をするページを作ってみましょう。HTMLのページを作成する場合には、テンプレートを使うと便利です。

Mitamaでは、Controllerから直接Jinja2を呼び出すことができます。アプリディレクトリ内に :file:`templates/` フォルダを作成し、HTMLテンプレートを置いてみましょう。

.. code-block:: jinja

    <!-- list.html -->
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset='utf-8'>
        </head>
        <body>
            <h1>Todo一覧</h1>
            <a href='{{ url('/create') }}'>Todoを作成</a>
            <ul>
            {% for todo in todos %}
                <li>
                    <h3>{{todo.title}}</h3>
                    <p>{{todo.description}}</p>
                    <a href='{{ url('/done/'+todo._id|string) }}'>完了</a>
                </li>
            {% endfor %}
            </ul>
        </body>
    </html>


.. code-block:: jinja

    <!-- create.html -->
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset='utf-8'>
        </head>
        <body>
            <h1>Todoを作成</h1>
            <form action='' method='POST'>
                <input type='text' name='title' placeholder='タイトル'>
                <textarea name='description' placeholder='内容'></textarea>
                <input type='datetime-local' name='deadline'>
                <p>{{error}}</p>
                <button>作成</button>
            </form>
        </body>
    </html>

たまにテンプレート内に出てくる :samp:`url(...)` という関数は、最終的にパスがmitama.json内の設定に合わせて変わってしまうため、それを変換するために実行しています。Controller内などでは、:samp:`Controller.app.convert_url(self, ...)` を使うと同様の処理ができます。

HTMLができたら、それを表示する処理、フォームから送信されたデータからTodoを作成する処理、Todoを削除する処理を作成しましょう。

.. code-block:: python

    ...
    class HomeController(Controller):
        def handle(self, request):
            todos = Todo.query.filter(Todo.user == request.user).all()
            template = self.view.get_template('list.html')
            return Response.render(template, {
                'todos': todos
            })
        def create(self, request):
            template = self.view.get_template('create.html')
            if request.method == 'POST':
                post = request.post()
                try:
                    todo = Todo()
                    todo.title = post['title']
                    todo.description = post['description']
                    todo.deadline = datetime.strptime(post['deadline'], '%Y-%m-%dT%H:%M')
                    todo.user = request.user
                    todo.create()
                except Exception as err:
                    return Response.render(template, {
                        'error': err
                    })
                return Response.redirect(self.app.convert_url('/'))
            return Response.render(template)
        def done(self, request):
            todo = Todo.query.filter(Todo._id == request.params['id']).filter(Todo.user == request.user).one()
            todo.delete()
            return Response.redirect(self.app.convert_url('/'))
    ...
    class App(App):
        ...
        router = Router([
            view('/', HomeController),
            view('/create', HomeController, 'create'),
            view('/done/<id>', HomeController, 'done'),
        ], middlewares = [SessionMiddleware])

いきなり大量のコードを書くハメになりましたね…少し整理しましょう。

.. code-block:: python
   
        def handle(self, request):
            todos = Todo.query.filter(Todo.user == request.user).all()
            template = self.view.get_template('list.html')
            return Response.render(template, {
                'todos': todos
            })

:samp:`Todo.query.filter(...).all()` によって、ログインしているユーザーにより登録されたTodoをすべて取得しています。
:samp:`request.user` にはログインしているユーザーのモデルが格納されています。モデルを定義するときにColumn(User)とすればユーザー扱うプロパティを作成できます。
:samp:`Response.render(...)` ではテンプレートで生成したHTMLをレスポンスに入れて返してくれます。

.. code-block:: python

        def create(self, request):
            template = self.view.get_template('create.html')
            if request.method == 'POST':
                post = request.post()
                try:
                    todo = Todo()
                    todo.title = post['title']
                    todo.description = post['description']
                    todo.deadline = datetime.strptime(post['deadline'], '%Y-%m-%dT%H:%M')
                    todo.user = request.user
                    todo.create()
                except Exception as err:
                    return Response.render(template, {
                        'error': err
                    })
                return Response.redirect(self.app.convert_url('/'))
            return Response.render(template)

createメソッドでは、フォームから送信されたデータの登録を行っています。
登録作業が正常に行えた場合、トップページにリダイレクトされます。先程も解説したとおり、Controller内では、:samp:`self.app.controller(path)` によってURLを変換しましょう。


.. code-block:: python

        def done(self, request):
            todo = Todo.query.filter(Todo._id == request.params['id']).filter(Todo.user == request.user).one()
            todo.delete()
            return Response.redirect(self.app.convert_url('/'))

doneメソッドでは、URLに指定されたIDの、ログインしているユーザーのTodoを抽出し、削除しています。
その後、すぐにトップページにリダイレクトさせています。

これで簡単なTodoアプリの完成です。動きましたか？


ファイルを整理する
=====================

とりあえず、現在のフルコードを貼ってみましょう。

.. code-block:: python

    from mitama.app import App, Router, Controller
    from mitama.app.method import view
    from mitama.http import Response
    from mitama.db import BaseDatabase
    from mitama.db.types import *

    class Database(BaseDatabase):
        pass

    db = Database()

    class Todo(db.Model):
        title = Column(String)
        description = Column(String)
        deadline = Column(DateTime)
        user = Column(User)

    db.create_all()

    class HomeController(Controller):
        def handle(self, request):
            todos = Todo.query.filter(Todo.user == request.user).all()
            template = self.view.get_template('list.html')
            return Response.render(template, {
                'todos': todos
            })
        def create(self, request):
            template = self.view.get_template('create.html')
            if request.method == 'POST':
                post = request.post()
                try:
                    todo = Todo()
                    todo.title = post['title']
                    todo.description = post['description']
                    todo.deadline = datetime.strptime(post['deadline'], '%Y-%m-%dT%H:%M')
                    todo.user = request.user
                    todo.create()
                except Exception as err:
                    return Response.render(template, {
                        'error': err
                    })
                return Response.redirect(self.app.convert_url('/'))
            return Response.render(template)
        def done(self, request):
            todo = Todo.query.filter(Todo._id == request.params['id']).filter(Todo.user == request.user).one()
            todo.delete()
            return Response.redirect(self.app.convert_url('/'))

    class App(App):
        router = Router([
            view('/', HomeController),
            view('/create', HomeController, 'create'),
            view('/done/<id>', HomeController, 'done'),
        ], middlewares = [SessionMiddleware])

長いですよね。これだけ多くのものが一つのファイルに固まっていると混乱するので、ファイルを分割してみましょう。
開発者的にもまだはっきりと言える状態ではありませんが、一旦以下のファイル構成に落ち着いています。

.. code-block:: 

    myfirstapp
    |- templates/
    |- static/
    |- __init__.py
    |- controller.py
    |- main.py
    |- middleware.py
    +- model.py

:file:`controller.py` には、Controllerクラスの定義を記述します。

.. code-block:: python

    from mitama.app import Controller
    from mitama.http import Response
    from .model import Todo

    class HomeController(Controller):
        def handle(self, request):
            todos = Todo.query.filter(Todo.user == request.user).all()
            template = self.view.get_template('list.html')
            return Response.render(template, {
                'todos': todos
            })
        def create(self, request):
            template = self.view.get_template('create.html')
            if request.method == 'POST':
                post = request.post()
                try:
                    todo = Todo()
                    todo.title = post['title']
                    todo.description = post['description']
                    todo.deadline = datetime.strptime(post['deadline'], '%Y-%m-%dT%H:%M')
                    todo.user = request.user
                    todo.create()
                except Exception as err:
                    return Response.render(template, {
                        'error': err
                    })
                return Response.redirect(self.app.convert_url('/'))
            return Response.render(template)
        def done(self, request):
            todo = Todo.query.filter(Todo._id == request.params['id']).filter(Todo.user == request.user).one()
            todo.delete()
            return Response.redirect(self.app.convert_url('/'))

そして、 :file:`model.py` にはTodoのようなモデルの定義と、それに必要なデータベースの定義を書きます。

.. code-block:: python

    from mitama.db import BaseDatabase
    from mitama.db.types import *

    class Database(BaseDatabase):
        pass

    db = Database()

    class Todo(db.Model):
        title = Column(String)
        description = Column(String)
        deadline = Column(DateTime)
        user = Column(User)

    db.create_all()

:file:`middleware.py` には、自前のMiddlewareを入れます。また、:file:`templates/` には先程と同様にテンプレートファイルを、 :file:`static/` には、:samp:`mitama.app.StaticFileController` によって配信できる静的ファイルを入れます。

最終的に、main.pyには下記のコードだけが残ります。

.. code-block:: python

    from .controller import HomeController
    from mitama.app import App, Router
    from mitama.app.method import view
    from mitama.app.middleware import SessionMiddleware

    class App(App):
        router = Router([
            view('/', HomeController),
            view('/create', HomeController, 'create'),
            view('/done/<id>', HomeController, 'done'),
        ], middlewares = [SessionMiddleware])

だいぶスッキリしましたね。実は、:command:`mitama mkapp <アプリ名>` というコマンドを使うと、このようにすでに分割された空のプロジェクトが生成されます。最初から整理された状態になってより開発にスムーズに取りかかれると思います。
