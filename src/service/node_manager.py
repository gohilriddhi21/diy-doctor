# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# node_manager.py - Contains a class to manage nodes representing a document

import time
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import tabula
from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SemanticSplitterNodeParser


class NodeManager:
    """
    Class to manage a document and generate nodes based on the document. Meant for use with a single document
    """
    def __init__(self, document_path, embed_model_name="sentence-transformers/all-MiniLM-L6-v2"):
        # Start message at initialization
        start_time = int(round(time.time()))
        print("Processing document data... ")

        # create a set of documents based on the model path passed in
        self._document_path = document_path
        self._all_documents = self._process_document_data()

        # Initialize the embedding model
        self._embed_model = HuggingFaceEmbedding(model_name=embed_model_name)

        # Set the ingestion pipeline and nodes
        self._pipeline = None
        self._nodes = self._set_ingestion_pipeline()

        # Completion message after initialized
        end_time = int(round(time.time()))
        print("Finished! Extracted {} nodes in {} seconds.\n".format(len(self._nodes), end_time - start_time))

    def __len__(self):
        """
        :return: The number of nodes managed by the object
        """
        return len(self._nodes)

    def get_nodes(self):
        """
        :return: The nodes managed by the object gracefully
        """
        return self._nodes

    def _process_document_data(self):
        """
        Processes the document data within the NodeManager
        :return: A full set of documents
        """
        base_documents = SimpleDirectoryReader(input_files=[self._document_path]).load_data()
        document_from_tables = self._get_table_documents()

        # Return only base documents if no documents from tables were found, otherwise return both
        if document_from_tables is None:
            return base_documents
        else:
            return base_documents + [document_from_tables]  # TODO should OSR also be included?

    def _get_table_documents(self):
        """
        Extracts documents from table data in the document passed in
        :return: A single document containing the table data contained in a document
        """
        # Read PDF
        tables = tabula.read_pdf(self._document_path, pages="all")

        # If no tables are found, return None directly
        if tables is None:
            return None

        # If tables are found, extract documents from them and return them
        else:
            table_docs = [df.to_markdown(index=False) for df in tables]
            all_tables_text = "\n\n".join(table_docs)
            document_from_tables = Document(text=all_tables_text)
            return document_from_tables

    def _set_ingestion_pipeline(self, breakpoint_percentile_threshold=85):
        """
        Sets the ingestion pipeline for documents
        :param breakpoint_percentile_threshold: The percentage of dissimilarity that must be exceeded to
        create a new chunk
        :return: The nodes to use in RAG system
        """
        self._pipeline = IngestionPipeline(transformations=[
            SemanticSplitterNodeParser(buffer_size=1, embed_model=self._embed_model,
                                       breakpoint_percentile_threshold=breakpoint_percentile_threshold),
            self._embed_model])
        nodes = self._pipeline.run(documents=self._all_documents)
        return nodes
