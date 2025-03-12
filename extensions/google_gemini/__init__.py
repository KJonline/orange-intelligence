from extensions.google_gemini.utils import _chat_completion_endpoint


def make_a_joke(text: str, **kwargs) -> str:
    prompt = f"Tell me a joke about {text}"

    return _chat_completion_endpoint(prompt)


def translate_to_english(input_text: str, **kwargs) -> str:
    prompt = (
        "Translate this sentence to English. Return only the translated sentence, do not add anything else. "
        + input_text
    )
    return _chat_completion_endpoint(prompt)

def make_it_polite(input_text: str, **kwargs) -> str:
    prompt = (
        "Convert this sentence to a polite one. Return only the converted sentence, do not add anything else. "
        + input_text
    )
    return _chat_completion_endpoint(prompt)

def proofread(input_text: str, **kwargs) -> str:
    prompt = (
        "Spellcheck this sentence and fix any spelling or grammar errors. Return only the improved sentence, do not add anything else. "
        + input_text
    )
    return _chat_completion_endpoint(prompt)

def custom_prompt(input_text: str, **kwargs) -> str:
    """Process a custom user prompt directly.
    
    Args:
        input_text: The custom prompt text entered by the user
        kwargs: Additional arguments including is_custom_prompt flag
        
    Returns:
        The response from the Google Gemini API
    """
    user_prompt = kwargs.get("prompt_text", "") + ": " + input_text 

    context = f"""
    I need you to return me a single answer for this next action. You cannot give me choice just a single answer.
    Action:
    {user_prompt}
    """

    # Simply pass the text directly to the chat completion endpoint
    return _chat_completion_endpoint(context)