# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# judge_llm_base.py - Contains a class to manage shared functionality for judge LLM classes


from abc import ABC, abstractmethod
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator


class JudgeLLMBase(ABC):
    """
    Parent class to provide shared functionality to child judge LLM classes that provide specific implementations
    """
    def __init__(self, model_name, max_tokens, context_window):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.context_window = context_window
        self.judge_llm = None

    @abstractmethod
    def initialize_judge_llm(self):
        pass

    def evaluate_faitfulness(self, judge_llm, response_obj):
        """
        Evaluates how faithful a response to a query was
        :param judge_llm:    The LLM to use to evaluate faithfulness
        :param response_obj: The full response object to evaluate
        :return: The faithfulness score
        """
        # Set up evaluators
        faithfulness_evaluator = FaithfulnessEvaluator(llm=judge_llm)

        # Evaluate for each score
        faithfulness_score = faithfulness_evaluator.evaluate_response(response=response_obj)
        return faithfulness_score.score

    def evaluate_relevancy(self, judge_llm, query, response_obj):
        """
        Evaluates how faithful a response to a query was
        :param judge_llm:    The LLM to use to evaluate relevancy
        :param query:        The original query used to generate the response
        :param response_obj: The full response object to evaluate
        :return: The relevancy score
        """
        # Set up evaluators
        relevancy_evaluator = RelevancyEvaluator(llm=judge_llm)

        # Evaluate for each score
        relevancy_score = relevancy_evaluator.evaluate_response(query=query, response=response_obj)
        return relevancy_score.score

    def verify_suggestions(self, judge_llm, query, response_obj):
        """
        Evaluates how faithful a response to a query was
        :param judge_llm:    The LLM to use to evaluate relevancy
        :param query:        The original query used to generate the response
        :param response_obj: The full response object to evaluate
        :return: The relevancy score
        """
        # Get the evaluation scores
        faithfulness = self.evaluate_faitfulness(judge_llm, response_obj)
        relevancy = self.evaluate_relevancy(judge_llm, query, response_obj)
        full_score = faithfulness + relevancy

        # Return context of success
        # TODO should the score be handled elsewhere
        if full_score == 2.0:
            return "GOOD"
        elif full_score == 1.0:
            return "VERIFY"
        elif full_score == 0.0:
            return "BAD"
        else:
            return "ERROR"
