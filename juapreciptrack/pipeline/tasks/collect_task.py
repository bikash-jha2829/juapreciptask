import logging

import dask
import ray
import xarray as xr

from config.config import CHUNK_SIZE


def load_datasets_with_dask(reference_ids):
    """Load datasets using Dask, leveraging the persisted Kerchunk references."""
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
    """Load a single dataset given a Kerchunk reference."""
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
