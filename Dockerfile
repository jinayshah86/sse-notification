# BUILD IMAGE
FROM python:3.9-slim-buster AS sse-notification-build

WORKDIR /app

COPY . /app

RUN pip install pipenv \
    && apt-get update \
    && apt-get clean

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# RUNTIME IMAGE
FROM python:3.9-slim-buster AS see-notification-runtime-image

RUN apt-get update \
    && apt-get install -y curl ca-certificates nginx supervisor \
    && rm -rf /var/lib/apt/lists/* /var/cache/oracle-jdk8-installer \
    && ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
    && rm -rf /root/.cache/pip \
    && apt-get clean

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/
COPY --from=sse-notification-build /opt/venv /opt/venv
COPY --from=sse-notification-build /app /app

EXPOSE 8000

CMD ["sh","-c","/usr/bin/supervisord"]
