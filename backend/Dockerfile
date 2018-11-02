FROM python:3.5

ENV DEBIAN_FRONTEND "noninteractive"

RUN apt update \
  && apt install -y python3-dev mysql-client libmysqlclient-dev \
  && apt install -y supervisor nginx \
  && groupadd nginx \
  && useradd -s /sbin/nologin -g nginx nginx

RUN mkdir -p /var/log/gunicorn \
  && mkdir -p /var/run/gunicorn

RUN mkdir -p /etc/nginx/sites-available \
  && mkdir -p /etc/nginx/sites-enabled \
  && rm -f /etc/nginx/sites-enabled/default \
  && ln -sf /dev/stdout /var/log/nginx/access.log \
  && ln -sf /dev/stderr /var/log/nginx/error.log

COPY flagger /opt/app/src
COPY Pipfile /opt/app/src/Pipfile
COPY Pipfile.lock /opt/app/src/Pipfile.lock
COPY docker/django/files/gunicorn_config.py /opt/app/src/gunicorn_config.py
COPY docker/django/files/entrypoint.sh /opt/app/src/entrypoint.sh

RUN chmod +x /opt/app/src/entrypoint.sh

COPY docker/etc/flagger.conf /etc/supervisor/conf.d/flagger.conf
COPY docker/nginx/etc/default /etc/nginx/sites-available/default
COPY docker/nginx/etc/nginx.conf /etc/nginx/nginx.conf

RUN ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

WORKDIR /opt/app/src
RUN pip install pipenv \
  && pipenv install --system --deploy

EXPOSE 80 8000

ENTRYPOINT ["/opt/app/src/entrypoint.sh"]