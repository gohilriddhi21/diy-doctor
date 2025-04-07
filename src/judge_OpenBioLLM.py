# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# judge_OpenBioLLM.py - Judge using the OpenBioLLM 8B parameter model


from abc import ABC
from judge_llm_base import JudgeLLMBase
from dotenv import load_dotenv
import os
from llama_index.llms.openrouter import OpenRouter
from llama_index.llms.huggingface import HuggingFaceInferenceAPI, HuggingFaceLLM
from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator


class JudgeOpenBioLLM(JudgeLLMBase, ABC):
    """
    Child class to use the judge LLM with
    """
    def __init__(self, model_name="aaditya/Llama3-OpenBioLLM-8B", max_tokens=512, context_window=4096):
        super().__init__(model_name, max_tokens, context_window)
        self.initialize_judge_llm()

    def initialize_judge_llm(self):
        """
        Initializes the judge LLM
        :return: None
        """
        # Note downloading the model the first time may take a few minutes
        # TODO might need to quantize, use GPU, lower max tokens, etc. because currently slow
        self.judge_llm = HuggingFaceLLM(model_name=self.model_name,
                                        tokenizer_name=self.model_name,
                                        max_new_tokens=self.max_tokens,
                                        context_window=self.context_window)

    def evaluate_faithfulness(self, response_obj):
        """
        Evaluates how faithful a response to a query was
        :param response_obj: The full response object to evaluate
        :return: The faithfulness score
        """
        # Set up evaluators
        faithfulness_evaluator = FaithfulnessEvaluator(llm=self.judge_llm)

        # Evaluate for each score
        faithfulness_score = faithfulness_evaluator.evaluate_response(response=response_obj)
        return faithfulness_score.score

    def evaluate_relevancy(self, query, response_obj):
        """
        Evaluates how faithful a response to a query was
        :param query:        The original query used to generate the response
        :param response_obj: The full response object to evaluate
        :return: The relevancy score
        """
        # Set up evaluators
        relevancy_evaluator = RelevancyEvaluator(llm=self.judge_llm)

        # Evaluate for each score
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
