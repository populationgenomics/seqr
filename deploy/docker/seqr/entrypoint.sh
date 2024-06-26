#!/usr/bin/env bash

echo $GSA_KEY > /tmp/gsa-key.json
gcloud auth activate-service-account --key-file /tmp/gsa-key.json
rm /tmp/gsa-key.json

# link to persistent disk dir with static files
mkdir -p /seqr_static_files/generated_files

gunicorn -w $GUNICORN_WORKER_THREADS -c /app/seqr/gunicorn_config.py wsgi:application
