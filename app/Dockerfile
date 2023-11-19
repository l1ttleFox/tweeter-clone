FROM python:3.11

RUN apt-get update && apt-get install -y python3-dev supervisor nginx \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./ /app/

CMD [""]

