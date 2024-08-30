# tests/test_kerchunk_reference.py
import unittest
from unittest.mock import patch, MagicMock
from pipeline.tasks.kerchunk_reference import generate_and_persist_kerchunk_reference

class TestKerchunkReference(unittest.TestCase):
    @patch('pipeline.tasks.kerchunk_reference.NetCDF3ToZarr')
    def test_generate_and_persist_kerchunk_reference(self, mock_NetCDF3ToZarr):
        mock_file_url = "file_url"
        mock_reference = {"mock": "reference"}
        mock_netCDF_instance = MagicMock()
        mock_netCDF_instance.translate.return_value = mock_reference
        mock_NetCDF3ToZarr.return_value = mock_netCDF_instance

        result = generate_and_persist_kerchunk_reference(mock_file_url)

        mock_NetCDF3ToZarr.assert_called_once_with(f"gs://{mock_file_url}", storage_options={"anon": True})
        self.assertEqual(result, mock_reference)

if __name__ == '__main__':
    unittest.main()
