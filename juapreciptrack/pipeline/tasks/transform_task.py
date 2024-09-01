import h3
import xarray as xr

from config.config import CHUNK_SIZE


def extract_relevant_data(ds, h3_resolution=10, output_path="output.parquet"):
    """
    Compute H3 index directly within an xarray.Dataset, extract relevant data, and save the results to Parquet.

    Args:
        ds (xr.Dataset): The xarray Dataset containing the data to be processed.
        h3_resolution (int): The resolution of the H3 index. Default is 10.
        output_path (str): The path where the Parquet file should be saved. Default is "output.parquet".

    Returns:
        dd.DataFrame: A Dask DataFrame containing the extracted and processed data.
    """

    # Function to compute H3 index
    def compute_h3(lat, lon):
        return h3.geo_to_h3(lat, lon, h3_resolution)

    # Apply the H3 computation using Xarray `apply_ufunc` with Dask
    h3_indices = xr.apply_ufunc(
        compute_h3,
        ds['latitude'], ds['longitude'],
        vectorize=True,  # Vectorized the function, allowing it to be applied element-wise
        dask='parallelized',  # Enables Dask for parallel processing
        output_dtypes=[str]  # The H3 index is a string
    )

    # Add the H3 index as a new coordinate or variable
    ds = ds.assign_coords(h3_index=h3_indices)

    # Extract the day from the time coordinate
    ds = ds.assign(day=ds['time'].dt.strftime('%Y-%m-%d'))

    # Convert to Dask DataFrame for Parquet export
    df = ds[['time', 'latitude', 'longitude', 'tp', 'h3_index', 'day']].to_dask_dataframe()

    return df
