#!/bin/sh

poetry config virtualenvs.create false
poetry install --no-dev
nginx
postfix start
uwsgi --ini /conf/uwsgi.ini
