# Riddhi Gohil
# CS 7180 - Generative AI
# gohil.r@northeastern.edu
# judge_MMedLlama.py - Judge using the MMed-Llama 3 Free model

import sys
import os
from abc import ABC
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models.judge_models.judge_base_class.judge_llm_base import JudgeLLMBase
from dotenv import load_dotenv
import os
from llama_index.llms.openrouter import OpenRouter
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator


class JudgeMMedLlama(JudgeLLMBase, ABC):
    """
    Child class to use the MMed-Llama 3 model as a judge LLM
    """
    def __init__(self, model_name="meta-llama/llama-3.2-3b-instruct:free", max_tokens=512, context_window=4096):
        super().__init__(model_name, max_tokens, context_window)
        self.initialize_judge_llm()

    def initialize_judge_llm(self):
        """
        Initializes the judge LLM
        :return: None
        """
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenRouter API key. "
                             "Set the 'OPENROUTER_API_KEY' environment variable in your '.env' file.")
        
        self.judge_llm = OpenRouter(api_key=api_key, 
                                   model=self.model_name,
                                   max_tokens=self.max_tokens,
                                   context_window=self.context_window
                                   )

    def evaluate_faithfulness(self, response_obj):
        """
        Evaluates how faithful a response to a query was
        :param response_obj: The full response object to evaluate
        :return: The faithfulness score
        """
        # Set up evaluator
        faithfulness_evaluator = FaithfulnessEvaluator(llm=self.judge_llm)

        # Evaluate for faithfulness score
        faithfulness_score = faithfulness_evaluator.evaluate_response(response=response_obj)
        return faithfulness_score.score

    def evaluate_relevancy(self, query, response_obj):
        """
        Evaluates how relevant a response to a query was
        :param query:        The original query used to generate the response
        :param response_obj: The full response object to evaluate
        :return: The relevancy score
        """
        # Set up evaluator
        relevancy_evaluator = RelevancyEvaluator(llm=self.judge_llm)

        # Evaluate for relevancy score
        relevancy_score = relevancy_evaluator.evaluate_response(query=query, response=response_obj)
        return relevancy_score.score

    def verify_suggestions(self, query, response_obj, verbose=False):
        """
        Verifies the faithfulness/relevancy of a response and provides a level of certainty
        :param query:        The original query used to generate a response
        :param response_obj: The response to the query
        :param verbose:      Whether to print scores or not
        :return: The verification level of the query
        """
        faithfulness = self.evaluate_faithfulness(response_obj)
        relevancy = self.evaluate_relevancy(query, response_obj)
        return self._verification_response(faithfulness, relevancy, verbose)