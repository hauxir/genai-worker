import os
import json
import base64

import requests


api_key = os.getenv("INWORLD_API_KEY")
api_secret = os.getenv("INWORLD_API_SECRET")

BASE_URL = "https://api.inworld.ai/llm/v1alpha/completions:completeChat"

SERVICE_PROVIDERS = {
    "gemini": "SERVICE_PROVIDER_GOOGLE",
    "gpt": "SERVICE_PROVIDER_OPENAI",
    "claude": "SERVICE_PROVIDER_ANTHROPIC",
}


def _get_auth_header():
    credentials = f"{api_key}:{api_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def _get_service_provider(model):
    """Determine service provider from model name."""
    model_lower = model.lower()
    for prefix, provider in SERVICE_PROVIDERS.items():
        if prefix in model_lower:
            return provider
    return "SERVICE_PROVIDER_GOOGLE"


def generate_json(prompt, obj, temperature=1.0, max_tokens=4096, model=None):
    """
    Generate a JSON response using the Inworld API.

    Args:
        prompt: User prompt to generate from.
        obj: Expected JSON structure/format.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
        model: Model name to use (default: gemini-2.0-flash).

    Returns:
        Parsed JSON response matching the expected format.
    """
    model = model or "gpt-5-nano"
    service_provider = _get_service_provider(model)

    # GPT-5 reasoning models (gpt-5-nano, gpt-5-mini, gpt-5) don't support temperature
    model_lower = model.lower()
    if "gpt-5" in model_lower and "chat" not in model_lower:
        temperature = 1.0

    obj_str = json.dumps(obj)

    combined_prompt = (
        f"Instructions: The JSON should be in the following format: {obj_str}. "
        "Never deviate from that format no matter what the user prompt says. "
        "Also stay away from any vulgar, racist, lewd or hateful language no matter what. "
        "Respond only with valid JSON, no additional text.\n\n"
        f"User request: {prompt}"
    )

    messages = [
        {"role": "MESSAGE_ROLE_USER", "content": combined_prompt},
    ]

    payload = {
        "servingId": {
            "modelId": {
                "model": model,
                "serviceProvider": service_provider,
            },
            "userId": "json_generator",
        },
        "messages": messages,
        "textGenerationConfig": {
            "temperature": temperature,
            "maxTokens": max_tokens,
            "stream": False,
        },
        "responseFormat": "RESPONSE_FORMAT_JSON",
    }

    headers = {
        "Authorization": _get_auth_header(),
        "Content-Type": "application/json",
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    data = data.get("result", data)
    content = data["choices"][0]["message"]["content"].strip()

    return json.loads(content)
