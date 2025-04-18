from src.service.node_manager import NodeManager
from dotenv import load_dotenv
from src.models.query_engine import QueryEngine
from src.models.judge_llm import JudgeLLM
from src.backend.database.PatientDAO import PatientDAO
from src.backend.database.MongoDBConnector import MongoDBConnector
import time


def test_success(query_engine, judge_llm_manager, query):
    query_start = int(round(time.time()))
    full_response = query_engine.generate_full_response(query)
    query_end = int(round(time.time()))
    print(query)
    print(full_response.response)
    verify_start = int(round(time.time()))
    verification = judge_llm_manager.verify_suggestions(query, full_response, verbose=True)
    verify_end = int(round(time.time()))
    print("Verification: {}".format(verification))
    print()
    print("Finished! Query took {} seconds, verification took {} seconds".format(query_end - query_start,
                                                                                 verify_end - verify_start))


def main():
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
    model_name = "bigcode/starcoder2-7b"
    query_engine = QueryEngine(model_name, nodes)

    # Get judge model
    judge_model = "qwen/qwen-turbo"
    judge_llm_manager = JudgeLLM(judge_model)
    query = "What is the patient's father medical history?"

    test_success(query_engine, judge_llm_manager, query)


if __name__ == "__main__":
    main()
