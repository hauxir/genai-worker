FROM python:3.11-slim

RUN apt-get update
RUN apt-get install -y redis nginx

COPY requirements.txt .
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN pip install -r requirements.txt

EXPOSE 5000

COPY app /app
WORKDIR /app

CMD bash entrypoint.sh
