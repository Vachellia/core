import yaml
import json


def get_yaml(file_name):
    try:
        with open(file_name) as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            return yaml.load(file, Loader=yaml.FullLoader)
    except Exception as error:
        raise Exception(f"get_yaml method error: {error}")

def get_json(file_name):
    try:
        with open(file_name) as json_file:
            return json.load(json_file)
    except Exception as error:
        raise Exception(f"get_json method error: {error}")