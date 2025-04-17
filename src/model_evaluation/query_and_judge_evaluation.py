# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# query_and_judge_evaluation.py - Script to evaluate every possible pair of query engine and judge model

import sys
from src.models.model_loading_function import MODEL_NAMES
from src.backend.database.PatientDAO import PatientDAO
from src.backend.database.MongoDBConnector import MongoDBConnector
from src.service.node_manager import NodeManager
from src.models.query_engine import QueryEngine
from src.models.judge_llm import JudgeLLM
from llama_index.core.evaluation import RetrieverEvaluator, generate_question_context_pairs
import pandas as pd
import os
import asyncio
from dotenv import load_dotenv
import time


def return_query_set():
    """
    The query set to evaluate faithfulness and relevancy.
    :return: The queries in a list
    """
    queries = [
        "What is the patient's father's medical history?",
        "What is the patient's blood type?",
        "Did the patient have a medical condition in 2021?",
        "Who is the patient's insurance providers?",
        "What medications (if any) are the patient using?",
        "What is the patient's preferred hospital?",
        "Why was the patient last admitted?",
        "Are the patient's parents' medical history the same?",
        "What is the patient's gender?",
        "From the patient's lab reports, what are the two lowest and highest fields?"
    ]
    return queries


def load_records_as_nodes(patient_id):
    """
    Loads all records for a patient ID into nodes for RAG.
    Requires open and closing a MongoDB connection (handled within function)
    :param patient_id: The patient ID to retrieve records for
    :return: The nodes to use in RAG
    """
    # Connect to database
    CONFIG_FILE_PATH = "config/config.yaml"
    db_connector = MongoDBConnector(CONFIG_FILE_PATH)
    patient_dao = PatientDAO(db_connector)

    # Get patient records
    records = patient_dao.get_patient_records_from_all_collections(patient_id)

    # Get nodes from patient records
    node_manager = NodeManager()
    node_manager.set_nodes_from_patient_data(records)
    nodes = node_manager.get_nodes()

    # Close database connection
    if db_connector.client:
        db_connector.close()

    # Return nodes
    return nodes


def evaluate_query(query, query_engine, judge_llm):
    """
    Evaluates a query response using the judge LLM
    :param query:        The query to evaluate the response to
    :param query_engine: The query engine to generate a response
    :param judge_llm:    The judge LLM to evaluate the faithfulness/relevancy of the response
    :return: The evaluation scores for the query
    """
    # Query start time
    query_start = time.time()

    # Get the full response
    response = query_engine.generate_full_response(query)

    # Extract components of response
    response_text = response.response
    response_context = "\n".join([node.get_content() for node in response.source_nodes])

    # Get faithfulness and relevancy scores
    faithfulness_score = judge_llm.evaluate_faithfulness(response)
    relevancy_score = judge_llm.evaluate_relevancy(query, response)

    # Query response end time
    query_end = time.time()
    full_response_time = query_end - query_start

    # Create a dictionary of the results from the query
    response_evaluation = {
        "query": query,
        "response": response_text,
        "context": response_context,
        "faithfulness": faithfulness_score,
        "relevancy": relevancy_score,
        "full_response_time": full_response_time
    }

    return response_evaluation


def get_qa_results(patient_record_nodes, query_engine, query_model_name):
    """
    Gets the question-answers results metrics (e.g. recall score)
    using the llama index evaluator for question-context pairs
    :param patient_record_nodes: The nodes to evaluate on
    :param query_engine:         The query engine being used to generate responses
    :param query_model_name:     The name of the model being used to generate queries
    :return: The full results from the QA set
    """
    # Create a QA dataset
    qa_dataset = generate_question_context_pairs(nodes=patient_record_nodes, llm=query_engine.get_llm(),
                                                 num_questions_per_chunk=1)

    # Evaluate LLM with the QA dataset
    retriever_evaluator = RetrieverEvaluator.from_metric_names(["mrr", "hit_rate", "precision", "recall"],
                                                               retriever=query_engine.get_retriever())
    qa_eval_results = asyncio.run(retriever_evaluator.aevaluate_dataset(qa_dataset))
    per_metric_results = [result.metric_vals_dict for result in qa_eval_results]

    # Create a dataframe from the metrics
    df_metrics = pd.DataFrame(per_metric_results)

    # Create dictionary for means of results per model
    qa_eval_dict = {
        "query_llm": query_model_name,
        "mrr": df_metrics['mrr'].mean(),
        "hit_rate": df_metrics['hit_rate'].mean(),
        "precision": df_metrics['precision'].mean(),
        "recall": df_metrics['recall'].mean()
    }
    return qa_eval_dict


