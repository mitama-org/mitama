<h1 align="center">
  <img src="https://user-images.githubusercontent.com/50577904/94712498-86f98d00-0384-11eb-8d97-bbe79a165609.png" height="178" width="485" />
</h1>

<p align="center">
  <img src='https://img.shields.io/github/license/mitama-org/mitama'>
  <img src='https://badge.fury.io/py/mitama.svg'>
  <img src="https://img.shields.io/circleci/build/gh/mitama-org/mitama/master">
  <img src='https://img.shields.io/github/stars/mitama-org/mitama.svg'>
</p>

[ [English](README.en.md) | [日本語](README.md) ]


## About Mitama

A time of relief comes to system managers who are consumed by hard work.

## Install
Mitama is developed as a Python package, so it can be installed by pip.

```bash
$ pip install mitama
```

If the following command brings up a version, Congratulations on your Mitama debut!

```bash
$ mitama version
1.0.0
```

Once you've successfully installed the app, you can create a "project". A project is the unit in which Mitama is run, and for each project, user and organization information can be generated and apps can be installed. The data and resource files used in the app are also generated and installed in the project folder.

```bash
$ mitama new myfirstproject
$ ls myfirstproject
mitama.json
```
When you hit the command, a directory will be created, and there should be a file named "mitama.json" in it. This is the configuration file.

## Setting up a server
Enter the directory of the project you created and start the server.

```bash
$ cd myfirstproject
$ mitama run
```

By default, the HTTP server is started on port 8080. Go to http://localhost:8080 and check.

## Setup
Open mitama.json in your project.

```json
{
  "apps": {
    "mitama.portal": {
      "path": "/"
    }
  }
}
```

In this file, you configure which packages are delivered in which directory in the HTTP server. By default, the mitama.portal package, which is a portal system included by default in Mitama, is delivered as the root path.

Try it out and make the following changes

```json
{
  "apps": {
    "mitama.portal": {
      "path": "/portal"
    }
  }
}
```

Once you've made the change, stop the server with Ctrl-C and try to start it again. You should then see a 404 error in the root and the portal should be delivered at http://localhost:8080/portal.

If you want to run an app created by a volunteer or your own work, please add the information of the app under the apps just like the portal.

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

You can install the app by pip, but you can also install it by putting the whole package in the project directory if it's not published in PyPI. In this case, the package name should be a folder name. For more information, please follow the publisher's instructions.

## Other
See [official documentation](https://mitama-docs.netlify.app/index.html) for references, app creation, and other details.
