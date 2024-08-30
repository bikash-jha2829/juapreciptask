import h3
import dask.dataframe as dd


def extract_relevant_data(ds, h3_resolution=10):
    """Extract relevant data (time, latitude, longitude, tp) and compute H3 index directly in Dask."""
    df = ds[['time', 'latitude', 'longitude', 'tp']].to_dask_dataframe()

    def compute_h3_for_partition(partition):
        """Compute h3_index for a partition of the Dask DataFrame."""
        h3_indices = [
            h3.geo_to_h3(lat, lon, h3_resolution) for lat, lon in zip(partition['latitude'], partition['longitude'])
        ]
        return partition.assign(h3_index=h3_indices)

    df = df.map_partitions(compute_h3_for_partition)
    df['day'] = df['time'].dt.strftime('%Y-%m-%d')
    return df.persist()
