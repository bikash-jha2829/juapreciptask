import os
import dask
import ray
import warnings
import logging
from dask.distributed import Client
from distributed import LocalCluster
from ray.util.dask import ray_dask_get, dataframe_optimize
from config.settings import (
    RAY_NUM_CPUS,
    RAY_SPILL_DIR,
    RAY_OBJECT_STORE_MEMORY,
    DASK_MEMORY_LIMIT,
    DASK_CONFIG,
    SUPPRESS_WARNINGS, DASK_WORKER_THREADS, DASK_NUM_WORKERS
)


def initialize_ray_and_dask():
    """Initialize Ray and configure Dask to use Ray as its scheduler."""

    # Suppress all warnings if configured to do so
    if SUPPRESS_WARNINGS:
        warnings.filterwarnings("ignore")

    # Set Dask and Ray logging levels from configuration
    logging.getLogger('distributed').setLevel(DASK_CONFIG['logging']['distributed'])
    logging.getLogger('ray').setLevel(DASK_CONFIG['logging']['ray'])

    ray.init(
        ignore_reinit_error=True,
        log_to_driver=False,
        num_cpus=RAY_NUM_CPUS,
        include_dashboard=True,
        object_store_memory=RAY_OBJECT_STORE_MEMORY,
    )

    dask.config.set(scheduler=ray_dask_get)
    dask.config.set(DASK_CONFIG)
    # Initialize LocalCluster with specific worker and memory settings
    cluster = LocalCluster(
        n_workers=DASK_NUM_WORKERS,  # Number of workers
        threads_per_worker=DASK_WORKER_THREADS,  # Ensuring one thread per worker
        memory_limit=DASK_MEMORY_LIMIT,  # Memory limit per worker
        local_directory=RAY_SPILL_DIR,  # Spill directory
    )

    client = Client(cluster)
    print(f"Dask client initialized. Dashboard available at: {client.dashboard_link}")
    return client
