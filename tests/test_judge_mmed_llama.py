import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.service.node_manager import NodeManager
from src.models.query_engines.usable_query_engines.query_engine_mistral import QueryEngineMistral
from dotenv import load_dotenv
from src.models.judge_models.usable_judge_classes.judge_MetaLlama import JudgeMetaLlama


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
    node_manager = NodeManager(pdf_path)
    query_engine = QueryEngineMistral(node_manager.get_nodes())
    judge_llm_manager = JudgeMetaLlama()
    query_1 = "What treatments could be effective for somebody with a migraine?"
    query_2 = "Who is \"BEING MY OWN ADVOCATE\" by?"
    test_success(query_engine, judge_llm_manager, query_1)
    test_success(query_engine, judge_llm_manager, query_2)


if __name__ == "__main__":
    main()
