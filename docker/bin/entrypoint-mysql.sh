#!/bin/sh

poetry install

nginx
postfix start
uwsgi --ini /conf/uwsgi.ini
