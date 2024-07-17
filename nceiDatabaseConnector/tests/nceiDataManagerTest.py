import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import requests
import pandas as pd
from io import StringIO
from nceiDatabaseConnector.nceiDatabasePackage.nceiDataManager import \
    NCEIDataManager


class TestNCEIDataManager(unittest.TestCase):

    @patch('requests.get')
    @patch('os.path.isfile')
    def test_download_stations_already_downloaded(self, mock_isfile, mock_requests_get):
        manager = NCEIDataManager()
        mock_isfile.return_value = True

        manager.download_stations()

        mock_requests_get.assert_not_called()
        self.assertEqual(mock_isfile.call_count, 2)

    @patch('requests.get')
    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_download_stations(self, mock_makedirs, mock_open, mock_isfile, mock_requests_get):
        manager = NCEIDataManager()
        mock_isfile.return_value = False
        mock_requests_get.return_value.ok = True
        mock_requests_get.return_value.content = b'test content'

        manager.download_stations()

        self.assertEqual(mock_isfile.call_count, 2)
        self.assertEqual(mock_requests_get.call_count, 2)
        self.assertEqual(mock_makedirs.call_count, 2)
        self.assertEqual(mock_open.call_count, 2)


    @patch('requests.get')
    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_download_year(self, mock_makedirs, mock_open, mock_isfile, mock_requests_get):
        manager = NCEIDataManager()
        mock_isfile.return_value = False
        mock_requests_get.return_value.ok = True
        mock_requests_get.return_value.content = b'test content'

        manager.download_year(2000, "./data/climate/script")

        mock_isfile.assert_called_once_with("./data/climate/script2000.csv.gz")
        mock_requests_get.assert_called_once()
        mock_makedirs.assert_called_once()
        mock_open.assert_called_once_with("./data/climate/script2000.csv.gz", "wb")

    @patch('requests.get')
    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_download_year_already_downloaded(self, mock_makedirs, mock_open, mock_isfile, mock_requests_get):
        manager = NCEIDataManager()
        mock_isfile.return_value = True

        manager.download_year(2000, "./data/climate/script")

        mock_isfile.assert_called_once_with("./data/climate/script2000.csv.gz")
        mock_requests_get.assert_not_called()
        mock_makedirs.assert_not_called()
        mock_open.assert_not_called()


if __name__ == '__main__':
    unittest.main()
