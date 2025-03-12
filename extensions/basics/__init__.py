import json


def upper_case(text: str, **kwargs) -> str:
    return text.upper()


def lower_case(text: str, **kwargs) -> str:
    return text.lower()


def pretty_json(text: str, **kwargs) -> str:
    return json.dumps(json.loads(text), indent=4)
