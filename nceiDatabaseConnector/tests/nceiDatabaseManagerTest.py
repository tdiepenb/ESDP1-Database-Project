import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import os
import psycopg2
from io import StringIO
from nceiDatabaseConnector.nceiDatabasePackage.nceiDatabaseManager import \
    NCEIDatabaseManager


class TestNCEIDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.manager = NCEIDatabaseManager(db_name="testdb", db_user="testuser", db_password="testpass",
                                           db_host="localhost", db_port="5432", debug_messages=True)
        self.connection_mock = MagicMock()
        self.cursor_mock = MagicMock()

    @patch('psycopg2.connect')
    def test_connect_to_db_success(self, mock_connect):
        mock_connect.return_value = self.connection_mock
        self.connection_mock.cursor.return_value = self.cursor_mock

        conn, cursor = self.manager.connect_to_db()
        self.assertEqual(conn, self.connection_mock)
        self.assertEqual(cursor, self.cursor_mock)

    @patch('psycopg2.connect')
    def test_insert_copy_success(self, mock_connect):
        mock_connect.return_value = self.connection_mock
        self.connection_mock.cursor.return_value = self.cursor_mock

        with patch('builtins.open',
                   unittest.mock.mock_open(read_data='id,latitude,longitude\n1,10,10\n2,20,20')) as mock_file:
            self.manager.insert_copy(file_path="test.csv", table_name="Station",
                                     columns=["id", "latitude", "longitude"])

        self.cursor_mock.copy_expert.assert_called()
        self.connection_mock.commit.assert_called()
        self.cursor_mock.execute.assert_called_with('SELECT COUNT(*) FROM "Station"')

    @patch('psycopg2.connect')
    def test_create_stations_table_success(self, mock_connect):
        mock_connect.return_value = self.connection_mock
        self.connection_mock.cursor.return_value = self.cursor_mock

        self.manager.create_stations_table()
        self.cursor_mock.execute.assert_called()
        self.connection_mock.commit.assert_called()

    @patch('psycopg2.connect')
    def test_create_climate_table_success(self, mock_connect):
        mock_connect.return_value = self.connection_mock
        self.connection_mock.cursor.return_value = self.cursor_mock

        self.manager.create_climate_table(2023)
        self.cursor_mock.execute.assert_called()
        self.connection_mock.commit.assert_called()

    def test_split_csv_file(self):
        content = "id,latitude,longitude\n1,10,10\n2,20,20\n3,30,30\n4,40,40\n"
        with patch('builtins.open', unittest.mock.mock_open(read_data=content)) as mock_file:
            mock_file.return_value.readlines.return_value = content.split('\n')
            chunks = self.manager.split_csv_file("test.csv", 2)

        expected_chunks = ["test_chunk0.csv", "test_chunk1.csv"]
        self.assertEqual(chunks, expected_chunks)

    @patch('psycopg2.connect')
    def test_is_valid_year(self, mock_connect):
        self.assertTrue(self.manager.is_valid_year(2023))

    @patch('psycopg2.connect')
    def test_is_year_in_db(self, mock_connect):
        mock_connect.return_value = self.connection_mock
        self.connection_mock.cursor.return_value = self.cursor_mock
        self.cursor_mock.fetchall.return_value = [(1,)]

        self.assertTrue(self.manager.is_year_in_db(2023))

    @patch('psycopg2.connect')
    def test_check_year(self, mock_connect):
        mock_connect.return_value = self.connection_mock
        self.connection_mock.cursor.return_value = self.cursor_mock
        self.cursor_mock.fetchall.return_value = [(1,)]

        self.assertTrue(self.manager.check_year(2023))


if __name__ == '__main__':
    unittest.main()
