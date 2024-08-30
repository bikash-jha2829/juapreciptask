# tests/test_ray_dask_init.py
import unittest
from unittest.mock import patch, MagicMock
from infrastructure.ray_dask_init import initialize_ray_and_dask


class TestRayDaskInit(unittest.TestCase):
    @patch('infrastructure.ray_dask_init.Client')
    @patch('infrastructure.ray_dask_init.dask.config.set')
    @patch('infrastructure.ray_dask_init.ray.init')
    def test_initialize_ray_and_dask(self, mock_ray_init, mock_dask_config_set, mock_client):
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        client = initialize_ray_and_dask()

        mock_ray_init.assert_called_once()
        mock_dask_config_set.assert_called()
        mock_client.assert_called_once()
        self.assertEqual(client, mock_client_instance)


if __name__ == '__main__':
    unittest.main()
