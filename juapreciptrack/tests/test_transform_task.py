# tests/test_transform_task.py
import unittest
from unittest.mock import patch, MagicMock
from pipeline.tasks.transform_task import extract_relevant_data


class TestTransformTask(unittest.TestCase):
    @patch('pipeline.tasks.transform_task.h3.geo_to_h3')
    @patch('pipeline.tasks.transform_task.ds.to_dask_dataframe')
    def test_extract_relevant_data(self, mock_to_dask_dataframe, mock_geo_to_h3):
        mock_ds = MagicMock()
        mock_df = MagicMock()
        mock_to_dask_dataframe.return_value = mock_df

        mock_partition = MagicMock()
        mock_geo_to_h3.side_effect = lambda lat, lon, res: f"h3_{lat}_{lon}_{res}"

        def mock_map_partitions(func):
            return func(mock_partition)

        mock_df.map_partitions.side_effect = mock_map_partitions

        result = extract_relevant_data(mock_ds)

        mock_to_dask_dataframe.assert_called_once()
        mock_geo_to_h3.assert_called()
        self.assertTrue(result.persist.called)


if __name__ == '__main__':
    unittest.main()
