from extensions.openai.utils import _chat_completion_endpoint


def make_a_joke(text: str, **kwargs) -> str:
    prompt = f"Tell me a joke about {text}"

    return _chat_completion_endpoint(prompt)

def custom_prompt(text: str, **kwargs) -> str:
    """Process a custom user prompt directly.
    
    Args:
        text: The custom prompt text entered by the user
        kwargs: Additional arguments including is_custom_prompt flag
        
    Returns:
        The response from the OpenAI API
    """
    # Simply pass the text directly to the chat completion endpoint
    return _chat_completion_endpoint(text)
