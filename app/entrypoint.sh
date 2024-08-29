#!/bin/bash
rm -rf /tmp/*
redis-server &
WORKERS=${WORKERS:-2}
echo $WORKERS workers
celery -A worker worker -l info -E --concurrency=$WORKERS &
nginx
gunicorn --limit-request-line 10000 --timeout 900 --bind unix:genai.sock app:app  --access-logfile -
