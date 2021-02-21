#!/bin/sh

nginx start
python /code/rewrite_json.py
uwsgi --ini /code/uwsgi.ini
