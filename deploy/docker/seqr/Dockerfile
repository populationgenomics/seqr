FROM python:3.9-slim-buster

ARG SEQR_SERVICE_PORT
ENV SEQR_SERVICE_PORT=$SEQR_SERVICE_PORT
EXPOSE $SEQR_SERVICE_PORT

WORKDIR /app/seqr
COPY requirements.txt /app/seqr/

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https ca-certificates curl gnupg \
    # install dependencies of the HaploPainter.pl script used to generate static pedigree images
    libgtk2-perl libdbi-perl libtk-perl libsort-naturally-perl && \
    # Google Cloud SDK
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-sdk && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r /app/seqr/requirements.txt

COPY admin /app/seqr/admin
COPY matchmaker /app/seqr/matchmaker
COPY reference_data /app/seqr/reference_data
COPY seqr /app/seqr/seqr
COPY ui/dist /app/seqr/ui/dist
COPY panelapp /app/seqr/panelapp
COPY wsgi.py settings.py manage.py deploy/docker/seqr/entrypoint.sh deploy/docker/seqr/init_db.sh deploy/docker/seqr/config/ /app/seqr/

RUN python manage.py collectstatic --no-input

# Berglass: Store and retrieve secrets on Google Cloud
COPY --from=us-docker.pkg.dev/berglas/berglas/berglas:latest /bin/berglas /bin/berglas

ENTRYPOINT ["/bin/berglas", "exec", "--", "/app/seqr/entrypoint.sh"]
