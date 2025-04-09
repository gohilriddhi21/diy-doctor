# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# query_engine_mistral.py - Child class to use mistral-7b-instruct model as query engine

from src.models.query_engines.query_engine_base_class.query_engine_base import QueryEngine
from llama_index.core import Settings
from llama_index.llms.openrouter import OpenRouter
import os


class QueryEngineMistral(QueryEngine):
    """
    Usable query engine with the mistralai/mistral-7b-instruct LLM model
    """
    def __init__(self, nodes=None, embed_model_name="sentence-transformers/all-MiniLM-L6-v2"):
        # Load LLM and put in Settings
        self._model_name = "mistralai/mistral-7b-instruct"
        self._llm = self.load_llm()

        # Instantiate super class
        super().__init__(nodes=nodes, llm=self._llm, embed_model_name=embed_model_name)

    def load_llm(self):
        """
        Loads an LLM
        :return: The llm being used by the query engine after loading
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenRouter API key. "
                             "Set the 'OPENROUTER_API_KEY' environment variable in your \'.env\' file.")
        llm = OpenRouter(api_key=api_key, model=self._model_name, max_tokens=512, context_window=4096)
        return llm

    def get_llm(self):
        """
        Returns the LLM being used by the Query Engine
        :return: Current LLM model
        """
        return self._llm
