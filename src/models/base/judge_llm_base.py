# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# judge_llm_base.py - Contains a class to manage shared functionality for judge LLM classes


from abc import ABC, abstractmethod


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

    @abstractmethod
    def evaluate_faithfulness(self, response_obj):
        """
        Evaluates how faithful a response to a query was
        :param response_obj: The full response object to evaluate
        :return: The faithfulness score
        """
        pass

    @abstractmethod
    def evaluate_relevancy(self, query, response_obj):
        """
        Evaluates how faithful a response to a query was
        :param query:        The original query used to generate the response
        :param response_obj: The full response object to evaluate
        :return: The relevancy score
        """
        pass

    def verify_suggestions(self, query, response_obj):
        """
        Verifies the faithfulness/relevancy of a response and provides a level of certainty
        :param query:        The original query used to generate a response
        :param response_obj: The response to the query
        :return: The verification level of the query
        """
        pass

    def _print_verbose_scores(self, faithfulness_score, relevancy_score):
        """
        Prints faithfulness and relevancy scores
        :param faithfulness_score: The faithfulness score
        :param relevancy_score:    The relevancy score
        :return: None
        """
        print("Faithfulness: {}".format(faithfulness_score))
        print("Relevancy: {}".format(relevancy_score))

    def _verification_response(self, faithfulness_score, relevancy_score, verbose=False):
        """
        Returns a response depending on the faithfulness/relevancy of a response
        :param faithfulness_score: The faithfulness score (0.0 or 1.0)
        :param relevancy_score:    The relevancy score (0.0 or 1.0)
        :param verbose:            Whether to print scores or not
        :return: The verification level of the response
        """
        # Get the evaluation scores
        full_score = faithfulness_score + relevancy_score

        # Prints if verbose
        if verbose:
            self._print_verbose_scores(faithfulness_score, relevancy_score)

        # Return context of success
        # TODO should the score be handled elsewhere?
        if full_score == 2.0:
            return "GOOD"
        elif full_score == 1.0:
            return "VERIFY"
        elif full_score == 0.0:
            return "BAD"
        else:
            return "ERROR"
