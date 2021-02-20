FROM alpine:3.7

RUN apk add --no-cache nginx python3 sqlite mariadb-client postgresql
RUN mkdir /code
RUN adduser -S nginx && adduser -S -g nginx nginx
RUN usermod -u 1000 nginx
WORKDIR /code

ADD entrypoint.sh /code/entrypoint.sh
ADD uwsgi.ini /code/uwsgi.ini
ADD ../mitama/ /code

RUN pip install --upgrade pip poetry --no-cache-dir
RUN poetry install --no-dev

RUN mkdir /project
RUN mkdir /logs
RUN mkdir /pid
RUN touch /logs/mitama.log
RUN touch /pid/mitama.pid
RUN mitama init
RUN chown -R nginx:nginx /project
RUN chmod -R 755 /project
RUN chmod -R 777 /logs
RUN chmod -R 777 /pid
USER 1000
WORKDIR /project

EXPOSE 80
CMD ["/code/entrypoint.sh"]
