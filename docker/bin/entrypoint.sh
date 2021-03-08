#!/bin/sh

poetry install --no-dev
nginx
postfix start
uwsgi --ini /conf/uwsgi.ini
