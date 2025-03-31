# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# llm_model.py - Contains a class to manage querying with a base model

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.retrievers.bm25 import BM25Retriever
import Stemmer
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openrouter import OpenRouter
import os


class QueryEngine:
    """
    Class to manage base queries and responses
    """
    def __init__(self, nodes=None, embed_model_name="sentence-transformers/all-MiniLM-L6-v2"):
        # Set defaults for variables necessary to generate retrievals
        # Set index and nodes
        self._nodes = nodes
        self._index = None

        # Set retrievers
        self._base_retriever = None
        self._auto_merging_retriever = None
        self._bm25_retriever = None
        self._fusion_retriever = None

        # Set the default engine
        self._query_engine = None
        self._default_retriever = "fusion"

        # Set embedding model
        self._embed_model = HuggingFaceEmbedding(model_name=embed_model_name)

        # Set LLM
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenRouter API key. "
                             "Set the 'OPENROUTER_API_KEY' environment variable in your \'.env\' file.")
        self._llm = OpenRouter(api_key=api_key, model="mistralai/mistral-7b-instruct", max_tokens=512, context_window=4096)

        # Put embedding model and LLM in settings
        # TODO really would rather parameterize this somewhere, but for now this works
        Settings.embed_model = self._embed_model
        Settings.llm = self._llm

        # Set message for when queries/settings are attempted without nodes
        self._no_nodes_message = "Nodes are not yet initialized. " \
                                 "Initialize nodes via constructor or \"set_query_nodes\" method"

        # If nodes were passed in, set the inner variables and retrievers
        if nodes is not None:
            self.set_nodes_and_retrievers(nodes)
            self.update_query_engine(self._default_retriever)

    def generate_response(self, query):
        """
        Generates a response to a query without additional information
        :param query: The query to use in querying the engine
        :return: The query response as a String, or a message that no query was passed
        """
        response = self.generate_full_response(query)
        if query:
            response = response.response  # Extracts just the text response if a query was returned
        return response

    def generate_full_response(self, query):
        """
        Generates a response to a query with all additional information provided by engine
        :param query: The query to use in querying the engine
        :return: The query response object
        """
        if query:
            response_obj = self._query_engine.query(query)
        else:
            response_obj = "No query provided! Please enter a query and try again."
        return response_obj

    def set_nodes_and_retrievers(self, nodes):
        """
        Sets the nodes and retrievers managed by the query engine
        :param nodes: The nodes to use as context
        :return: None
        """
        self._nodes = nodes
        self._index = VectorStoreIndex(nodes)
        self._query_engine = self._index.as_query_engine()
        self._set_retrievers()

    def update_query_engine(self, retriever):  # TODO could improve how engine selected
        """
        Sets which query engine is the default for queries
        :param retriever: The name of the retriever to use in the engine
        :return: None
        """
        if retriever == "base":
            self._query_engine = RetrieverQueryEngine.from_args(self._base_retriever)
        elif retriever == "auto_merging":
            self._query_engine = RetrieverQueryEngine.from_args(self._auto_merging_retriever)
        elif retriever == "bm25":
            self._query_engine = RetrieverQueryEngine.from_args(self._bm25_retriever)
        elif retriever == "fusion":
            self._query_engine = RetrieverQueryEngine.from_args(self._fusion_retriever)
        else:
            print("ERROR! Invalid retriever name. Only pass in a retriever name from the list below:\n"
                  "base\n"
                  "auto_merging\n"
                  "bm25\n"
                  "fusion\n")

    def get_llm(self):
        """
        Returns the LLM being used by the Query Engine
        :return: LLM model
        """
        return self._llm

    def _set_retrievers(self):
        """
        Sets all retrievers if nodes are passed in
        :return: None
        """
        if self._nodes is not None:
            self._set_base_retriever()
            self._set_auto_merging_retriever()
            self._set_bm25_retriever()
            self._set_fusion_retriever()
        else:
            print(self._no_nodes_message)

    def _set_base_retriever(self, similarity_top_k=1):
        """
        Creates a base retriever object
        :param similarity_top_k: Top k chunks to use as context
        :return: None
        """
        self._base_retriever = self._index.as_retriever(similarity_top_k=similarity_top_k)

    def _set_auto_merging_retriever(self, similarity_top_k=3):
        """
        Creates an auto merging retriever object
        :param similarity_top_k: Top k chunks to use as context
        :return: None
        """
        auto_base_retriever = self._index.as_retriever(similarity_top_k=similarity_top_k)
        self._auto_merging_retriever = AutoMergingRetriever(auto_base_retriever, self._index.storage_context)

    def _set_bm25_retriever(self, similarity_top_k=2, language="english"):
        """
        Creates a bm25 retriever object
        :param similarity_top_k: Top k chunks to use as context
        :param language: language of the nodes being parsed
        :return: None
        """
        self._bm25_retriever = BM25Retriever.from_defaults(nodes=self._nodes, similarity_top_k=similarity_top_k,
                                                           stemmer=Stemmer.Stemmer(language), language=language)

    def _set_fusion_retriever(self, similarity_top_k=7, num_queries=1, vector_weight=0.4, lexical_weight=0.6):
        """
        Creates a fusion retriever based on a vector-based (AutoMerging Retriever) and lexical-based (BM25 Retriever) retrievers
        The weights for vector and lexical methods should add up to 1.0
        :param similarity_top_k: The top k values to consider
        :param num_queries:      Number of queries for the fusion retriever to use.
            Defaults to 1 so original query is the only one used. If num_queries > 1,
            then additional queries will be generated
        :param vector_weight:    The amount of weight to give to the vector retriever's retrieval scores
        :param lexical_weight:   The amount of weight to give to the vector retriever's retrieval scores
        :return: None
        """
        # Get a new AutoMerging Retriever and BM25 retriever
        fusion_auto_base = self._index.as_retriever(similarity_top_k=similarity_top_k)
        fusion_vector_retriever = AutoMergingRetriever(fusion_auto_base, self._index.storage_context)
        fusion_lexical_retriever = BM25Retriever.from_defaults(nodes=self._nodes,
                                                               similarity_top_k=similarity_top_k,
                                                               stemmer=Stemmer.Stemmer('english'),
                                                               language='english')

        # Create the fusion retriever
        self._fusion_retriever = QueryFusionRetriever(
            retrievers=[fusion_vector_retriever, fusion_lexical_retriever],
            similarity_top_k=similarity_top_k,
            num_queries=num_queries,
            retriever_weights=[vector_weight, lexical_weight]
        )