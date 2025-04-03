import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.backend.database.MongoDBConnector import MongoDBConnector

class TestMongoDBConnector(unittest.TestCase):
    def test_connection_success(self):
        """
        Test if the connection to MongoDB is successful
        """
        config_file_path = "config/config.yaml"
        conn = MongoDBConnector(config_file_path)
        self.assertIsNotNone(conn.client, "MongoDB connection failed or not established correctly")
        conn.close_connection()


if __name__ == "__main__":
    unittest.main()
