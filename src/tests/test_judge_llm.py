from src.node_manager import NodeManager
from src.llm_model import QueryEngine
from dotenv import load_dotenv
from src.judge_qwen import JudgeQwen
from src.judge_OpenBioLLM import JudgeOpenBioLLM


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
    pdf_path = "WebMD.pdf"
    node_manager = NodeManager(pdf_path)
    query_engine = QueryEngine(node_manager.get_nodes())
    judge_llm_manager = JudgeOpenBioLLM()
    query_1 = "What treatments could be effective for somebody with a migraine?"
    query_2 = "Who is \"BEING MY OWN ADVOCATE\" by?"
    test_success(query_engine, judge_llm_manager, query_1)
    test_success(query_engine, judge_llm_manager, query_2)


if __name__ == "__main__":
    main()
