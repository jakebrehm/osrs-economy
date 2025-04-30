"""
Handles interactions with Google Storage.
"""

import datetime as dt
import json
from typing import Any

from google.cloud import storage


def get_storage_client(credentials: str) -> storage.Client:
    """Gets an instance of the storage client.

    The only parameter is the path to the credentials JSON file as a string.
    """
    return storage.Client.from_service_account_json(credentials)


def get_storage_bucket(
    client: storage.Client,
    bucket_name: str,
) -> storage.Bucket:
    """Gets the requested storage bucket."""
    return client.bucket(bucket_name)


def get_storage_blob(
    bucket: storage.Bucket,
    filename: str,
) -> storage.Blob:
    """Gets the requested storage blob from the provided bucket."""
    return bucket.blob(filename)


def upload_file_to_storage(
    bucket: storage.Bucket,
    source: str,
    destination: str,
) -> None:
    """Uploads a file to the provided storage bucket and returns the public URL.

    Requires the bucket object to be uploaded to, the source file path, and
    the destination file path.
    """
    blob = get_storage_blob(bucket, destination)
    blob.upload_from_filename(source)


def upload_image_to_storage(
    bucket: storage.Bucket,
    data: bytes,
    destination: str,
    content_type: str | None = None,
) -> None:
    """Uploads an image (as bytes) to the provided storage bucket.

    Requires the bucket object to be uploaded to, the image as bytes, and
    the destination file path.
    """
    blob = get_storage_blob(bucket, destination)
    blob.upload_from_string(data, content_type=content_type)


def upload_json_to_storage(
    bucket: storage.Bucket,
    data: dict | list | str,
    destination: str,
) -> None:
    """Uploads a JSON string to the provided storage bucket.

    Requires the bucket object to be uploaded to, the source string, and
    the destination file path.
    """
    if not isinstance(data, str):
        data = json.dumps(data)
    blob = get_storage_blob(bucket, destination)
    blob.upload_from_string(data, content_type="application/json")


def download_file_from_storage(
    bucket: storage.Bucket,
    source: str,
    destination: str,
) -> None:
    """Downloads data from the provided storage bucket and saves it to a file.

    Requires the bucket object to be downloaded from, the source file path,
    and the destination file path.
    """
    blob = get_storage_blob(bucket, source)
    blob.download_to_filename(destination)


def download_json_from_storage(
    bucket: storage.Bucket,
    source: str,
) -> Any:
    """Downloads data from the provided storage bucket and saves it to a file.

    Requires the bucket object to be downloaded from, the source file path,
    and the destination file path.
    """
    blob = get_storage_blob(bucket, source)
    data = blob.download_as_string()
    return json.loads(data)


def get_last_updated_time(
    bucket: storage.Bucket,
    filename: str,
) -> dt.datetime | None:
    """Gets the last updated time for the provided storage filename."""
    blob = get_storage_blob(bucket, filename)
    blob.reload()
    return blob.updated
