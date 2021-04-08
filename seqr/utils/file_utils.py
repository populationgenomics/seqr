import logging
import os
import subprocess

from google.cloud import storage


logger = logging.getLogger(__name__)
storage_client = None


def gcs_storage_client():
    """Returns a lazily initialized GCS storage client."""
    global storage_client
    if not storage_client:
        storage_client = storage.Client()
    return storage_client


def _run_gsutil_command(command, gs_path, gunzip=False):
    #  Anvil buckets are requester-pays and we bill them to the anvil project
    project_arg = '-u anvil-datastorage ' if gs_path.startswith('gs://fc-secure') else ''
    command = 'gsutil {project_arg}{command} {gs_path}'.format(
        project_arg=project_arg, command=command, gs_path=gs_path,
    )
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


def file_iter(file_path, byte_range=None, raw_content=False):
    if _is_google_bucket_file_path(file_path):
        for line in _google_bucket_file_iter(file_path, byte_range=byte_range, raw_content=raw_content):
            yield line
    else:
        mode = 'rb' if raw_content else 'r'
        with open(file_path, mode) as f:
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


def _google_bucket_file_iter(gs_path, byte_range=None, raw_content=False):
    """Iterate over lines in the given file"""
    if raw_content:  # Fast path to avoid launching a Python process.
        path_segments = gs_path.split('/')
        if not gs_path.startswith('gs://') or len(path_segments) < 4:
            raise ValueError(f'Invalid GCS path: "{gs_path}"')
        bucket = gcs_storage_client().bucket(path_segments[2])
        blob = bucket.blob('/'.join(path_segments[3:]))
        if byte_range:
            yield blob.download_as_bytes(start=byte_range[0], end=byte_range[1])
        else:
            yield blob.download_as_bytes()
        return

    range_arg = ' -r {}-{}'.format(byte_range[0], byte_range[1]) if byte_range else ''
    process = _run_gsutil_command('cat{}'.format(range_arg), gs_path, gunzip=gs_path.endswith("gz") and not raw_content)
    for line in process.stdout:
        if not raw_content:
            line = line.decode('utf-8')
        yield line

