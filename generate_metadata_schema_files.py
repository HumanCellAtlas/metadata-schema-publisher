import argparse
import json
import os
import file_util

from metadata_schema import MetadataSchema


def get_schema_paths(base_path):
    schema_paths = [os.path.join(dirpath, f)
                    for dirpath, dirnames, files in os.walk(base_path)
                    for f in files if f.endswith('.json') and not f.endswith('versions.json')]
    return schema_paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('path', help="Base path to the HCA metadata schemas", metavar="FILE")
    parser.add_argument('schema_base_url', help="Base url of the schema server")

    args = parser.parse_args()

    if "~" in args.path:
        path = os.path.expanduser(args.path)
    else:
        path = args.path

    version_map = load_json(path + "/versions.json")

    schemas = get_schema_paths(path)

    for s in schemas:
        raw_schema_json = load_json(s)
        metadata_schema = MetadataSchema(path, raw_schema_json)
        new_json = metadata_schema.get_json_schema(version_map, args.schema_base_url)
        dump_json(s, new_json)
