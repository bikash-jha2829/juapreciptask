import logging
from config.settings import DASK_CONFIG


def initialize_logging():
    """Initialize logging configuration."""
    logging.basicConfig(
        level=logging.INFO,  # Set the root logger to INFO level
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Set the specific logger level for 'distributed' and 'ray'
    logging.getLogger('distributed').setLevel(DASK_CONFIG['logging']['distributed'])
    logging.getLogger('ray').setLevel(DASK_CONFIG['logging']['ray'])
