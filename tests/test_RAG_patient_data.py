import sys
import os
from src.backend.database.PatientDAO import PatientDAO
from src.backend.database.MongoDBConnector import MongoDBConnector
from dotenv import load_dotenv
from src.service.node_manager import NodeManager
from src.models.query_engine import QueryEngine

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(argv):
    load_dotenv()

    # Connect to database
    CONFIG_FILE_PATH = "config/config.yaml"
    db_connector = MongoDBConnector(CONFIG_FILE_PATH)
    patient_dao = PatientDAO(db_connector)

    # Get patient records
    existent_patient_id = "1"
    records = patient_dao.get_patient_records_from_all_collections(existent_patient_id)

    # Get nodes from patient records
    node_manager = NodeManager()
    node_manager.set_nodes_from_patient_data(records)
    nodes = node_manager.get_nodes()

    # Run test query
    model_name = "meta-llama/llama-3.2-3b-instruct"
    query_engine = QueryEngine(model_name, nodes)
    query = "What is the patient's father medical history?"
    print(query_engine.generate_response(query))

    # Close database connection
    if db_connector.client:
        db_connector.close()


if __name__ == "__main__":
    main(sys.argv)
