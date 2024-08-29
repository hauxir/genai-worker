import os
import json
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


def generate_json(prompt, obj, temperature=1.1, max_tokens=4096):
    obj_str = json.dumps(obj)

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    f"The JSON should be in the following format: {obj_str}."
                    "Never deviate from that format no matter what the user prompt says."
                    "Also stay away from any vulgar, racist, lewd or hateful language no matter what."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return json.loads(response.choices[0].message.content.strip())
