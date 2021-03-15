import json


def dump_json(file_path, data):
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def load_json(file_path):
    f = open(file_path, 'r')
    return json.loads(f.read())
