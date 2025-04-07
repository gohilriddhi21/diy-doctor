import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.backend.database.MongoDBConnector import MongoDBConnector
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PatientDAO:
    def __init__(self, db_connector: MongoDBConnector):
        """
        DAO for retrieving patient records.
        :param db_connector: Instance of MongoDBConnector
        """
        self.db_connector = db_connector
    
    def __get_patient_by_id__(self, patient_id: str, collection_key: str):
        """
        Retrieve a patient's record from a specific collection.
        :param patient_id: The ID of the patient
        :param collection_key: The key for the collection in config.yaml
        :return: The patient's record or None if not found
        """
        collection = self.db_connector.db.get_collection(collection_key)
        return list(collection.find({"Patient_ID": patient_id}))

    def get_patient_records_from_all_collections(self, patient_id: str):
        """
        Retrieve a patient's records from all collections in the database.
        :param patient_id: The ID of the patient
        :return: A list of patient records from all collections
        """
        patient_records = []
        try:
            collections = self.db_connector.config['mongodb']['collections']['patient'].values()        
            for collection_name in collections:
                logger.info("Retrieving patient records from collection: %s", collection_name)
                result = self.__get_patient_by_id__(patient_id, collection_name)
                if result:
                    logger.info("Found patient records in collection %s", collection_name)
                    patient_records.extend(result)
                logger.info("Patient records retrieved from collection %s", collection_name)
        except Exception as e:
            logger.error(f"Error retrieving patient records: {e}")
        
        return patient_records if patient_records else None
