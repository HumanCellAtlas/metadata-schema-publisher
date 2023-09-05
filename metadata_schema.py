import traceback

from dict_util import ImmutableDict, find_values_with_key


class MetadataSchema:
    def __init__(self, raw_json: dict, schema_path: str):
        self.raw_json = raw_json
        self.schema_path = schema_path
        self.json = raw_json

    def get_json_schema(self, version_map: dict, schema_base_url: str):
        self.json = self.insert_id_url(version_map, schema_base_url)
        self.json = self.update_refs_urls(version_map, schema_base_url)
        return self.json

    def insert_id_url(self, version_map, schema_base_url):
        id = generate_id(self.schema_path, schema_base_url, version_map)
        id_key = self.get_id_key()
        id_obj = {id_key: id}
        print(f'id_obj: {id_obj}')
        self.raw_json.update(id_obj)
        json_schema = self.raw_json
        print(f'id after update: {json_schema[id_key]}')
        return json_schema

    def update_refs_urls(self, version_map, schema_base_url) -> dict:
        ref_changes = {}
        entity_version = get_version(self.schema_path, version_map)
        for schema_ref in find_values_with_key("$ref", self.json):
            if schema_base_url not in schema_ref:
                ref_path = schema_ref.replace(".json", "")
                ref_path_parts = ref_path.split("/")
                ref_path_parts_len = len(ref_path_parts)

                if "#" in ref_path:
                    for i in range(0, ref_path_parts_len):
                        if "#" in ref_path_parts[i]:
                            ref_path_parts.insert(i, entity_version)
                            break
                else:
                    ref_version = get_version(ref_path, version_map)
                    ref_path_parts.insert(ref_path_parts_len - 1, ref_version)

                new_schema_ref = schema_base_url + "/".join(ref_path_parts)
                ref_changes[schema_ref] = new_schema_ref

        immutable_schema = ImmutableDict(self.json)
        self.json = immutable_schema.replace_values_with_key("$ref", ref_changes)
        return self.json

    def get_id_key(self):
        if "draft-04" in self.json.get("$schema"):
            id_key = "id"
        else:
            id_key = "$id"
        return id_key


def get_version(schema_path: str, version_map: dict) -> str:
    hierarchy = schema_path.split("/")
    latest = version_map["version_numbers"]

    try:
        for path in hierarchy:
            latest = latest[path]
    except KeyError as e:
        raise MetadataSchemaError(f'The version for {schema_path} is not found')

    if not isinstance(latest, dict):
        return latest


def generate_id(schema_path, schema_base_url, version_map):
    id_url = schema_base_url + get_relative_url(schema_path, version_map)
    print(f'id_url: {id_url}')
    return id_url


def get_relative_url(schema_path, version_map) -> str:
    version = get_version(schema_path, version_map)
    print(f'schema_path: {schema_path}')
    el = schema_path.split("/")
    el.insert(len(el) - 1, version)
    return "/".join(el)


class MetadataSchemaError(Exception):
    """Base-class for all exceptions raised by this module."""
