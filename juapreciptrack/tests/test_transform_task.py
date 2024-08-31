import unittest
import h3
import pandas as pd
import xarray as xr
from datetime import datetime

from pipeline.tasks.transform_task import extract_relevant_data


class TestExtractRelevantData(unittest.TestCase):

    def setUp(self):
        # Create a sample dataset with 'time' as a dimension and 'latitude', 'longitude' as independent coordinates
        data = {
            'time': pd.to_datetime(['2023-08-30 00:00:00', '2023-08-30 01:00:00', '2023-08-30 02:00:00']),
            'latitude': [37.7749, 37.7749, 37.7749],  # Assuming the location is constant
            'longitude': [-122.4194, -122.4194, -122.4194],  # Assuming the location is constant
            'tp': [0.1, 0.5, 0.3]
        }

        # Create an xarray.Dataset
        self.ds = xr.Dataset(
            {
                "tp": (["time"], data["tp"]),  # 'tp' is a variable with 'time' as the dimension
            },
            coords={
                "time": data["time"],  # 'time' is the dimension
                "latitude": data["latitude"],  # Independent coordinates
                "longitude": data["longitude"]
            }
        )

    def test_extract_relevant_data(self):
        # Run the function to test
        result_df = extract_relevant_data(self.ds)

        # Compute the result to get the final DataFrame
        # result_df = result_df.compute()

        # Verify the H3 indices and 'day' column
        expected_h3_indices = [
            h3.geo_to_h3(37.7749, -122.4194, 10)
        ] * 27

        self.assertListEqual(result_df['h3_index'].tolist(), expected_h3_indices)
        self.assertListEqual(result_df['day'].tolist(), ['2023-08-30'])
        self.assertListEqual(result_df['tp'].tolist(), [0.1, 0.5, 0.3])


if __name__ == '__main__':
    unittest.main()
