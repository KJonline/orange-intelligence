try:
    from extensions.ollama.example import improve_grammar, make_it_polite, translate_to_english  # noqa: F401
except ImportError:
    # Define placeholder functions if dependencies are missing
    def improve_grammar(text: str, **kwargs) -> str:
        return "Error: Ollama module not available. Please install with: pip install ollama"
    
    def make_it_polite(text: str, **kwargs) -> str:
        return "Error: Ollama module not available. Please install with: pip install ollama"
    
    def translate_to_english(text: str, **kwargs) -> str:
        return "Error: Ollama module not available. Please install with: pip install ollama"
