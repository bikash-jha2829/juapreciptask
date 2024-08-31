import logging
import os
import pystac
import dask.dataframe as dd
from datetime import datetime

import ray

from config.config import CATALOG_DIR, PARQUET_DIR, CATALOG_PATH, UPDATE_STAC
from pipeline.tasks.transform_task import extract_relevant_data
from pipeline.tasks.collect_task import load_datasets_with_dask

logger = logging.getLogger(__name__)


def create_stac_item_from_parquet(day, file_path):
    """Create a STAC item from a Parquet file."""
    df_file = dd.read_parquet(file_path, columns=['h3_index', 'tp', 'day'])

    h3_indexes_file = df_file['h3_index'].unique().compute()
    min_tp_file = df_file['tp'].min().compute()
    max_tp_file = df_file['tp'].max().compute()
    mean_tp_file = df_file['tp'].mean().compute()

    item = pystac.Item(
        id=f"item-{os.path.basename(file_path)}",
        geometry=None,
        bbox=None,
        datetime=datetime.fromisoformat(day),
        properties={
            "min_precipitation": float(min_tp_file),
            "max_precipitation": float(max_tp_file),
            "mean_precipitation": float(mean_tp_file),
            "h3_indexes": h3_indexes_file.tolist()
        }
    )

    item.add_asset("parquet", pystac.Asset(href=file_path, media_type="application/x-parquet"))
    return item


def process_batch_and_update_catalog(batch, catalog):
    """Process a batch of reference IDs, write to Parquet, and update the STAC catalog."""
    print(f"Processing batch with {len(batch)} references...")

    # Load and process datasets
    combined_ds = load_datasets_with_dask(batch)
    combined_ds = combined_ds.compute()
    df = extract_relevant_data(combined_ds)

    # Efficient bulk writing with partitioning
    df.to_parquet(
        PARQUET_DIR,
        engine='pyarrow',
        partition_on=['day'],
        compression='snappy',
        write_index=False,
        overwrite=False,
        write_metadata_file=True
    )

    # Update the STAC catalog if needed
    print("STAC catalog update enabled:", UPDATE_STAC)
    if UPDATE_STAC and catalog:
        print("Updating STAC catalog...")
        collections = {}
        days = df['day'].unique().compute()
        print(f"Processing {len(days)} unique days...")

        for day in days:
            day_parquet_dir = os.path.join(PARQUET_DIR, f'day={day}')
            collection_id = f"collection-{day}"
            collection_path = os.path.join(CATALOG_DIR, collection_id)

            # Use or create the collection for this day
            collection = collections.get(collection_id)
            if not collection:
                collection = pystac.Collection(
                    id=collection_id,
                    description=f"Precipitation data for {day}",
                    extent=pystac.Extent(
                        spatial=pystac.SpatialExtent([None]),
                        temporal=pystac.TemporalExtent([[datetime.fromisoformat(day), None]])
                    ),
                    license="proprietary"
                )
                collections[collection_id] = collection
                catalog.add_child(collection)

            # Add items to the collection
            parquet_files = [f for f in os.listdir(day_parquet_dir) if f.endswith('.parquet')]
            for file_name in parquet_files:
                file_path = os.path.join(day_parquet_dir, file_name)
                stac_item = create_stac_item_from_parquet(day, file_path)
                collection.add_item(stac_item)

            # Save the collection for the day
            logger.info(f"Saving collection for day {day} to {collection_path}")
            collection.normalize_hrefs(collection_path)
            collection.save()

        logger.info(f"Processed and updated catalog for batch with {len(batch)} references")
