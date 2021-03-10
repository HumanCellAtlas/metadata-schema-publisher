import copy
from collections import OrderedDict


def find_values_with_key(key_to_find, dictionary):
    for key, value in dictionary.items():
        if key == key_to_find:
            yield value
        elif isinstance(value, dict):
            for result in find_values_with_key(key_to_find, value):
                yield result
        elif isinstance(value, list):
            for d in value:
                if isinstance(d, dict):
                    for result in find_values_with_key(key_to_find, d):
                        yield result


class ImmutableDict:
    def __init__(self, value: dict):
        self.value = copy.deepcopy(value)

    def insert_obj_at(self, obj: dict, pos: int) -> OrderedDict:
        return OrderedDict({k: v for k, v in (list(self.value.items())[:pos] + list(obj.items()) + list(self.value.items())[pos:])})

    def replace_values_with_key(self, key: str, old_to_new_value_map: dict):
        self._replace_value_with_key(key, self.value, old_to_new_value_map)
        return self.value

    def _replace_value_with_key(self, key_to_change: str, dictionary: dict, old_to_new_value_map: dict):
        for key in dictionary.keys():
            if key == key_to_change:
                new_value = old_to_new_value_map.get(dictionary[key], dictionary[key])
                dictionary[key] = new_value
            elif isinstance(dictionary[key], dict):
                self._replace_value_with_key(key_to_change, dictionary[key], old_to_new_value_map)
            elif isinstance(dictionary[key], list):
                for d in dictionary[key]:
                    if isinstance(d, dict):
                        self._replace_value_with_key(key_to_change, d, old_to_new_value_map)