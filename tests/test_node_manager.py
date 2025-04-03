import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.service.node_manager import NodeManager

def main():
    pdf_path = "tests/WebMD.pdf"
    node_manager = NodeManager(pdf_path)
    print(node_manager.get_nodes()[-4])

if __name__ == "__main__":
    main()
