import logging
import dask
import ray
import xarray as xr

from config.config import CHUNK_SIZE


def load_datasets_with_dask(reference_ids):
    """
    Load datasets using Dask, leveraging the persisted Kerchunk references.

    Args:
        reference_ids (list): A list of Ray object references to Kerchunk references.

    Returns:
        xr.Dataset: An optimized xarray Dataset concatenated along the 'time' dimension.
    """
    references = ray.get(reference_ids)
    datasets = [
        dask.delayed(load_single_dataset)(reference) for reference in references
    ]
    combined_dataset = dask.delayed(xr.concat)(datasets, dim='time')
    optimized_dataset = combined_dataset.chunk(CHUNK_SIZE)
    optimized_dataset = optimized_dataset.persist()
    logging.info("Optimized dataset persisted.")
    return optimized_dataset


def load_single_dataset(reference):
    """
    Load a single dataset given a Kerchunk reference.
    The dataset is loaded with xarray using the Kerchunk engine,
    which allows for remote and lazy loading from cloud storage.

    Args:
        reference (str): A Kerchunk reference to a dataset.

    Returns:
        xr.Dataset: An xarray Dataset loaded using the Kerchunk engine.
    """
    ds = xr.open_dataset(
        reference,
        engine='kerchunk',
        backend_kwargs=dict(
            storage_options=dict(
                remote_protocol='gs',
                lazy=True,
                remote_options={"anon": True}
            )
        )
    )
    return ds
