import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.backend.database.MongoDBConnector import MongoDBConnector

class PatientDAO:
    def __init__(self, db_connector: MongoDBConnector):
        """
        Data Access Object for retrieving patient records.
        :param db_connector: Instance of MongoDBConnector
        """
        self.db_connector = db_connector

    def get_patient_record(self, patient_id: str, collection_key: str):
        """
        Retrieve a patient's record from a specific collection.
        :param patient_id: The ID of the patient
        :param collection_key: The key for the collection in config.yaml
        :return: The patient's record or None if not found
        """
        collection = self.db_connector.get_collection(collection_key)
        return collection.find_one({"Patient_ID": patient_id})

