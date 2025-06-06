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
    def __init__(self, embed_model_name="sentence-transformers/all-MiniLM-L6-v2"):
        # Initialize the embedding model
        self._embed_model = HuggingFaceEmbedding(model_name=embed_model_name)

        # Set the ingestion pipeline and nodes
        self._pipeline = self._set_ingestion_pipeline()

        # Create storage for documents and nodes
        self._documents = None
        self._nodes = None

    def __len__(self):
        """
        :return: The number of nodes managed by the object
        """
        return len(self._nodes)

    def clear_nodes(self):
        """
        Sets all documents and nodes to None to clear documents
        :return: None
        """
        self._nodes = None

    def set_nodes_from_patient_data(self, patient_records):
        """
        Sets nodes from a list of patient records
        :param patient_records: Patient record data in form of list[dict{}, dict{}, ...]
        :return: None
        """
        # Start message
        start_time = int(round(time.time()))
        print("Processing document data from patient records... ")

        self._documents = self._process_records_document_data(patient_records)
        self._nodes = self._pipeline.run(documents=self._documents)

        # Completion message
        end_time = int(round(time.time()))
        print("Finished! Extracted {} nodes in {} seconds.\n".format(len(self._nodes), end_time - start_time))

    def get_nodes(self):
        """
        :return: The nodes managed by the object gracefully
        """
        return self._nodes

    def get_documents(self):
        """
        :return: The documents managed by the object gracefully
        """
        return self._documents

    def _process_records_document_data(self, patient_records):
        """
        Processes a patient record list of dictionaries into a set of documents
        :param patient_records: The patient records object
        :return: None if patient records were None, else the processed set of Documents to extract info from
        """
        if patient_records is None:
            return None
        else:
            documents = []
            for record in patient_records:
                record_string = self._process_record_to_text(record)
                documents.append(Document(text=record_string))
            return documents

    def _process_record_to_text(self, record):
        """
        Process data from record dictionary into a single String to extract information from
        :param record: The record dictionary to process into a text String (assumes non-empty)
        :return: The processed record as a String
        """
        record_string = ""
        for key in record:
            record_string += "{}: {} ".format(key, record[key]).replace("_", " ").lower()
        return record_string

    def _process_pdf_document_data(self, document_path):
        """
        Processes the document data within the NodeManager
        :return: A full set of documents
        """
        base_documents = SimpleDirectoryReader(input_files=[document_path]).load_data()
        document_from_tables = self._get_table_documents(document_path)

        # Return only base documents if no documents from tables were found, otherwise return both
        if document_from_tables is None:
            return base_documents
        else:
            return base_documents + [document_from_tables]  # TODO should OSR also be included?

    def _get_table_documents(self, document_path):
        """
        Extracts documents from table data in the document passed in
        :return: A single document containing the table data contained in a document
        """
        # Read PDF
        tables = tabula.read_pdf(document_path, pages="all")

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
        pipeline = IngestionPipeline(transformations=[
            SemanticSplitterNodeParser(buffer_size=1, embed_model=self._embed_model,
                                       breakpoint_percentile_threshold=breakpoint_percentile_threshold),
            self._embed_model])
        return pipeline
