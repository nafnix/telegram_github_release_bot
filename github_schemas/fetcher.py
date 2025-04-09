from pathlib import Path

import orjson
import requests


data = requests.get(
    'https://octokit.github.io/webhooks/payload-examples/api.github.com/index.json'
).content


folder = Path('./github_schemas')


for schema in orjson.loads(data):
    with Path.open(folder / f'{schema["name"]}.json', 'wb') as schema_file:
        schema_file.write(orjson.dumps(schema))
