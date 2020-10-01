<h1 align="center">
  <img src="https://user-images.githubusercontent.com/50577904/94712498-86f98d00-0384-11eb-8d97-bbe79a165609.png" height="178" width="485" />
</h1>

<p align="center">
  <img src='https://img.shields.io/github/license/mitama-org/mitama'>
  <img src='https://badge.fury.io/py/mitama.svg'>
  <img src="https://img.shields.io/circleci/build/gh/mitama-org/mitama/master">
  <img src='https://img.shields.io/github/stars/mitama-org/mitama.svg'>
</p>

## Mitamaとは

Mitamaは悩めるシステム管理者のための<ruby>幸魂<rp>(</rp><rt>webアプリケーションフレームワーク</rt><rp>)</rp>です

## インストール
MitamaはPythonパッケージとして開発されているので、pipでインストールすることができます。

```bash
$ pip install mitama
```

下記のコマンドでバージョンが出てきたら、インストール成功です。Mitamaデビューおめでとうございます。

```bash
$ mitama version
1.0.0
```

無事インストールができたら、「プロジェクト」を作成してみましょう。プロジェクトとは、Mitamaを稼働させる時の単位で、プロジェクトごとにユーザーや組織の情報が生成されたり、アプリをインストールすることができます。アプリ内で使用するデータやリソースファイルもプロジェクトのフォルダ内に生成・設置されます。

```bash
$ mitama new myfirstproject
$ ls myfirstproject
mitama.json
```
コマンドを叩くとディレクトリが作成され、中に mitama.json というファイルが置いてあると思います。こいつは設定ファイルです。

## サーバーを立ち上げる
作成したプロジェクトのディレクトリに入り、サーバーを起動します。

```bash
$ cd myfirstproject
$ mitama run
```

デフォルトでは、8080番ポートでHTTPサーバーが起動します。http://localhost:8080 にアクセスし、確認してください。

## 設定
プロジェクト内のmitama.jsonを開いてください。

```json
{
  "apps": {
    "mitama.portal": {
      "path": "/"
    }
  }
}
```

このファイルの中では、どのパッケージを、HTTPサーバーにおけるどのディレクトリで配信するかを設定します。デフォルトでは、Mitamaに標準で搭載されているポータルシステムである mitama.portal パッケージが、ルートパスで配信されています。

試しに、以下の様に変更を加えてみてください。

```json
{
  "apps": {
    "mitama.portal": {
      "path": "/portal"
    }
  }
}
```

変更したら、サーバーを一度Ctrl-Cで止め、再度起動してみましょう。するとルートでは404エラーが表示され、ポータルはhttp://localhost:8080/portal で配信されるようになるはずです。

もし有志の方が作ったアプリや自作のものを動かすときには、portalと同じ様にapps下にアプリの情報を書き加えてください。

```json
{
  "apps": {
    "mitama.portal": {
      "path": "/"
    },
    "NewPackageName": {
      "path": "/newapppath"
    }
  }
}
```

アプリはpipでインストールすることもできますが、PyPIで公開されていない場合などはアプリのパッケージをまるごとプロジェクトディレクトリに設置することでインストールすることもできます。この場合、パッケージ名はフォルダ名などになるかと思います。詳しくは公開者の指示に従ってください。

## その他
リファレンス、アプリ作成、その他詳細は[公式ドキュメント](https://mitama-docs.netlify.app/index.html)をご参照ください。
