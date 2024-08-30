# Steps to Run the Project


This guide will walk you through setting up and running the project.

This project processes precipitation data, integrates it with STAC catalogs, and optimizes it for use with Dask and Ray. The pipeline loads datasets, processes them into Parquet format, and updates a STAC catalog.

## Prerequisites

- **Python "^3.10"**: Ensure that Python is installed on your machine.
- **Poetry**: This project uses [Poetry](https://python-poetry.org/) for dependency management.

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

The [STAC](https://stacspec.org/en) catalog is a powerful tool for organizing and querying geospatial data. It provides a standardized way to describe and access datasets, making it easier to discover and use data across different platforms and tools.

Jupyter Notebook Attached.
https://github.com/bikash-jha2829/juapreciptask/blob/main/juapreciptrack/notebooks/read_stac.ipynb

For more context how to use STAC as api refer: https://github.com/microsoft/PlanetaryComputerExamples/blob/main/quickstarts/reading-stac.ipynb
