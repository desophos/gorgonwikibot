"""Automatic download of json files, latest version, with local cache."""

import json
import os
from functools import lru_cache

import requests

version = requests.get("http://client.projectgorgon.com/fileversion.txt").text
path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), ".cache", "v" + version)
)

os.makedirs(path, exist_ok=True)


def _download(file):
    return requests.get(
        f"http://cdn.projectgorgon.com/v{version}/data/{file}.json"
    ).json()


@lru_cache  # files don't change at runtime, so skip repeated I/O
def get_file(file):
    filename = os.path.join(path, file + ".json")
    try:
        # look for file in local cache
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # file not downloaded, so retrieve from server and store locally
        contents = _download(file)
        with open(filename, "w") as f:
            json.dump(contents, f)
        return contents
