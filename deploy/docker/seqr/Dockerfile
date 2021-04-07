FROM python:3.7-buster

ARG SEQR_REPO=https://github.com/populationgenomics/seqr
ARG SEQR_GIT_SHA
ARG SEQR_SERVICE_PORT
ENV SEQR_SERVICE_PORT=$SEQR_SERVICE_PORT
ENV PATH $PATH:/root/google-cloud-sdk/bin
EXPOSE $SEQR_SERVICE_PORT

# install commmon utilities
RUN apt update && apt install -y --no-install-recommends \
    # install dependencies of the HaploPainter.pl script used to generate static pedigree images
    cpanminus libpango1.0-dev libgtk2.0-dev && \
    apt clean && rm -rf /var/lib/apt/lists/* && \
    cpanm --notest Cairo DBI Gtk2 Tk Sort::Naturally && \
    # install gcloud tools
    curl https://sdk.cloud.google.com | bash && \
    # update seqr repo
    git clone -q $SEQR_REPO seqr && \
    cd seqr && \
    git checkout $SEQR_GIT_SHA && \
    # install seqr dependencies
    pip install -r requirements.txt && \
    cd deploy/docker/seqr && \
    cp readiness_probe entrypoint.sh / && \
    cp bin/*.sh /usr/local/bin/ && \
    cp config/*.py /seqr

COPY --from=us-docker.pkg.dev/berglas/berglas/berglas:latest /bin/berglas /bin/berglas

ENTRYPOINT exec /bin/berglas exec -- /entrypoint.sh
