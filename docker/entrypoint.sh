#!/bin/sh

nginx start
python /code/setup_config.py
uwsgi --ini /code/uwsgi.ini
