import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.backend.database.PatientDAO import PatientDAO
from src.backend.database.MongoDBConnector import MongoDBConnector

class TestPatientDAO(unittest.TestCase):
    
    CONFIG_FILE_PATH = "config/config.yaml"
    
    def setUp(self):
        self.db_connector = MongoDBConnector(self.CONFIG_FILE_PATH)
        self.patient_dao = PatientDAO(self.db_connector)
    
    def tearDown(self):
        if self.db_connector.client:
            self.db_connector.close()

    def test_get_patient_by_id_from_patient_data_success(self):
        existent_patient_id = "1"
        records = self.patient_dao.__get_patient_by_id__(existent_patient_id, "patient_data")
        self.assertTrue(records[0]["Name"],"Bobby JacksOn")
    
    def test_get_patient_by_id_from_patient_diseases_success(self):
        existent_patient_id = "1"
        records = self.patient_dao.__get_patient_by_id__(existent_patient_id, "patient_diseases")
        self.assertTrue(records[0]["Doctor"],"Matthew Smith")
    
    def test_get_patient_by_id_from_patient_lab_reports_success(self):
        existent_patient_id = 1
        records = self.patient_dao.__get_patient_by_id__(existent_patient_id, "patient_lab_reports")
        self.assertTrue(records[0]["WBC"], 10.29)
    
    def test_get_patient_by_id_from_login_success(self):
        existent_patient_id = "1"
        records = self.patient_dao.__get_patient_by_id__(existent_patient_id, "login")
        self.assertTrue(records[0]["lower_username"], "bobby")
        self.assertTrue(records[0]["password"], "password")

    # def test_get_patient_record_failure(self):
    #     non_existent_patient_id = "0"
    #     records = self.patient_dao.__get_patient_record__(non_existent_patient_id)
    #     self.assertIsInstance(records, list)
    #     self.assertGreater(len(records), 0)

if __name__ == '__main__':
    unittest.main()