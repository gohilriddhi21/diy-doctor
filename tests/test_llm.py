import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.service.node_manager import NodeManager
from src.models.query_engines.query_engine_base_class.llm_model import QueryEngine
from dotenv import load_dotenv


def main():
    load_dotenv()
    pdf_path = "tests/WebMD.pdf"
    node_manager = NodeManager()
    node_manager.set_nodes_from_pdf(pdf_path)
    nodes = node_manager.get_nodes()
    query_engine = QueryEngine(nodes)
    query = "What treatments could be effective for somebody with a migraine?"
    print(query_engine.generate_response(query))


if __name__ == "__main__":
    main()
