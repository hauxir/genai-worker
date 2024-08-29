import time
import os
import json

from celery.result import AsyncResult
from flask import Flask, Response, request, jsonify

import common
import worker

app = Flask(__name__)

SECRET = os.getenv("SECRET")


def remove_old_files(directory, age_limit):
    current_time = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > age_limit:
                os.remove(file_path)


def process_prompt(prompt, format, temperature, force_new_result):
    hash = common.hash_parameters_md5(prompt, format, temperature)
    file_path = f"/tmp/{hash}.txt"
    if os.path.exists(file_path) and not force_new_result:
        with open(file_path, "r") as file:
            content = file.read()
            if content:
                return dict(state="ready", result=json.loads(content))
            else:
                return dict(state="pending")
    else:
        with open(file_path, "w") as file:
            pass
        worker.process_prompt.delay(prompt, format, temperature)
        return dict(state="started")


@app.route("/api/json", methods=["POST"])
def gpt_json():
    auth_header = request.headers.get("Authorization")
    if SECRET and (not auth_header or auth_header.split()[-1] != SECRET):
        return Response("Unauthorized", 401)
    prompt = request.json.get("prompt")
    format = json.loads(json.dumps(request.json.get("format", dict())))
    temperature = request.json.get("temperature", 1.1)
    force_new_result = request.json.get("force_new_result", False)

    results = process_prompt(prompt, format, temperature, force_new_result)

    if results["state"] == "started":
        remove_old_files("/tmp", 3600)

    return jsonify(results)
