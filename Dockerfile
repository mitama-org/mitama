FROM alpine:3.13

RUN apk add --no-cache shadow nginx sqlite mariadb-client postgresql gcc libffi-dev build-base rust cargo libressl-dev python3 python3-dev py3-pip
RUN pip3 install --upgrade pip poetry --no-cache-dir
RUN mkdir /code
RUN usermod -u 1000 nginx
WORKDIR /code

ADD docker/entrypoint.sh /code/entrypoint.sh
ADD docker/setup_config.py /code/setup_config.py
ADD docker/uwsgi.ini /code/uwsgi.ini
ADD mitama/ /code/mitama
ADD pyproject.toml /code/pyproject.toml

RUN poetry install --no-dev
RUN mkdir /project
RUN mkdir /logs
RUN mkdir /pid
RUN touch /logs/mitama.log
RUN touch /pid/mitama.pid
RUN python3 mitama init
RUN chown -R nginx:nginx /project
RUN chmod -R 755 /project
RUN chmod -R 777 /logs
RUN chmod -R 777 /pid
USER 1000
WORKDIR /project

ENV DATABASE_TYPE='sqlite3' DATABASE_HOST='localhost' DATABASE_NAME='mitama' DATABASE_USER='root' DATABASE_PASSWORD='password'
EXPOSE 80
CMD ["/code/entrypoint.sh"]
