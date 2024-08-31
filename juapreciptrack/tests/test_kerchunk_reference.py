import ray
from unittest.mock import patch
from pipeline.tasks.kerchunk_reference import generate_and_persist_kerchunk_reference


@patch('pipeline.tasks.kerchunk_reference.NetCDF3ToZarr.translate')
def test_generate_and_persist_kerchunk_reference(mock_translate):
    # Setup mock return value
    mock_translate.return_value = {
        'refs': {
            # Minimal valid structure
        },
        'version': 1
    }

    # Initialize Ray for the test
    ray.init(ignore_reinit_error=True)

    try:
        # Call the Ray remote function
        result_id = generate_and_persist_kerchunk_reference.remote('gcp-public-data-arco-era5/raw/date-variable-single_level/2022/11/01/total_precipitation/surface.nc')

        # Get the result
        result = ray.get(result_id)

        # Assertions
        assert isinstance(result, dict)
        assert 'refs' in result
        # mock_translate.assert_called_once()

    finally:
        # Shutdown Ray after the test
        ray.shutdown()
