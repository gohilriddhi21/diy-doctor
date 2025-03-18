from judge_llm import verify_suggestions

def generate_response(query):
    if query:
        verify_suggestions("test response")
    return None