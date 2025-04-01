from src.node_manager import NodeManager
from src.llm_model import QueryEngine
from dotenv import load_dotenv
from src.judge_default import JudgeDefault
from src.judge_OpenBioLLM import JudgeOpenBioLLM


def test_success(query_engine, judge_llm_manager, query):
    response_text = query_engine.generate_response(query)
    judge_llm = judge_llm_manager.judge_llm
    full_response = query_engine.generate_full_response(query)
    faithfulness_score = judge_llm_manager.evaluate_faithfulness(full_response)
    relevancy_score = judge_llm_manager.evaluate_relevancy(query, full_response)
    verification = judge_llm_manager.verify_suggestions(query, full_response)
    print(response_text)
    print("Faithfulness: {}".format(faithfulness_score))
    print("Relevancy: {}".format(relevancy_score))
    print("Verification: {}".format(verification))
    print()


def main():
    load_dotenv()
    pdf_path = "WebMD.pdf"
    node_manager = NodeManager(pdf_path)
    query_engine = QueryEngine(node_manager.get_nodes())
    judge_llm_manager = JudgeDefault()
    query_1 = "What treatments could be effective for somebody with a migraine?"
    query_2 = "Who is \"BEING MY OWN ADVOCATE\" by?"
    test_success(query_engine, judge_llm_manager, query_1)
    test_success(query_engine, judge_llm_manager, query_2)


if __name__ == "__main__":
    main()
