import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.service.node_manager import NodeManager
from src.models.llm_model import QueryEngine
from dotenv import load_dotenv


def main():
    load_dotenv()
    pdf_path = "tests/WebMD.pdf"
    node_manager = NodeManager(pdf_path)
    query_engine = QueryEngine(node_manager.get_nodes())
    query = "What treatments could be effective for somebody with a migraine?"
    print(query_engine.generate_response(query))


if __name__ == "__main__":
    main()
