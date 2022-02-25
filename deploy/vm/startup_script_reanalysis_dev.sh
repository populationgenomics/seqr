#!/bin/bash

set -x

# gcsfuse
echo "deb http://packages.cloud.google.com/apt gcsfuse-focal main" | tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

# stackdriver-agent
curl -sSO https://dl.google.com/cloudagents/add-monitoring-agent-repo.sh
bash add-monitoring-agent-repo.sh

apt update
apt install -y gcsfuse docker.io stackdriver-agent

service stackdriver-agent start

# Mount GCS bucket for static file serving.
mkdir -p /seqr_static_files
gcsfuse cpg-seqr-reanalysis-dev-static-files /seqr_static_files

gcloud -q auth configure-docker australia-southeast1-docker.pkg.dev

# Clear Docker cache, in case the VM restarted.
docker system prune -f -a

docker run --name seqr -p 80:8000 \
    -v /seqr_static_files:/seqr_static_files \
    -e DEPLOYMENT_TYPE=dev \
    -e BASE_URL=https://seqr-reanalysis-dev.populationgenomics.org.au/ \
    -e POSTGRES_SERVICE_HOSTNAME=10.94.145.3 \
    -e POSTGRES_SERVICE_PORT=5432 \
    -e POSTGRES_USERNAME=postgres-reanalysis-dev \
    -e POSTGRES_PASSWORD=sm://seqr-308602/postgres-reanalysis-dev-password \
    -e ANALYST_PROJECT_CATEGORY=analyst-projects \
    -e ANALYST_USER_GROUP=analysts \
    -e PM_USER_GROUP=project-managers \
    -e PYTHONPATH=/seqr \
    -e STATIC_MEDIA_DIR=/seqr_static_files \
    -e ELASTICSEARCH_PROTOCOL=https \
    -e ELASTICSEARCH_SERVICE_HOSTNAME=elasticsearch.es.australia-southeast1.gcp.elastic-cloud.com \
    -e ELASTICSEARCH_SERVICE_PORT=9243 \
    -e SEQR_ES_USERNAME=seqr-reanalysis-dev \
    -e SEQR_ES_PASSWORD=sm://seqr-308602/seqr-reanalysis-dev-es-password \
    -e REDIS_SERVICE_HOSTNAME=10.94.144.3 \
    -e GUNICORN_WORKER_THREADS=20 \
    -e SOCIAL_AUTH_GOOGLE_OAUTH2_CLIENT_ID=1021400127367-4vch8s8kc9opeg4v14b2n70se55jpao4.apps.googleusercontent.com \
    -e SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=sm://seqr-308602/social-auth-google-oauth2-secret-reanalysis-dev \
    -e DJANGO_KEY=sm://seqr-308602/django-key-reanalysis-dev \
    -e SENDGRID_API_KEY=sm://seqr-308602/sendgrid-api-key \
    -e GSA_KEY=sm://seqr-308602/gsa-key-reanalysis-dev \
    australia-southeast1-docker.pkg.dev/seqr-308602/seqr-project/seqr:gcloud-reanalysis-dev
