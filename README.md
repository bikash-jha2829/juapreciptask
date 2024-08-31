# JuaPrecipTask

## NetCDF4 to Parquet Conversion Pipeline + STAC Catalog

### PS
- 🚀 **Dask, Ray, and Xarray** are our distributed superheroes for data processing!
- 🖥️ **Running Locally?** Remember, we’re not in full driver-worker mode here, so stick with a smaller dataset for smooth sailing. (Refer juapreciptrack/config.py -> BATCH_SIZE)
- ⚡ **Shortcut Alert!** You could load data into **GeoPandas** and loop through it for faster local processing—but that’s not the distributed or production-grade way.
- 📈 **Geek Out with Dask Dashboard!** Dive in to monitor memory usage and track stage progress like a pro.
- 📚 **How to Run**: For detailed instructions, refer to the **README.md** inside.
- 📓 **STAC Catalog**: Check out our Jupyter Notebook for a straightforward example of how to query datasets on the STAC catalog. For more details, refer to the juapreciptrack/README.md file inside.

## Overview

This project is designed to convert NetCDF4 files stored in Google Cloud Storage (GCS) into Apache Parquet files, optimized for querying and filtering by timestamp and a hierarchical geospatial index (H3). The pipeline utilizes Ray and Dask for distributed processing, making it scalable and flexible enough to handle large datasets and complex workflows.

### Data Source

The source data consists of ERA5 total precipitation data for the year 2022, available in NetCDF4 format. The data can be accessed from the ARCO dataset hosted at the following GCS path:

``gs://gcp-public-data-arco-era5/raw/date-variable-single_level/``



### Pipeline Workflow

![ARC](https://github.com/user-attachments/assets/a01439e1-cb93-48a1-8cb4-223d2a1827cb)


The pipeline follows these key steps:

1. **Generate Kerchunk References**: Create lightweight references for NetCDF4 files to enable efficient data access.
2. **Distributed Processing with Ray and Dask**: Process the data across multiple nodes using Ray and Dask.
3. **Data Transformation and Enrichment**: Extract relevant variables, create H3 indices, and prepare the data for storage.
4. **Load Data into Parquet**: Save the processed data into Parquet files on GCS.
5. **STAC Catalog Management**: Update a SpatioTemporal Asset Catalog (STAC) for efficient metadata management and search capabilities.

### Key Features

- **Queryable Parquet Dataset**: The Parquet files support efficient filtering by timestamp and geospatial H3 indices.
- **Scalable and Distributed Processing**: The pipeline leverages Ray and Dask for scalable processing across multiple nodes.
- **Flexible Architecture**: Designed to handle large-scale geospatial data and machine learning workloads.
- **STAC API Integration**: Uses the STAC API for managing and searching metadata, facilitating quick data discovery.

### Considerations

#### Apache Beam vs. Ray & Dask

- **Apache Beam**: Ideal for processing tasks within the Google Cloud ecosystem, but less flexible for external data sources(S3/NASA ERA5/SENTINEL DATASET) and machine learning workloads.
- **Ray & Dask**: Chosen for their flexibility in handling large datasets and ability to integrate with other data sources, such as AWS S3 or NASA datasets. This approach also supports distributed machine learning workloads, making it more versatile for future extensions.

#### Search Engine Integration

The pipeline uses the STAC API to manage metadata, allowing for efficient searches without loading entire Parquet files into memory. This supports queries such as:

- Filtering by precipitation values.
- Identifying regions (H3 indices) with specific precipitation characteristics.
- Retrieving lists of Parquet files based on temporal and spatial criteria.

### Why Kerchunk?

When dealing with large-scale NetCDF4 data, Xarray (XR) is a powerful library due to its support for lazy loading and distributed processing with Dask. However, directly loading remote NetCDF4 files from GCS using `gcsfs` is not yet fully supported, leading to potential inefficiencies.

#### Challenges with Direct NetCDF4 Access

- **Inefficiencies**: Directly accessing remote NetCDF4 files can be slow and resource-intensive and not supported with Xarray, especially when dealing with large datasets.
- **Scalability Issues**: Downloading files locally for processing limits the ability to scale the pipeline across multiple nodes.

#### Approach 1: Download Files Locally

This method involves downloading the NetCDF4 files locally before processing them. While this ensures compatibility, it is not optimal for large-scale, distributed processing due to the time and storage resources required.

#### Approach 2: Use Kerchunk for Efficient Access

Kerchunk provides a more efficient solution by creating lightweight, JSON-based references to the NetCDF4 files. These references allow Xarray to load only the necessary data, avoiding the need to download entire files.

**Benefits of Using Kerchunk:**

- **Optimized Data Access**: Load only the required portions of the data, reducing memory usage and speeding up processing.
- **Enable Distributed Processing**: Kerchunk references are easy to distribute across nodes, enhancing parallel processing capabilities.
- **No Local Storage Requirements**: Eliminates the need for local storage of large files, saving both time and resources.

#### Implementation in the Pipeline

In this pipeline, Kerchunk is used to generate references for the NetCDF4 files stored in GCS. Xarray, combined with Kerchunk, reads these references efficiently. Ray is utilized to parallelize the generation and processing of these references, ensuring scalability and performance across large datasets.

## Usage

To execute the pipeline, run the `run_pipeline` function in the `pipeline_manager.py` module. 

```python main.py```


### Prerequisites
```python
Install poetry

cd juapreciptrack
poetry install
```

## Quick run

```bash
cd juapreciptrack
python main.py
```

### Run tests
```bash
cd juapreciptrack
pytest -v tests/
```
