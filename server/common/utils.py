# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Utility Functions."""

import multiprocessing
import os
import time
from typing import Any, List
import yaml

import asyncio
from google.cloud import storage

from server.config.logging import logger


def load_config_to_env(config_file: str) -> None:
    """Set config to environment variables.

    Args:
        config_file: path to .yaml file.
    """

    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        for key, value in config.items():
            os.environ[key] = str(value)

    except FileNotFoundError:
        logger.error(
            f"Error: Configuration file '{config_file}' not found."
        )
    except yaml.YAMLError as e:
        logger.error(
            f"Error: Invalid YAML format in '{config_file}': {e}"
        )


def get_gcs_mime_type(gcs_uri: str) -> str:
    """Return mime type for GCS file"""
    storage_client = storage.Client()
    bucket_name, object_name = gcs_uri[5:].split("/", 1)

    # Get the blob (object) and its metadata.
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.reload()
    return blob.content_type


def upload_file_to_gcs(
    file: str,
    bucket_name: str
) -> str:
    """Upload a file to GCS.

    Args:
        file: File uploaded.
        bucket_name: Bucket to upload file to.

    Returns:
        gcs_uri of uploaded file.
    """
    filename =  f"{time.strftime('%Y%m%d_%H%M%S')}_"\
      f"{file.filename}"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(filename)
    blob.upload_from_string(file.read(), content_type=file.content_type)

    gcs_uri = f"gs://{bucket_name}/{filename}"
    return gcs_uri



async def make_parallel_calls(
    items,
    async_processing_func,
    num_processes=None,
    extra_args=None
) -> List[Any]:
    """Helper function for parallel calls.

    Args:
        items: Items to send in paralle.
        async_processing_func: Function to call in parallel.
        num_processes (Optional): The number of processes to use.
        extra_args: If processing func requires additional args for each item.
    """
    results_queue = multiprocessing.Queue()
    processes = []
    for item in items:
        args = (item, results_queue, async_processing_func)
        if extra_args:
            args += extra_args

        p = multiprocessing.Process(
            target=process_item,
            args=args
        )
        processes.append(p)
        p.start()

    # Get results from Queue.
    results = []
    for _ in range(len(items)):
        results.append(await asyncio.to_thread(results_queue.get))

    for p in processes:
        p.join()
    return results


def process_item(item, results_queue, async_processing_function, extra_args=None) -> None:
    """Process item for parallelization.

    Args:
        item: Current item to process.
        results_queue: Multiprocessing queue to store processes to run.
        async_processing_function: Function to add to queue.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if extra_args:
        result = loop.run_until_complete(async_processing_function(item, extra_args))
    else:
        result = loop.run_until_complete(async_processing_function(item))
    results_queue.put(result)
    loop.close()
