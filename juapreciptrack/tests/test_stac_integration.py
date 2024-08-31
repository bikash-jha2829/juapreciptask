import unittest
import os
import pandas as pd
import dask.dataframe as dd
import pystac
import tempfile
import shutil
from datetime import datetime

import ray

from pipeline.tasks.stac_integration import create_stac_item_from_parquet, process_batch_and_update_catalog


class TestStacProcessing(unittest.TestCase):

    def setUp(self):
        # Setup a temporary directory for Parquet and STAC catalog
        self.temp_dir = tempfile.mkdtemp()
        self.parquet_dir = os.path.join(self.temp_dir, 'parquet')
        self.catalog_dir = os.path.join(self.temp_dir, 'catalog')
        os.makedirs(self.parquet_dir)
        os.makedirs(self.catalog_dir)

        # Create a sample DataFrame
        data = {
            'h3_index': ['abc', 'def', 'ghi'],
            'tp': [0.1, 0.5, 0.3],
            'day': ['2023-08-30', '2023-08-30', '2023-08-30']
        }
        df = pd.DataFrame(data)
        self.ddf = dd.from_pandas(df, npartitions=1)

        # Write it as a Parquet file
        self.file_path = os.path.join(self.parquet_dir, 'test.parquet')
        self.ddf.to_parquet(self.file_path)

    def tearDown(self):
        # Remove temporary directories after the test
        shutil.rmtree(self.temp_dir)

    def test_create_stac_item_from_parquet(self):
        # Test the creation of a STAC item from a Parquet file
        stac_item = create_stac_item_from_parquet('2023-08-30', self.file_path)
        self.assertIsInstance(stac_item, pystac.Item)
        self.assertEqual(stac_item.properties['min_precipitation'], 0.1)
        self.assertEqual(stac_item.properties['max_precipitation'], 0.5)
        self.assertEqual(stac_item.properties['mean_precipitation'], 0.3)
        self.assertEqual(stac_item.properties['h3_indexes'], ['abc', 'def', 'ghi'])


if __name__ == '__main__':
    unittest.main()
