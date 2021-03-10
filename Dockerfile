FROM alpine:3.13
RUN mkdir /pkg
COPY mitama-*.whl /pkg/
WORKDIR /pkg
RUN apk add --no-cache python3 python3-dev py3-pip libmagic nginx build-base gcc libffi-dev openssl-dev rust cargo zlib-dev jpeg-dev nginx postfix git git-daemon \
    && pip3 install --upgrade pip \
    && pip3 install uwsgi poetry \
    && pip3 install --find-links=/pkg mitama \
    && apk del --purge rust cargo zlib-dev libffi-dev gcc build-base python3-dev
RUN mkdir /conf
RUN mkdir /log
RUN mkdir /project
RUN chmod 755 /log
ADD /docker/conf/uwsgi.ini /conf/uwsgi.ini
ADD /docker/conf/nginx.conf /etc/nginx/nginx.conf
ADD /docker/bin/entrypoint.sh /bin/entrypoint.sh

WORKDIR /project
CMD ["/bin/entrypoint.sh"]
