# tests/test_pipeline_manager.py
import unittest
from unittest.mock import patch, MagicMock
from pipeline.pipeline_manager import run_pipeline


class TestPipelineManager(unittest.TestCase):
    @patch('pipeline.pipeline_manager.ensure_directory_exists')
    @patch('pipeline.pipeline_manager.initialize_ray_and_dask')
    @patch('pipeline.pipeline_manager.pystac.Catalog')
    @patch('pipeline.pipeline_manager.fsspec.filesystem')
    @patch('pipeline.pipeline_manager.generate_and_persist_kerchunk_reference')
    @patch('pipeline.pipeline_manager.process_batch_and_update_catalog')
    @patch('pipeline.pipeline_manager.time.time')
    def test_run_pipeline(self, mock_time, mock_process_batch, mock_generate_kerchunk, mock_fsspec, mock_Catalog, mock_initialize_ray, mock_ensure_directory):
        mock_time.side_effect = [0, 120]  # Simulate 2 minutes duration
        mock_client = MagicMock()
        mock_initialize_ray.return_value = mock_client
        mock_fs = MagicMock()
        mock_fsspec.return_value = mock_fs
        mock_fs.glob.return_value = ['file1', 'file2']

        run_pipeline()

        mock_ensure_directory.assert_called()
        mock_initialize_ray.assert_called_once()
        mock_generate_kerchunk.assert_called()
        mock_process_batch.assert_called()
        mock_time.assert_called()


if __name__ == '__main__':
    unittest.main()
