import logging
import os
import subprocess

import google.cloud.storage


logger = logging.getLogger(__name__)
storage_client = None


def _gcs_storage_client():
    """Returns a lazily initialized GCS storage client."""
    global storage_client
    if not storage_client:
        storage_client = google.cloud.storage.Client()
    return storage_client


def _run_gsutil_command(command, gs_path, gunzip=False):
    command = f'gsutil {command} {gs_path}'
    if gunzip:
        command += " | gunzip -c -q - "

    logger.info('==> {}'.format(command))
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)


def _is_google_bucket_file_path(file_path):
    return file_path.startswith("gs://")


def does_file_exist(file_path):
    if _is_google_bucket_file_path(file_path):
        process = _run_gsutil_command('ls', file_path)
        return process.wait() == 0
    return os.path.isfile(file_path)


def _iterate(f, byte_range=None):
    if byte_range:
        f.seek(byte_range[0])
        for line in f:
            if f.tell() < byte_range[1]:
                yield line
            else:
                break
    else:
        for line in f:
            yield line


def file_iter(file_path, byte_range=None, raw_content=False):
    mode = 'rb' if raw_content else 'r'
    if _is_google_bucket_file_path(file_path):
        path_segments = file_path.split('/')
        if len(path_segments) < 4:
            raise ValueError(f'Invalid GCS path: "{file_path}"')
        bucket = _gcs_storage_client().bucket(path_segments[2])
        blob = bucket.blob('/'.join(path_segments[3:]))
        with blob.open(mode) as f:
            for line in _iterate(f, byte_range):
                yield line
    else:
        with open(file_path, mode) as f:
            for line in _iterate(f, byte_range):
                yield line
