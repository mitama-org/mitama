<h1 align="center">
  <img src="https://user-images.githubusercontent.com/50577904/94712498-86f98d00-0384-11eb-8d97-bbe79a165609.png" height="178" width="485" />
</h1>

<p align="center">
  <img src='https://img.shields.io/github/license/mitama-org/mitama'>
  <img src='https://badge.fury.io/py/mitama.svg'>
  <img src="https://img.shields.io/circleci/build/gh/mitama-org/mitama/master">
  <img src='https://img.shields.io/github/stars/mitama-org/mitama.svg'>
</p>

## 什么是Mitama？

被辛勤工作消耗掉的系统管理者迎来了一个解脱的时刻。

## 安装

Mitama是作为一个Python包开发的，所以它可以通过pip安装。

```bash
$ pip install mitama
```

如果下面的命令带来了一个版本，恭喜你的Mitama首秀

```bash
$ mitama version
1.0.0
```

一旦你成功安装了应用程序，你就可以创建一个 "项目"。项目是运行Mitama的单位，对于每个项目，可以生成用户和组织信息，并可以安装应用程序。应用中使用的数据和资源文件也会生成并安装在项目文件夹中。

```bash
$ mitama new myfirstproject
$ ls myfirstproject
mitama.json
```

当你点击该命令时，将创建一个目录，其中应该有一个名为 "mitama.json "的文件。这就是配置文件。

## 设置一个服务器
进入你创建的项目的目录，启动服务器。

```bash
$ cd myfirstproject
$ mitama run
```

默认情况下，HTTP服务器是在8080端口启动的。转到http://localhost:8080，然后检查。

## 设置
在你的项目中打开mitama.json。

```json
{
  "apps": {
    "mitama.portal": {
      "path": "/"
    }
  }
}
```

在这个文件中，你可以配置哪些包在HTTP服务器的哪个目录下被交付。默认情况下，Mitama.portal包是Mitama中默认包含的一个门户系统，它被作为根路径交付。

试试吧，并做以下修改

```json
{
  "apps": {
    "mitama.portal": {
      "path": "/portal"
    }
  }
}
```

一旦你做了修改，用Ctrl-C停止服务器，并尝试再次启动它。然后你应该在根目录中看到一个404错误，门户网站应该在http://localhost:8080/portal。

如果你想运行一个由志愿者创建的应用程序或你自己的作品，请在应用程序下添加应用程序的信息，就像门户网站一样。

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

你可以通过pip来安装这个应用，但如果它没有在PyPI中发布，你也可以通过把整个包放在项目目录中来安装它。在这种情况下，软件包的名称应该是一个文件夹的名称。欲了解更多信息，请遵循出版商的指示。

## 其他
有关参考资料、应用程序的创建和其他细节，请参见[官方文档](https://mitama-docs.netlify.app/index.html)。