#!/bin/sh

nginx start
uwsgi --ini /code/uwsgi.ini
