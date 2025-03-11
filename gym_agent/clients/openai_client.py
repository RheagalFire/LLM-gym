from openai import OpenAI
from gym_agent.settings import get_settings

settings = get_settings()
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_completion(
    prompt: str,
    model: str = settings.DEFAULT_MODEL,
    temperature: float = settings.DEFAULT_TEMPERATURE,
    max_tokens: int = settings.DEFAULT_MAX_TOKENS,
    system_message: str = "You are a helpful assistant.",
):
    """
    Get a completion from the OpenAI API.

    Args:
        prompt: The prompt to send to the API
        model: The model to use
        temperature: The temperature to use
        max_tokens: The maximum number of tokens to generate
        system_message: The system message to use

    Returns:
        The completion text
    """
    response = openai_client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def get_structured_output(
    prompt: str,
    model: str = settings.DEFAULT_MODEL,
    temperature: float = settings.DEFAULT_TEMPERATURE,
    max_tokens: int = settings.DEFAULT_MAX_TOKENS,
    system_message: str = "You are a helpful assistant.",
    response_format=None,
):
    """
    Get a structured output from the OpenAI API.

    Args:
        prompt: The prompt to send to the API
        model: The model to use
        temperature: The temperature to use
        max_tokens: The maximum number of tokens to generate
        system_message: The system message to use
        response_format: The response format to use (e.g., {"type": "json_object"})

    Returns:
        The structured output
    """
    kwargs = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
    }

    if response_format:
        kwargs["response_format"] = response_format

    response = openai_client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
