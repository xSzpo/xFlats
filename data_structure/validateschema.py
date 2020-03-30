from jsonschema import validate, Draft3Validator, SchemaError, ValidationError
import jsonschema
import json
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
schema_file = "schema.json"


with open(os.path.join(dir_path, schema_file), "r") as file:
    schema = json.load(file)

with open(os.path.join(dir_path, "oto_28366699_850000.json"), "r") as file:
    jsonfile = json.load(file)


valid = Draft3Validator(schema)

if not valid.is_valid(jsonfile):
    errors = sorted(valid.iter_errors(jsonfile), key=lambda e: e.absolute_path)
    print([(e.relative_path[-1]+" -> "+e.message) for e in errors])
