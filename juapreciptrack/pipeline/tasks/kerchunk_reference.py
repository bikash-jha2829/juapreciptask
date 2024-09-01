import ray
from kerchunk.netCDF3 import NetCDF3ToZarr


@ray.remote
def generate_and_persist_kerchunk_reference(file_url):
    """
    Generate a Kerchunk reference for a NetCDF file and persist it using Ray.

    Args:
        file_url (str): The URL of the NetCDF file in cloud storage.

    Returns:
        dict: A dictionary representing the Kerchunk reference.
    """
    full_url = f"gs://{file_url}"
    reference = NetCDF3ToZarr(full_url, storage_options={"anon": True}).translate()
    return reference
