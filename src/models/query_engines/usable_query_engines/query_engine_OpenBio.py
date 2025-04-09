# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# query_engine_OpenBio.py - Child class to use aaditya/Llama3-OpenBioLLM-8B model as query engine

from src.models.query_engines.query_engine_base_class.query_engine_base import QueryEngineBase
from llama_index.llms.huggingface import HuggingFaceLLM


class QueryEngineOpenBio(QueryEngineBase):
    """
    Usable query engine with the aaditya/Llama3-OpenBioLLM-8B LLM model
    """
    def __init__(self, nodes=None, embed_model_name="sentence-transformers/all-MiniLM-L6-v2"):
        # Load LLM and put in Settings
        self._model_name = "aaditya/Llama3-OpenBioLLM-8B"
        self._llm = self.load_llm()

        # Instantiate super class
        super().__init__(nodes=nodes, llm=self._llm, embed_model_name=embed_model_name)

    def load_llm(self):
        """
        Loads an LLM
        :return: The llm being used by the query engine after loading
        """
        llm = HuggingFaceLLM(model_name=self._model_name,
                             tokenizer_name=self._model_name,
                             max_new_tokens=512,
                             context_window=4096)
        return llm

    def get_llm(self):
        """
        Returns the LLM being used by the Query Engine
        :return: Current LLM model
        """
        return self._llm
