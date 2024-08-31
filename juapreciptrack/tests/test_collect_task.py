# tests/test_collect_task.py
import unittest
from unittest.mock import patch, MagicMock
from pipeline.tasks.collect_task import load_datasets_with_dask, load_single_dataset


class TestCollectTask(unittest.TestCase):
    @patch('pipeline.tasks.collect_task.xr.open_dataset')
    def test_load_single_dataset(self, mock_open_dataset):
        mock_reference = "mock_reference"
        mock_ds = MagicMock()
        mock_open_dataset.return_value = mock_ds

        ds = load_single_dataset(mock_reference)

        mock_open_dataset.assert_called_once_with(
            mock_reference,
            engine='kerchunk',
            backend_kwargs=dict(
                storage_options=dict(
                    remote_protocol='gs',
                    lazy=True,
                    remote_options={"anon": True}
                )
            )
        )
        self.assertEqual(ds, mock_ds)

    @patch('pipeline.tasks.collect_task.dask.delayed')
    @patch('pipeline.tasks.collect_task.ray.get')
    def test_load_datasets_with_dask(self, mock_ray_get, mock_dask_delayed):
        mock_reference_ids = [1, 2, 3]
        mock_ray_get.return_value = ["ref1", "ref2", "ref3"]
        mock_dask_instance = MagicMock()
        mock_dask_delayed.return_value = mock_dask_instance

        result = load_datasets_with_dask(mock_reference_ids)

        mock_ray_get.assert_called_once_with(mock_reference_ids)
        self.assertEqual(len(mock_dask_delayed.mock_calls), 10)


if __name__ == '__main__':
    unittest.main()
