# tests/test_stac_integration.py
import unittest
from unittest.mock import patch, MagicMock
from pipeline.tasks.stac_integration import create_stac_item_from_parquet, process_batch_and_update_catalog


class TestStacIntegration(unittest.TestCase):
    @patch('pipeline.tasks.stac_integration.dd.read_parquet')
    @patch('pipeline.tasks.stac_integration.pystac.Item')
    def test_create_stac_item_from_parquet(self, mock_Item, mock_read_parquet):
        mock_day = "2022-11-11"
        mock_file_path = "file_path"
        mock_df = MagicMock()
        mock_read_parquet.return_value = mock_df
        mock_item = MagicMock()
        mock_Item.return_value = mock_item

        item = create_stac_item_from_parquet(mock_day, mock_file_path)

        mock_read_parquet.assert_called_once_with(mock_file_path)
        mock_Item.assert_called_once()
        self.assertEqual(item, mock_item)

    @patch('pipeline.tasks.stac_integration.os.listdir')
    @patch('pipeline.tasks.stac_integration.load_datasets_with_dask')
    @patch('pipeline.tasks.stac_integration.extract_relevant_data')
    @patch('pipeline.tasks.stac_integration.pystac.Collection')
    @patch('pipeline.tasks.stac_integration.pystac.Catalog')
    def test_process_batch_and_update_catalog(self, mock_Catalog, mock_Collection, mock_extract_data, mock_load_datasets, mock_listdir):
        mock_batch = [1, 2, 3]
        mock_catalog = MagicMock()
        mock_load_datasets.return_value.compute.return_value = "combined_ds"
        mock_df = MagicMock()
        mock_extract_data.return_value = mock_df
        mock_df.to_parquet.return_value = None
        mock_listdir.return_value = ["file1.parquet", "file2.parquet"]

        process_batch_and_update_catalog(mock_batch, mock_catalog)

        mock_load_datasets.assert_called_once_with(mock_batch)
        mock_extract_data.assert_called_once()
        mock_df.to_parquet.assert_called_once()
        mock_Collection.assert_called()
        mock_catalog.add_child.assert_called()


if __name__ == '__main__':
    unittest.main()
