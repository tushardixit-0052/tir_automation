import json
from jsonschema import validate
from pathlib import Path


def assert_response_exists(response):
    assert response is not None, "API did not return any response"


def assert_schema(response_json, schema_name: str):
    schema_path = Path(f"tests/schemas/{schema_name}")
    with open(schema_path) as f:
        schema = json.load(f)

    validate(instance=response_json, schema=schema)
