# David Treadwell
# CS 7180 - Generative AI
# treadwell.d@northeastern.edu
# model_loading_function.py - Function to properly load (pre-defined) LLM models for use throughout project


import os
from llama_index.llms.openrouter import OpenRouter
from llama_index.llms.llama_cpp import LlamaCPP

# Set model names
MODEL_NAMES = [
    "aaditya/Llama3-OpenBioLLM-8B",
    "Henrychur/MMed-Llama-3-8B",
    "meta-llama/llama-3.2-3b-instruct",
    "mistralai/mistral-7b-instruct",
    "qwen/qwen-turbo",
    "bigcode/starcoder2-7b"
]

# Set model access indexes
OPENBIO_INDEX = 0
MMED_LLAMA_INDEX = 1
META_LLAMA_INDEX = 2
MISTRAL_INDEX = 3
QWEN_INDEX = 4
STARCODER2_INDEX = 5

def load_llm(model_name, max_tokens=512, context_window=4096):
    """
    Loads a model from the model name
    :param model_name:     The name of the model to load. Note that it must be in the defined "models->router" dictionary
    :param max_tokens:     The maximum number of tokens the model can generate in response
    :param context_window: Size of the context the model can pull from
    :return: A loaded LLM object
    """
    # Valid load cases
    if model_name == MODEL_NAMES[OPENBIO_INDEX]:
        return _load_hugging_face_model(model_name=os.path.join("gguf_models", "openbiollm-llama3-8b.Q8_0.gguf"),
                                        max_tokens=max_tokens, context_window=context_window)

    elif model_name == MODEL_NAMES[MMED_LLAMA_INDEX]:
        return _load_hugging_face_model(model_name=os.path.join("gguf_models", "mmed-llama-3-8b-q4_k_m.gguf"),
                                        max_tokens=max_tokens, context_window=context_window)

    elif model_name == MODEL_NAMES[META_LLAMA_INDEX]:
        return _load_openrouter_model(model_name, max_tokens=max_tokens, context_window=context_window)

    elif model_name == MODEL_NAMES[MISTRAL_INDEX]:
        return _load_openrouter_model(model_name, max_tokens=max_tokens, context_window=context_window)

    elif model_name == MODEL_NAMES[QWEN_INDEX]:
        return _load_openrouter_model(model_name, max_tokens=max_tokens, context_window=context_window)

    elif model_name == MODEL_NAMES[STARCODER2_INDEX]:
        return _load_hugging_face_model(model_name=os.path.join("gguf_models", "bigcode.starcoder2-7b.Q8_0.gguf"),
                                        max_tokens=max_tokens, context_window=context_window)
     
    # Error case where model name is invalid
    else:
        print("ERROR! Invalid model name. Please select a valid name from the list of pre-defined models")
        print("{}\n".format(model for model in MODEL_NAMES))


def _load_openrouter_model(model_name, max_tokens, context_window):
    """
    Loads an LLM via OpenRouter API
    :param model_name:     The model name
    :param max_tokens:     The maximum number of tokens the model can generate in response
    :param context_window: Size of the context the model can pull from
    :return: Loaded LLM
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Missing OpenRouter API key. "
                         "Set the 'OPENROUTER_API_KEY' environment variable in your \'.env\' file.")
    llm = OpenRouter(api_key=api_key,
                     model=model_name,
                     max_tokens=max_tokens,
                     context_window=context_window)
    return llm


def _load_hugging_face_model(model_name, max_tokens, context_window):
    """
    Loads an LLM via Llama Index Hugging Face API
    :param model_name:     The model name
    :param max_tokens:     The maximum number of tokens the model can generate in response
    :param context_window: Size of the context the model can pull from
    :return: Loaded LLM
    """
    llm = LlamaCPP(
        model_path=model_name,
        max_new_tokens=max_tokens,
        context_window=context_window,
    )
    return llm
