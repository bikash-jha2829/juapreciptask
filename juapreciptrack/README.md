# Steps to Run the Project

## Overview 

This guide will walk you through setting up and running the project.

This project processes precipitation data, integrates it with STAC catalogs, and optimizes it for use with Dask and Ray. The pipeline loads datasets, processes them into Parquet format, and updates a STAC catalog.

<!-- TOC -->
* [Steps to Run the Project](#steps-to-run-the-project)
  * [Overview](#overview-)
  * [Prerequisites](#prerequisites)
  * [Setup Instructions](#setup-instructions)
  * [2. Configure and run the Project](#2-configure-and-run-the-project)
    * [Dask Dashboard:  docs](#dask-dashboard-docs)
  * [Output Files](#output-files)
  * [How to use STAC catalog](#how-to-use-stac-catalog-)
  * [Local RUN logs](#local-run-logs)
    * [What happens after running the project?](#what-happens-after-running-the-project)
        * [1. Catalog Directory](#1-catalog-directory)
        * [2. Parquet Directory](#2-parquet-directory)
<!-- TOC -->


## Prerequisites

-[ ] **Python "^3.10"**: Ensure that Python is installed on your machine.
-[ ] **Poetry**: This project uses [Poetry](https://python-poetry.org/) for dependency management.

## Setup Instructions

1. **Install Poetry**

   If you don't have Poetry installed, you can install it using pip:

   ```bash
   pip install poetry
    ```

   ```bash
   poetry install
   ```

## 2. Configure and run the Project

The project’s configuration is centralized in two key files: `config/config.py` and `config/settings.py`. These files are crucial for defining settings like file paths, batch sizes, and other environment-specific variables.
```bash
cd juapreciptrack
python main.py
```


```python
# config/config.py
# This file defines directory paths and pipeline-specific settings. 
# For example, the BATCH_SIZE and GCS_FILE_PATTERNS variables are used to control the data processing:

BATCH_SIZE = 8

GCS_FILE_PATTERNS = [
    'gs://gcp-public-data-arco-era5/raw/date-variable-single_level/2022/12/*/total_precipitation/surface.nc',
    'gs://gcp-public-data-arco-era5/raw/date-variable-single_level/2022/11/*/total_precipitation/surface.nc',
]

# Flags like CREATE_PARQUET, UPDATE_STAC, and SUPPRESS_WARNINGS are available to manage different aspects of the pipeline’s behavior.

CREATE_PARQUET = True
UPDATE_STAC = True
SUPPRESS_WARNINGS = True

# config/settings.py
# This file contains the configuration for Ray and Dask, which are used for distributed computing:
# It specifies CPU allocation, memory limits, logging configurations, and how Dask should be integrated with Ray.

RAY_NUM_CPUS = os.cpu_count()
DASK_MEMORY_LIMIT = '16GB'

# Dask is configured to use Ray as its scheduler, ensuring efficient task execution and memory management.

```
### Dask Dashboard:  [docs](https://docs.dask.org/en/stable/dashboard.html)

**While the project is running, you can monitor the progress of each stage, as well as CPU and memory usage, through the Dask dashboard.**

**Note:** 
_If you notice that memory usage is high or the job is taking longer than expected, consider reducing the amount of data being processed. You can do this by adjusting the **file patterns and batch size** in the configuration._

Once you run the project you will see the dask and ray dashboard link in the console

```python
 python main.py

2024-08-30 14:54:29,044 INFO worker.py:1774 -- Started a local Ray instance. 
View the RAY dashboard at 127.0.0.1:8265 
Dask client initialized. 
Dashboard available at: http://127.0.0.1:8787/status

```


## Output Files

Once the pipeline successfully completes, you will find two main directories inside the `DATA_DIR` (typically named `data`):

1. **`catalog/`**:
   - catalog.json : This is the catalog which will be keep a href for all
   - Contains the STAC catalog files, organized by date. 
   - Each date has a `collection.json` file along with corresponding Parquet items (`item-part.*.parquet`) and their associated metadata (`item-part.*.parquet.json`).

3. **`parquet/`**:
   - Stores the processed data in Parquet format, partitioned by day.
   - Each day has multiple Parquet files (`part.*.parquet`), making it easy to manage and query the data by specific dates.

These directories structure the processed data and STAC metadata, allowing for efficient data retrieval and cataloging.


## How to use STAC catalog 

## How to Use STAC Catalog

The [STAC](https://stacspec.org/en) catalog is a powerful tool for organizing and querying geospatial data. It provides a standardized way to describe and access datasets, making it easier to discover and use data across different platforms and tools.

### Jupyter Notebook Example

You can explore an example Jupyter Notebook to understand how to read and query a STAC catalog:

- [Example Notebook](https://github.com/bikash-jha2829/juapreciptask/blob/main/juapreciptrack/notebooks/read_stac.ipynb)

### Flask-based API for Querying a SpatioTemporal Asset Catalog (STAC)

This project includes a Flask-based API to query a SpatioTemporal Asset Catalog (STAC).

#### Running the Flask API

You can run the Flask API by providing the path to your STAC catalog JSON file:

```bash
python stac_flask_query_api.py --catalog ../data/catalog/catalog.json
```

#### API Endpoints

1. **Root Endpoint**

   This endpoint simply returns a welcome message.

   ```bash
   curl -X GET "http://127.0.0.1:5000/"
   ```

2. **/search-parquet Endpoint**

   This endpoint returns the paths of Parquet files associated with a given H3 index and within a specified datetime range.

   ```bash
   curl -G "http://127.0.0.1:5000/search-parquet" \
   --data-urlencode "datetime_range=2022-12-01T00:00:00Z/2022-12-31T23:59:59Z" \
   --data-urlencode "h3_index=8a0326233ab7fff"
   ```

3. **/search-h3 Endpoint**

   This endpoint returns distinct H3 indexes that meet specific precipitation criteria within a given datetime range.

   ```bash
   curl -G "http://127.0.0.1:5000/search-h3" \
   --data-urlencode "datetime_range=2022-12-01T00:00:00Z/2022-12-31T23:59:59Z" \
   --data-urlencode "min_precipitation=0.01" \
   --data-urlencode "max_precipitation=0.03" \
   --data-urlencode "filter_type=max"
   ```

#### Additional Examples

- **Without Precipitation Filters (for /search-h3):**

   ```bash
   curl -G "http://127.0.0.1:5000/search-h3" \
   --data-urlencode "datetime_range=2022-12-01T00:00:00Z/2022-12-31T23:59:59Z"
   ```

- **With Only a Specific H3 Index (for /search-parquet):**

   ```bash
   curl -G "http://127.0.0.1:5000/search-parquet" \
   --data-urlencode "h3_index=8a0326233ab7fff"
   ```



For more context how to use STAC as api refer: https://github.com/microsoft/PlanetaryComputerExamples/blob/main/quickstarts/reading-stac.ipynb

## Local RUN logs

<details>
  <summary><b>Environment Setup and Installation Log (click to open)</b></summary>

```bash
(.venv) bikash@G9TLWLT47P juapreciptask-main % cd juapreciptrack 
(.venv) bikash@G9TLWLT47P juapreciptrack % python --version 
Python 3.10.6
(.venv) bikash@G9TLWLT47P juapreciptrack % poetry --version         
Poetry (version 1.8.3)
(.venv) bikash@G9TLWLT47P juapreciptrack % poetry install --no-cache
Installing dependencies from lock file

pyproject.toml changed significantly since poetry.lock was last generated. Run `poetry lock [--no-update]` to fix the lock file.
(.venv) bikash@G9TLWLT47P juapreciptrack % poetry lock --no-update
Resolving dependencies... (2.3s)

Writing lock file
(.venv) bikash@G9TLWLT47P juapreciptrack % poetry install --no-cache
Installing dependencies from lock file

Package operations: 128 installs, 0 updates, 0 removals

  - Installing mdurl (0.1.2)
  - Installing pyasn1 (0.6.0)
  - Installing cachetools (5.5.0)
  - Installing certifi (2024.7.4)
  - Installing charset-normalizer (3.3.2)
  - Installing idna (3.8)
  - Installing markdown-it-py (3.0.0)
  - Installing protobuf (5.28.0)
  - Installing pyasn1-modules (0.4.0)
  - Installing rsa (4.9)
  - Installing uc-micro-py (1.0.3)
  - Installing urllib3 (2.2.2)
  - Installing attrs (24.2.0)
  - Installing frozenlist (1.4.1)
  - Installing google-auth (2.34.0)
  - Installing googleapis-common-protos (1.65.0)
  - Installing linkify-it-py (2.0.3)
  - Installing locket (1.0.0)
  - Installing mdit-py-plugins (0.4.1)
  - Installing multidict (6.0.5)
  - Installing proto-plus (1.24.0)
  - Installing pygments (2.18.0)
  - Installing requests (2.32.3)
  - Installing rpds-py (0.20.0)
  - Installing six (1.16.0)
  - Installing toolz (0.12.1)
  - Installing zipp (3.20.1)
  - Installing aiohappyeyeballs (2.4.0)
  - Installing aiosignal (1.3.1)
  - Installing async-timeout (4.0.3)
  - Installing click (8.1.7)
  - Installing cloudpickle (3.0.0)
  - Installing fsspec (2024.6.1)
  - Installing google-api-core (2.19.2)
  - Installing google-crc32c (1.5.0)
  - Installing importlib-metadata (8.4.0)
  - Installing markupsafe (2.1.5)
  - Installing numpy (2.1.0)
  - Installing oauthlib (3.2.2)
  - Installing packaging (24.1)
  - Installing partd (1.4.2)
  - Installing python-dateutil (2.9.0.post0)
  - Installing pytz (2024.1)
  - Installing pyyaml (6.0.2)
  - Installing referencing (0.35.1)
  - Installing rich (13.8.0)
  - Installing typing-extensions (4.12.2)
  - Installing tzdata (2024.1)
  - Installing yarl (1.9.4)
  - Installing aiohttp (3.10.5)
  - Installing annotated-types (0.7.0)
  - Installing asciitree (0.3.3)
  - Installing contourpy (1.3.0)
  - Installing dask (2024.8.1)
  - Installing distlib (0.3.8)
  - Installing fasteners (0.19)
  - Installing filelock (3.15.4)
  - Installing google-cloud-core (2.4.1)
  - Installing google-resumable-media (2.7.2)
  - Installing jinja2 (3.1.4)
  - Installing jsonschema-specifications (2023.12.1)
  - Installing msgpack (1.0.8)
  - Installing numcodecs (0.13.0)
  - Installing opencensus-context (0.1.3)
  - Installing pandas (2.2.2)
  - Installing pillow (10.4.0)
  - Installing platformdirs (4.2.2)
  - Installing psutil (6.0.0)
  - Installing pyarrow (17.0.0)
  - Installing pydantic-core (2.20.1)
  - Installing sortedcontainers (2.4.0)
  - Installing requests-oauthlib (2.0.0)
  - Installing tblib (3.0.0)
  - Installing textual (0.78.0)
  - Installing tornado (6.4.1)
  - Installing wrapt (1.16.0)
  - Installing xyzservices (2024.6.0)
  - Installing zict (3.0.0)
  - Installing aiohttp-cors (0.7.0)
  - Installing bokeh (3.5.2): Pending...
  - Installing cfgv (3.4.0)
  - Installing cftime (1.6.4)
  - Installing bokeh (3.5.2): Installing...
  - Installing bokeh (3.5.2)
  - Installing cfgv (3.4.0)
  - Installing cftime (1.6.4)
  - Installing colorful (0.5.6)
  - Installing cramjam (2.8.3)
  - Installing dask-expr (1.1.11)
  - Installing decorator (5.1.1)
  - Installing distributed (2024.8.1)
  - Installing exceptiongroup (1.2.2)
  - Installing google-auth-oauthlib (1.2.1)
  - Installing google-cloud-storage (2.18.2)
  - Installing grpcio (1.66.1)
  - Installing h5py (3.11.0)
  - Installing identify (2.6.0)
  - Installing iniconfig (2.0.0)
  - Installing jsonschema (4.23.0)
  - Installing mccabe (0.7.0)
  - Installing memray (1.13.4)
  - Installing mypy-extensions (1.0.0)
  - Installing nodeenv (1.9.1)
  - Installing opencensus (0.11.4)
  - Installing pathspec (0.12.1)
  - Installing pluggy (1.5.0)
  - Installing prometheus-client (0.20.0)
  - Installing py-spy (0.3.14)
  - Installing pycodestyle (2.12.1)
  - Installing pydantic (2.8.2)
  - Installing pyflakes (3.2.0)
  - Installing smart-open (7.0.4)
  - Installing tomli (2.0.1)
  - Installing ujson (5.10.0)
  - Installing virtualenv (20.26.3)
  - Installing zarr (2.18.2)
  - Installing black (24.8.0)
  - Installing fastparquet (2024.5.0)
  - Installing flake8 (7.1.1)
  - Installing gcsfs (2024.6.1)
  - Installing h3 (3.7.7)
  - Installing h5netcdf (1.3.0)
  - Installing isort (5.13.2)
  - Installing kerchunk (0.2.6)
  - Installing netcdf4 (1.7.1.post2)
  - Installing pre-commit (3.8.0)
  - Installing pystac (1.10.1)
  - Installing pytest (8.3.2)
  - Installing ray (2.35.0)
  - Installing scipy (1.14.1)
  - Installing structlog (24.4.0)
  - Installing xarray (2024.7.0)
 ```
</details>

<details open>
  <summary><b>Project Execution Log (click to collapse)</b></summary>

```bash
(.venv) bikash@G9TLWLT47P juapreciptask-main % cd juapreciptrack
(.venv) bikash@G9TLWLT47P juapreciptrack % python main.py   
Created directory: /Users/bikash/planet/juagit/juapreciptask-main/data/catalog
Created directory: /Users/bikash/planet/juagit/juapreciptask-main/data/parquet
2024-08-31 20:14:41,085 INFO worker.py:1774 -- Started a local Ray instance. View the dashboard at 127.0.0.1:8265 
Dask client initialized. Dashboard available at: http://127.0.0.1:8787/status
Directory already exists: /Users/bikash/planet/juagit/juapreciptask-main/data/catalog
Found 31 files matching the pattern.
2024-08-31 20:14:47,230 - pipeline.pipeline_manager - INFO - Total references to process: 31
2024-08-31 20:14:47,230 - root - INFO - Total batches to process: 4
Processing batch with 8 references...
2024-08-31 20:14:54,689 - root - INFO - Optimized dataset persisted.
STAC catalog update enabled: True
Updating STAC catalog...
2024-08-31 20:16:31,030 - distributed.shuffle._scheduler_plugin - WARNING - Shuffle dd97d1ca1fbd8a22d4f68f2a7dd0f9c8 initialized by task ('shuffle-transfer-dd97d1ca1fbd8a22d4f68f2a7dd0f9c8', 9) executed on worker tcp://127.0.0.1:54155
2024-08-31 20:16:37,096 - distributed.shuffle._scheduler_plugin - WARNING - Shuffle dd97d1ca1fbd8a22d4f68f2a7dd0f9c8 deactivated due to stimulus 'task-finished-1725128197.093463'
Processing 8 unique days...
2024-08-31 20:16:38,446 - distributed.shuffle._scheduler_plugin - WARNING - Shuffle 54c1ae0e51e45798b8d258354cc58541 initialized by task ('shuffle-transfer-54c1ae0e51e45798b8d258354cc58541', 0) executed on worker tcp://127.0.0.1:54155
2024-08-31 20:16:38,587 - distributed.shuffle._scheduler_plugin - WARNING - Shuffle 54c1ae0e51e45798b8d258354cc58541 deactivated due to stimulus 'task-finished-1725128198.586661'
...
2024-08-31 20:24:16,183 - distributed.shuffle._scheduler_plugin - WARNING - Shuffle ced8964f8b674f93abe8f3c5f32b5355 initialized by task ('shuffle-transfer-ced8964f8b674f93abe8f3c5f32b5355', 0) executed on worker tcp://127.0.0.1:54156
2024-08-31 20:24:16,329 - distributed.shuffle._scheduler_plugin - WARNING - Shuffle ced8964f8b674f93abe8f3c5f32b5355 deactivated due to stimulus 'task-finished-1725128656.327584'
2024-08-31 20:24:17,153 - pipeline.tasks.stac_integration - INFO - Saving collection for day 2022-12-31 to /Users/bikash/planet/juagit/juapreciptask-main/data/catalog/collection-2022-12-31
2024-08-31 20:24:17,569 - pipeline.tasks.stac_integration - INFO - Processed and updated catalog for batch with 7 references
2024-08-31 20:24:17,592 - pipeline.pipeline_manager - INFO - Processed batch 4 of 4
2024-08-31 20:24:32,118 - pipeline.pipeline_manager - INFO - Processing complete. Computation took 9.87 minutes
```
</details>



### What happens after running the project?

After running the project, the pipeline processes the precipitation data, generates Parquet files, and updates the STAC catalog. 
The processed data is stored in the `data` directory( (the location is configurable via config.py), with two main subdirectories: catalog and parquet.


##### 1. Catalog Directory

The `catalog` directory contains collections that are partitioned by date. Each date-specific folder includes:
- A `collection.json` file.
- Parquet files, each with an associated JSON metadata file.

The structure also includes a STAC index organized by date and H3 indices.

<details open>
  <summary><b>Directory Structure:(click to collapse)</b></summary>


```bash
data/
├── catalog
│   ├── catalog.json
│   ├── collection-2022-12-01
│   │   ├── collection.json
│   │   ├── item-part.0.parquet
│   │   │   └── item-part.0.parquet.json
│   │   └── item-part.1.parquet
│   │       └── item-part.1.parquet.json
│   ├── collection-2022-12-02
│   │   ├── collection.json
│   │   ├── item-part.2.parquet
│   │   │   └── item-part.2.parquet.json
│   │   └── item-part.3.parquet
│   │       └── item-part.3.parquet.json
│   └── ... (other dates)
```
</details>


##### 2. Parquet Directory

The `parquet` directory contains parquet files that are partitioned by date. Each date-specific folder holds multiple parts of the parquet files.

<details open>
  <summary><b>Directory Structure:(click to collapse)</b></summary>

```bash
data/
└── parquet
    ├── _common_metadata
    ├── _metadata
    ├── day=2022-12-01
    │   ├── part.0.parquet
    │   └── part.1.parquet
    ├── day=2022-12-02
    │   ├── part.2.parquet
    │   └── part.3.parquet
    ├── day=2022-12-03
    │   ├── part.4.parquet
    │   └── part.5.parquet
    └── ... (other dates)
```
</details>
