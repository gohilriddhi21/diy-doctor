# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# query_engine_mistral.py - Child class to use mistral-7b-instruct model as query engine

from llama_index.core import Settings
from llama_index.llms.openrouter import OpenRouter
import os


class QueryEngineMistral:
    def __init__(self, embed_model_name="sentence-transformers/all-MiniLM-L6-v2"):
        # Instantiate super class
        super().__init__(embed_model_name)

        # Load LLM and put in Settings
        self._model_name = "mistralai/mistral-7b-instruct"
        self._llm = self.load_llm()

    def load_llm(self):
        """
        Loads an LLM
        :return: The llm being used by the query engine after loading
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenRouter API key. "
                             "Set the 'OPENROUTER_API_KEY' environment variable in your \'.env\' file.")
        llm = OpenRouter(api_key=api_key, model=self._model_name , max_tokens=512, context_window=4096)
        Settings.llm = self._llm
        return llm

    def get_llm(self):
        """
        Returns the LLM being used by the Query Engine
        :return: Current LLM model
        """
        return self._llm
