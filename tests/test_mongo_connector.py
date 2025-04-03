import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.backend.database.MongoDBConnector import MongoDBConnector
import yaml
from pymongo.errors import ConnectionFailure

class TestMongoDBConnector(unittest.TestCase):

    CONFIG_FILE_PATH = "test_config.yaml"
    
    def setUp(self):
        test_config_data = {
            'mongodb': {
                'uri': 'mongodb+srv://genai:genai123@diy-doctor.b82as.mongodb.net/?appName=DIY-Doctor',
                'database_name': 'diy-doctor',
                'collections': {
                    'logins_collection': 'login',
                    'patient_data_collection': 'patient_data',
                    'family_medical_history_collection': 'family_medical_history',
                    'patient_diseases_collection': 'patient_diseases',
                    'patient_lab_reports_collection': 'patient_lab_reports'
                }
            }
        }
        with open(self.CONFIG_FILE_PATH, 'w') as f:
            yaml.dump(test_config_data, f)
        self.connector = MongoDBConnector(self.CONFIG_FILE_PATH)

    def tearDown(self):
        if os.path.exists(self.CONFIG_FILE_PATH):
            os.remove(self.CONFIG_FILE_PATH)
        if self.connector.client:
            self.connector.close()

    def test_read_config_success(self):
        self.assertIsNotNone(self.connector.config)
        self.assertIn('mongodb', self.connector.config)
        self.assertEqual(self.connector.config['mongodb']['database_name'], 'diy-doctor')

    def test_read_config_file_not_found(self):
        connector = MongoDBConnector("non_existent_config.yaml")
        self.assertEqual(connector.config, {})

    def test_read_config_invalid_yaml(self):
        invalid_config_path = "invalid_config.yaml"
        with open(invalid_config_path, 'w') as f:
            f.write("invalid: yaml: content")
        connector = MongoDBConnector(invalid_config_path)
        self.assertEqual(connector.config, {})
        import os
        os.remove(invalid_config_path)

    def test_connect_success(self):
        self.assertIsNotNone(self.connector.db)
        self.assertEqual(self.connector.db.name, 'diy-doctor')
        try:
            self.connector.db.command('ping')
            self.assertTrue(True) # If ping succeeds, connection is likely good
        except ConnectionFailure:
            self.fail("Failed to connect to MongoDB even though connection object was created.")

    def test_connect_failure_invalid_uri(self):
        invalid_config_path = "invalid_uri_config.yaml"
        invalid_config_data = {
            'mongodb': {
                'uri': 'invalid_uri',
                'database_name': 'invalid_db'
            }
        }
        with open(invalid_config_path, 'w') as f:
            yaml.dump(invalid_config_data, f)
        conn = MongoDBConnector(invalid_config_path)
        self.assertIsNone(conn.db)
        # with self.assertRaises(ConnectionFailure):
        #     conn.db.command("ping")
        os.remove(invalid_config_path)

    def test_close_connection(self):
        self.assertIsNotNone(self.connector.client)
        self.connector.close()
        self.assertIsNone(self.connector.client)

if __name__ == '__main__':
    unittest.main()