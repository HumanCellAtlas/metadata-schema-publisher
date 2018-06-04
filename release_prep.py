import json
from optparse import OptionParser
import pprint

import os

SCHEMA_BASE = "https://schema.humancellatlas.org/"
SCHEMA_BASE_DEV = "http://schema.dev.data.humancellatlas.org/"


class ReleasePreparation():

    def _findSchemaVersion(self, schema, versions):
        hierarchy = schema.split("/")

        latest = versions["version_numbers"]

        for e in hierarchy:
            latest = latest[e]

        if not isinstance(latest, dict):
            return latest

    def _findValue(self, key, dictionary):
        for k, v in dictionary.items():
            if k == key:
                yield v
            elif isinstance(v, dict):
                for result in self._findValue(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    if isinstance(d, dict):
                        for result in self._findValue(key, d):
                            yield result

    def _replaceValue(self, key, dictionary, old, new):
        for k in dictionary.keys():
            if k == key and dictionary[k] == old:
                dictionary[k] = new
            elif isinstance(dictionary[k], dict):
                self._replaceValue(key, dictionary[k], old, new)
            elif isinstance(dictionary[k], list):
                for d in dictionary[k]:
                    if isinstance(d, dict):
                        self._replaceValue(key, d, old, new)

    def _insertIntoDict(self, dict, obj, pos):
        return {k: v for k, v in (list(dict.items())[:pos] + list(obj.items()) + list(dict.items())[pos:])}

    def expandURLs(self, base_server_path, path, file_data, version_numbers, branch_name):
        if branch_name == "develop":
            self.schema_base = SCHEMA_BASE_DEV
        else:
            self.schema_base = SCHEMA_BASE

        rel = path.replace(base_server_path + "/", "")
        rel = rel.replace(".json", "")

        if branch_name == "develop":
            version = "latest"
        else:
            version = self._findSchemaVersion(rel, version_numbers)

        el = rel.split("/")
        el.insert(len(el) - 1, version)

        id_url = self.schema_base + "/".join(el)
        id = ({'id': id_url})
        newJson = self._insertIntoDict(file_data, id, 1)

        for item in self._findValue("$ref", newJson):
            if self.schema_base not in item:
                d = item.replace(".json", "")

                if "#" in d:
                    v = version
                    el = d.split("/")
                    for i in range(0, len(el)):
                        if "#" in el[i]:
                            el.insert(i, v)
                            break
                else:
                    if branch_name == "develop":
                        v = "latest"
                    else:
                        v = self._findSchemaVersion(d, version_numbers)

                    el = d.split("/")
                    el.insert(len(el) - 1, v)

                expanded = self.schema_base + "/".join(el)

                self._replaceValue("$ref", newJson, item, expanded)

        return newJson


def _getJson(path):
    f = open(path, 'r')
    return json.loads(f.read())

def _saveJson(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def _getSchemaPaths(path):
    schemas = [os.path.join(dirpath, f)
               for dirpath, dirnames, files in os.walk(path)
               for f in files if f.endswith('.json') and not f.endswith('versions.json')]
    return schemas


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

    versions = _getJson(path + "/versions.json")

    schemas = _getSchemaPaths(path)

    context = options.context

    for s in schemas:
        jsonSchema = _getJson(s)

        newJson = releasePrep.expandURLs(path, s, jsonSchema, versions, context)

        _saveJson(s, newJson)