def evaluate_model_pairs(patient_id, query_questions, output_dir):
    """
    Runs the full evaluation of all models for a given patient
    :param patient_id:      The patient ID to evaluate records with
    :param query_questions: The query questions to evaluate faithfulness and relevancy with
    :param output_dir:      The output directory to save csv results
    :return: None
    """
    # Get the records for this patient id as nodes for the LLM's to use
    patient_record_nodes = load_records_as_nodes(patient_id)

    # Create empty dataframe for query responses
    query_responses_full = pd.DataFrame(columns=["query_llm", "judge_llm", "query", "response", "context",
                                                 "faithfulness", "relevancy", "full_response_time"])

    query_responses_avg = pd.DataFrame(columns=["query_llm", "judge_llm", "faithfulness_avg", "relevancy_avg",
                                                "avg_response_time"])

    # Create empty dataframe for qa results
    qa_results = pd.DataFrame(columns=["query_llm", "mrr", "hit_rate", "precision", "recall"])

    # Create a query engine and judge using the correct names for this pass
    for query_model_name in MODEL_NAMES:
        query_engine = QueryEngine(query_model_name, patient_record_nodes)

        for judge_model_name in MODEL_NAMES:
            # Prevent same-same comparisons
            if judge_model_name == query_model_name:
                continue

            # Start message
            print("Starting evaluation for query model: {}, judge model: {}".format(query_model_name, judge_model_name))

            # Create the query engine and judge from their respective names
            judge_llm = JudgeLLM(judge_model_name)

            # Evaluate each query
            faithfulness_sum = 0
            relevancy_sum = 0
            query_time_sums = 0
            for query in query_questions:
                query_evaluation = evaluate_query(query, query_engine, judge_llm)
                faithfulness_sum += query_evaluation['faithfulness']
                relevancy_sum += query_evaluation['relevancy']
                query_time_sums += query_evaluation['full_response_time']
                query_evaluation["query_llm"] = query_model_name
                query_evaluation["judge_llm"] = judge_model_name
                query_responses_full.loc[len(query_responses_full)] = query_evaluation

            # Get the averages and create dictionary
            faithfulness_avg = faithfulness_sum / len(query_questions)
            relevancy_avg = relevancy_sum / len(query_questions)
            avg_response_time = query_time_sums / len(query_questions)

            avg_dictionary = {
                "query_llm": query_model_name,
                "judge_llm": judge_model_name,
                "faithfulness_avg": faithfulness_avg,
                "relevancy_avg": relevancy_avg,
                "avg_response_time": avg_response_time
            }

            # Add to dataframe of averages
            query_responses_avg.loc[len(query_responses_avg)] = avg_dictionary

            # Save results to csv
            query_responses_full.to_csv(output_dir + os.sep + "query_results_full.csv", index=False, float_format='%.4f')
            query_responses_avg.to_csv(output_dir + os.sep + "query_results_avg.csv", index=False, float_format='%.4f')

        # Get the question-answer results of the evaluation dataset
        print("Generating QA metrics for {}".format(query_model_name))
        qa_eval_dict = get_qa_results(patient_record_nodes, query_engine, query_model_name)
        qa_results.loc[len(qa_results)] = qa_eval_dict

        # Save the results to csv
        qa_results.to_csv(output_dir + os.sep + "qa_results.csv", index=False, float_format='%.4f')


def main(argv):
    # Get output directory from command line argument
    if len(argv) != 3:
        print("ERROR! Please provide an output directory as the first argument"
              " and a patient id as the second argument.")
        sys.exit(-1)
    output_directory = argv[1]
    patient_id = argv[2]

    # Load environment variables
    load_dotenv()

    # Get the query questions
    query_questions = return_query_set()

    # Run the evaluation
    start_time = int(round(time.time()))
    evaluate_model_pairs(patient_id, query_questions, output_directory)
    end_time = int(round(time.time()))
    print("\n\nFinished all evaluations for patient id {}! Took {} seconds."
          "\nSaved results in {}".format(patient_id, end_time - start_time, output_directory))


if __name__ == "__main__":
    main(sys.argv)
