import os
import json

import requests
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
imgpush_host = os.getenv("IMGPUSH_HOST")

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


def generate_image(prompt, size="1024x1024", quality="high", background=None):
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size,
        background=background,
        quality=quality
    )
    image_base64 = result.json()["data"][0]["b64_json"]
    image_bytes = base64.b64decode(image_base64)
    imgpush_response = requests.post(imgpush_host, files={"file": ("image.png", image_bytes)}).json()
    return dict(url=f"{imgpush_host}/{imgpush_response["filename"]})
