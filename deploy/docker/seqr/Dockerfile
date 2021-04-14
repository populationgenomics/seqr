FROM google/cloud-sdk:335.0.0

ARG SEQR_SERVICE_PORT
ENV SEQR_SERVICE_PORT=$SEQR_SERVICE_PORT
ENV PATH $PATH:/root/google-cloud-sdk/bin
EXPOSE $SEQR_SERVICE_PORT

WORKDIR /app/seqr
ADD requirements.txt /app/seqr/

# install commmon utilities
RUN apt update && apt install -y --no-install-recommends \
    # install dependencies of the HaploPainter.pl script used to generate static pedigree images
    libgtk2-perl libdbi-perl libtk-perl libsort-naturally-perl && \
    apt clean && rm -rf /var/lib/apt/lists/*

# install seqr dependencies
RUN pip install -r /app/seqr/requirements.txt

ADD matchmaker /app/seqr/matchmaker
ADD reference_data /app/seqr/reference_data
ADD seqr /app/seqr/seqr
ADD static ui/dist /app/seqr/static
ADD ui/dist /app/seqr/ui/dist
ADD wsgi.py settings.py servctl manage.py deploy/docker/seqr/entrypoint.sh deploy/docker/seqr/init_db.sh deploy/docker/seqr/config/ /app/seqr

# Berglass: Store and retrieve secrets on Google Cloud
COPY --from=us-docker.pkg.dev/berglas/berglas/berglas:latest /bin/berglas /bin/berglas

ENTRYPOINT exec /bin/berglas exec -- /app/seqr/entrypoint.sh
