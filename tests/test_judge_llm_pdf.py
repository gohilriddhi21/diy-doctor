import os
import sys
from src.service.node_manager import NodeManager
from dotenv import load_dotenv
from src.models.query_engine import QueryEngine
from src.models.judge_llm import JudgeLLM


def test_success(query_engine, judge_llm_manager, query):
    response_text = query_engine.generate_response(query)
    full_response = query_engine.generate_full_response(query)
    print(query)
    print(response_text)
    verification = judge_llm_manager.verify_suggestions(query, full_response, verbose=True)
    print("Verification: {}".format(verification))
    print()


def main():
    load_dotenv()
    pdf_path = "tests/WebMD.pdf"
    node_manager = NodeManager()
    node_manager.set_nodes_from_pdf(pdf_path)
    nodes = node_manager.get_nodes()
    query_model = "mistralai/mistral-7b-instruct"
    judge_model = "qwen/qwen-turbo"
    query_engine = QueryEngine(query_model, nodes)
    judge_llm_manager = JudgeLLM(judge_model)
    query_1 = "What treatments could be effective for somebody with a migraine?"
    query_2 = "Who is \"BEING MY OWN ADVOCATE\" by?"
    test_success(query_engine, judge_llm_manager, query_1)
    test_success(query_engine, judge_llm_manager, query_2)


if __name__ == "__main__":
    main()
