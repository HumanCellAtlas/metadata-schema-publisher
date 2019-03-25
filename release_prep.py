import json
import os
from optparse import OptionParser


class ReleasePreparation:
    def __init__(self, schema_url, version_map):
        self.schema_url = schema_url
        self.version_map = version_map

    def _find_schema_version(self, schema):
        hierarchy = schema.split("/")

        latest = self.version_map["version_numbers"]

        for e in hierarchy:
            latest = latest[e]

        if not isinstance(latest, dict):
            return latest

    def _find_value(self, key, dictionary):
        for k, v in dictionary.items():
            if k == key:
                yield v
            elif isinstance(v, dict):
                for result in self._find_value(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    if isinstance(d, dict):
                        for result in self._find_value(key, d):
                            yield result

    def _replace_value(self, key, dictionary, old, new):
        for k in dictionary.keys():
            if k == key and dictionary[k] == old:
                dictionary[k] = new
            elif isinstance(dictionary[k], dict):
                self._replace_value(key, dictionary[k], old, new)
            elif isinstance(dictionary[k], list):
                for d in dictionary[k]:
                    if isinstance(d, dict):
                        self._replace_value(key, d, old, new)

    def _insert_into_dict(self, dict, obj, pos):
        return {k: v for k, v in (list(dict.items())[:pos] + list(obj.items()) + list(dict.items())[pos:])}

    def expand_urls(self, relative_path, file_data):
        version = self._find_schema_version(relative_path)

        el = relative_path.split("/")
        el.insert(len(el) - 1, version)

        id_url = self.schema_url + "/".join(el)

        if "draft-04" in file_data["$schema"]:
            id_key = "id"
        else:
            id_key = "$id"

        id = ({id_key: id_url})
        new_json = self._insert_into_dict(file_data, id, 1)

        for item in self._find_value("$ref", new_json):
            if self.schema_url not in item:
                d = item.replace(".json", "")

                if "#" in d:
                    v = version
                    el = d.split("/")
                    for i in range(0, len(el)):
                        if "#" in el[i]:
                            el.insert(i, v)
                            break
                else:
                    v = self._find_schema_version(d)

                    el = d.split("/")
                    el.insert(len(el) - 1, v)

                expanded = self.schema_url + "/".join(el)

                self._replace_value("$ref", new_json, item, expanded)

        return new_json

    def get_schema_key(self, file_data):
        if "draft-04" in file_data["$schema"]:
            schema_id_key = "id"
        else:
            schema_id_key = "$id"
        if schema_id_key in file_data:
            schema_id = file_data[schema_id_key]
            key = schema_id.replace(".json", "")
            key = key.replace(self.schema_url, "")
        else:
            key = None
        return key


def _get_json(path):
    f = open(path, 'r')
    return json.loads(f.read())


def _save_json(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def _get_schema_paths(path):
    schema_paths = [os.path.join(dirpath, f)
               for dirpath, dirnames, files in os.walk(path)
               for f in files if f.endswith('.json') and not f.endswith('versions.json')]
    return schema_paths


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path",
                      help="Base path to the HCA metadata schemas", metavar="FILE")
    parser.add_option("-c", "--context", dest="context",
                      help="Release context")

    (options, args) = parser.parse_args()

    if not options.path:
        print("You must supply the path to the metadata schema directory")
        exit(2)

    releasePrep = ReleasePreparation()

    if "~" in options.path:
        path = os.path.expanduser(options.path)
    else:
        path = options.path

    versions = _get_json(path + "/versions.json")

    schemas = _get_schema_paths(path)

    context = options.context

    for s in schemas:
        json_schema = _get_json(s)

        newJson = releasePrep.expand_urls(path, s, json_schema)

        _save_json(s, newJson)
