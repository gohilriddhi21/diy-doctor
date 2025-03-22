from src.node_manager import NodeManager


def main():
    pdf_path = "WebMD.pdf"
    node_manager = NodeManager(pdf_path)
    print(node_manager.get_nodes()[-4])


if __name__ == "__main__":
    main()
