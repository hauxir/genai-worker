import json

from celery import Celery

import openai_wrapper
import inworld_wrapper
import common


app = Celery("worker", broker="redis://localhost/0", backend="redis://localhost/1")


@app.task(bind=True)
def process_prompt(self, prompt, format, temperature, provider="openai", model=None):
    hash = common.hash_parameters_md5(prompt, format, temperature, provider, model)
    file_path = f"/tmp/{hash}.txt"

    if provider == "inworld":
        result = inworld_wrapper.generate_json(prompt, format, temperature, model=model)
    else:
        result = openai_wrapper.generate_json(prompt, format, temperature, model=model)

    with open(file_path, "w") as file:
        file.write(json.dumps(result))

    return result


@app.task(bind=True)
def process_image_prompt(self, prompt, size, quality, background=None):
    hash = common.hash_parameters_md5(prompt, size, quality, background)
    file_path = f"/tmp/{hash}.txt"

    result = openai_wrapper.generate_image(prompt, size, quality, background)

    with open(file_path, "w") as file:
        file.write(json.dumps(result))

    return result


__all__ = ["app"]
