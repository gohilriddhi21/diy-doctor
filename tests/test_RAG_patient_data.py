import sys
from src.backend.database.PatientDAO import PatientDAO
from src.backend.database.MongoDBConnector import MongoDBConnector
from dotenv import load_dotenv


def main(argv):
    load_dotenv()

    # Connect to database
    CONFIG_FILE_PATH = "config/config.yaml"
    db_connector = MongoDBConnector(CONFIG_FILE_PATH)
    patient_dao = PatientDAO(db_connector)

    # Get patient records
    existent_patient_id = "1"
    records = patient_dao.get_patient_records_from_all_collections(existent_patient_id)

    print(records)
    for record in records:
        print(record)

    # Close database connection
    if db_connector.client:
        db_connector.close()


if __name__ == "__main__":
    main(sys.argv)
