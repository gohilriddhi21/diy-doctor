from src.models.model_loading_function import load_llm
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator


class JudgeLLM:
    """
    Class to provide shared functionality to child judge LLM classes that provide specific implementations
    """
    def __init__(self, model_name):
        self.judge_llm = load_llm(model_name)

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
