import json
from pathlib import Path

import requests


class FakeRes:
    def __init__(self, json):
        self.json_res = json

    def json(self):
        return self.json_res


def get(*args, **kwargs):

    if "dishas.obspm.fr" not in args[0]:  # pragma: no cover
        return requests.api.get(*args, **kwargs)

    dir = Path("dishas_cache")
    dir.mkdir(exist_ok=True)

    table_id: str = args[0].split("&source")[0].split("id=")[1]
    path = dir / f"{table_id}.json"
    if path.exists():
        with open(path, "r") as f:
            return FakeRes(json.load(f))

    res = requests.api.get(*args, **kwargs)
    text = res.text
    if res.status_code == 200:
        with open(path, "w+") as f:
            f.write(text)

    return res


requests.get = get
