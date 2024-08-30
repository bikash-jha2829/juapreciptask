# config/settings.py

import os

# Ray configuration
RAY_NUM_CPUS = os.cpu_count()  # Number of CPUs to use
RAY_SPILL_DIR = "./spill/"  # Directory for spilling objects
RAY_OBJECT_STORE_MEMORY = 2 * 1024 ** 3  # Memory allocated to Ray's object store (2GB)

# Dask configuration
DASK_MEMORY_LIMIT = '16GB'  # Memory limit for Dask workers
DASK_SCHEDULER = "ray_dask_get"  # Scheduler to use with Dask (Ray's Dask integration)
DASK_SPILL_DIR = "./spill/"  # Directory for Dask worker spill files
DASK_CONFIG = {
    "distributed.worker.memory.target": 0.8,
    "distributed.worker.memory.spill": 0.75,
    "array.chunk-size": "32MB",
    "distributed.comm.timeouts.tcp": "120s",
    "distributed.comm.timeouts.connect": "120s",
    "distributed.worker.heartbeat.interval": "120s",
    # Logging configuration for Dask
    "logging": {
        "distributed": "INFO",  # Suppress distributed warnings, only show errors
        "ray": "INFO"  # Suppress Ray warnings, only show errors
    }

}

SUPPRESS_WARNINGS = True  # Control whether to suppress all warnings

