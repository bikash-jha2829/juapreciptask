import os

# Set BASE_DIR to the parent directory of juapreciptrack
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Paths to data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
PARQUET_DIR = os.path.join(DATA_DIR, 'parquet')
RAY_SPILL_DIR = "./spill/"

# Pipeline Configuration
BATCH_SIZE = 16
GCS_FILE_PATTERNS = [
    'gs://gcp-public-data-arco-era5/raw/date-variable-single_level/2022/12/11/total_precipitation/surface.nc',
    # 'gs://gcp-public-data-arco-era5/raw/date-variable-single_level/2022/10/*/total_precipitation/surface.nc'  pass if we need to load all 2022/10 files
]
# Flags to control pipeline execution
CREATE_PARQUET = True
UPDATE_STAC = True
SUPPRESS_WARNINGS = True  # Logging and Warnings Configuration
CHUNK_SIZE = {'time': 24, 'latitude': 720, 'longitude': 1440} # optimize this param if you ran into OOM issue

# STAC Catalog Configuration
CATALOG_ID = "precipitation-stac-catalog"
CATALOG_DESCRIPTION = "A STAC catalog for precipitation data."
CATALOG_DIR = os.path.join(DATA_DIR, 'catalog')
CATALOG_PATH = os.path.join(CATALOG_DIR, 'catalog.json')

# Environment Configuration
ENVIRONMENT = "development"  # todo: need to work on it later
