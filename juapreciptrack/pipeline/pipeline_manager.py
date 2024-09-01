import logging
import os
import time
import fsspec
import pystac
import ray
from dask.diagnostics import ProgressBar

from infrastructure.ray_dask_init import initialize_ray_and_dask
from pipeline.tasks.kerchunk_reference import generate_and_persist_kerchunk_reference
from pipeline.tasks.stac_integration import process_batch_and_update_catalog
from config.config import CATALOG_PATH, CATALOG_DIR, PARQUET_DIR, GCS_FILE_PATTERNS, UPDATE_STAC, BATCH_SIZE
from utils.common import ensure_directory_exists
from utils.logging_config import initialize_logging

logger = logging.getLogger(__name__)


def run_pipeline():
    """
    Run the complete data processing pipeline. This function handles the initialization
    of logging, directory structure, and the Ray and Dask clients. It processes data files
    based on patterns defined in the configuration, generates Kerchunk references, and updates
    the STAC catalog if configured to do so.

    Returns:
        None
    """
    initialize_logging()  # Initialize logging before anything else
    start = time.time()

    # Ensure required directories exist
    ensure_directory_exists(CATALOG_DIR)
    ensure_directory_exists(PARQUET_DIR)

    client = initialize_ray_and_dask()

    if UPDATE_STAC:
        ensure_directory_exists(CATALOG_DIR)
        if os.path.exists(CATALOG_PATH):
            catalog = pystac.Catalog.from_file(CATALOG_PATH)
        else:
            catalog = pystac.Catalog(id="precipitation-stac-catalog", description="A STAC catalog for precipitation data.")
    else:
        catalog = None

    all_reference_ids = []
    for pattern in GCS_FILE_PATTERNS:
        flist = fsspec.filesystem('gs', anon=True).glob(pattern)
        print(f"Found {len(flist)} files matching the pattern.")
        reference_ids = [generate_and_persist_kerchunk_reference.remote(url) for url in flist]
        all_reference_ids.extend(reference_ids)

    logger.info(f"Total references to process: {len(all_reference_ids)}")

    batch_size = BATCH_SIZE
    total_batches = len(all_reference_ids) // batch_size + (len(all_reference_ids) % batch_size > 0)
    logging.info(f"Total batches to process: {total_batches}")

    # Process each batch of references
    for i in range(0, len(all_reference_ids), batch_size):
        batch = all_reference_ids[i:i + batch_size]
        # Dask progress bar to track the computation progress
        with ProgressBar():
            process_batch_and_update_catalog(batch, catalog)
        logger.info(f"Processed batch {i // batch_size + 1} of {total_batches}")

    # Save and normalize the STAC catalog if updated
    if UPDATE_STAC:
        catalog.normalize_hrefs(CATALOG_DIR)
        catalog.save()

    end = time.time()
    elapsed_time_minutes = (end - start) / 60
    logger.info(f"Processing complete. Computation took {elapsed_time_minutes:.2f} minutes")

    # Cleanup the Dask client
    try:
        client.close()
    except Exception as e:
        logger.error(f"Error during Dask client shutdown: {e}")

    # Shutdown Ray
    try:
        ray.shutdown()
    except Exception as e:
        logger.error(f"Error during Ray shutdown: {e}")
