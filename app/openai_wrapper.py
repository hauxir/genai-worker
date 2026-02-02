import os
import json
import base64
import tempfile

import requests
from openai import OpenAI
import common

api_key = os.getenv("OPENAI_API_KEY")
imgpush_host = os.getenv("IMGPUSH_HOST")

client = OpenAI(api_key=api_key)


def generate_json(prompt, obj, temperature=1.1, max_tokens=4096, model=None):
    obj_str = json.dumps(obj)

    response = client.chat.completions.create(
        model=model or "gpt-5-nano",
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
    image_base64_json = result.json()
    if isinstance(image_base64_json, str):
        image_base64_json = json.loads(image_base64_json)
    image_base64 = image_base64_json["data"][0]["b64_json"]
    image_bytes = base64.b64decode(image_base64)
    image_bytes_cropped = common.crop_transparent_image(image_bytes)
    imgpush_response = requests.post(imgpush_host, files={"file": ("image.png", image_bytes_cropped)}).json()
    return dict(url=f"{imgpush_host}/{imgpush_response['filename']}")


def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    temp = tempfile.NamedTemporaryFile(delete=False, dir="/tmp", suffix=".png")
    temp.write(response.content)
    temp.flush()
    temp.close()
    return temp.name


def edit_image(prompt, image_url, mask_url=None):
    image_path = download_image(image_url)
    mask_path = download_image(mask_url) if mask_url else None

    try:
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()
        mask_data = None
        if mask_path:
            with open(mask_path, "rb") as mask_file:
                mask_data = mask_file.read()

        result = client.images.edit(
            model="gpt-image-1",
            image=image_data,
            mask=mask_data,
            prompt=prompt
        )

        image_base64_json = result.json()
        if isinstance(image_base64_json, str):
            image_base64_json = json.loads(image_base64_json)

        image_base64 = image_base64_json["data"][0]["b64_json"]
        image_bytes = base64.b64decode(image_base64)

        imgpush_response = requests.post(imgpush_host, files={"file": ("image.png", image_bytes)}).json()

        return dict(url=f"{imgpush_host}/{imgpush_response['filename']}")
    finally:
        os.remove(image_path)
        if mask_path:
            os.remove(mask_path)
