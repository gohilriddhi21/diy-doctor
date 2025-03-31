# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# judge_default.py - Default judge LLM based on RAG from assignment 4 of CS 7180 course


from abc import ABC
from src.judge_llm_base import JudgeLLMBase
from dotenv import load_dotenv
import os
from llama_index.llms.openrouter import OpenRouter


class JudgeDefault(JudgeLLMBase, ABC):
    """
    Child class to use the judge LLM with
    """
    def __init__(self, model_name="qwen/qwen-turbo", max_tokens=512, context_window=4096):
        super().__init__(model_name, max_tokens, context_window)
        self.initialize_judge_llm()

    def initialize_judge_llm(self):
        """
        Initializes the judge LLM
        :return: None
        """
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        self.judge_llm = OpenRouter(api_key=api_key, model=self.model_name,
                                    max_tokens=self.max_tokens,
                                    context_window=self.context_window)
