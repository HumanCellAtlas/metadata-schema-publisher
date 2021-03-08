import json
import os

from unittest import TestCase

from metadata_schema import MetadataSchema, get_version, MetadataSchemaError, get_relative_url


def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.loads(f.read())


class MetadataSchemaTest(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.version_map = load_json(f'{self.test_dir}/files/versions.json')
        self.schema_base_url = 'https://schema.humancellatlas.org/'

    def test_json_schema__returns_dict_with_schema_urls_in_id_and_refs__when_version_from_path_is_found(self):
        # given
        schema_path = 'type/project/project'
        schema_json = load_json(f'{self.test_dir}/files/project.json')

        # when
        schema = MetadataSchema(schema_json, schema_path)

        # then
        expected = load_json(f'{self.test_dir}/files/project-schema.json')
        self.assertEqual(schema.get_json_schema(self.version_map, self.schema_base_url), expected)

    def test_json_schema__raises_error__when_version_from_path_is_not_found(self):
        # given
        schema_path = 'type/project/project'
        schema_json = load_json(f'{self.test_dir}/files/project.json')

        # when/then
        with self.assertRaises(MetadataSchemaError):
            schema = MetadataSchema(schema_json, schema_path)
            schema.get_json_schema({'version_numbers': {}}, self.schema_base_url)

    def test_insert_id_url__inserts_id_property__when_version_from_path_is_found(self):
        # given
        schema_json = {
            '$schema': 'http://json-schema.org/draft-07/schema#',
        }
        version_map = {
            'version_numbers': {
                'type': {
                    'biomaterial': {
                        'donor': '1.2.3'
                    }
                }
            }
        }
        schema_path = 'type/biomaterial/donor'
        # when
        schema = MetadataSchema(schema_json, schema_path).insert_id_url(version_map, self.schema_base_url)
        # then
        self.assertEqual(schema.get('$id'), 'https://schema.humancellatlas.org/type/biomaterial/1.2.3/donor')

    def test_insert_id_url__raises_error__when_version_from_path_is_not_found(self):
        # given
        schema_json = {
            '$schema': 'http://json-schema.org/draft-07/schema#',
        }
        version_map = {
            'version_numbers': {
                'type': {
                    'biomaterial': {
                        'donor': '1.2.3'
                    }
                }
            }
        }
        schema_path = 'type/biomaterial/cell_suspension'

        # when/then
        with self.assertRaises(MetadataSchemaError):
            MetadataSchema(schema_json, schema_path).get_json_schema(version_map, self.schema_base_url)

    def test_insert_id_url__inserts_old_id_key__when_draft_04(self):
        # given
        schema_json = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
        }
        version_map = {
            'version_numbers': {
                'type': {
                    'biomaterial': {
                        'donor': '1.2.3'
                    }
                }
            }
        }
        schema_path = 'type/biomaterial/donor'
        # when
        schema = MetadataSchema(schema_json, schema_path).insert_id_url(version_map, self.schema_base_url)
        # then
        self.assertEqual(schema.get('id'), 'https://schema.humancellatlas.org/type/biomaterial/1.2.3/donor')

    def test_update_refs_urls__returns_json_with_updated_refs__when_all_ref_versions_found(self):
        # given
        schema_json = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'properties': {
                'provenance': {
                    'description': 'Provenance information provided by the system.',
                    'type': 'object',
                    '$ref': 'system/provenance.json'
                },
            }
        }
        version_map = {
            'version_numbers': {
                'type': {
                    'biomaterial': {
                        'donor': '1.2.3'
                    }
                },
                'system': {
                    'provenance': '1.0.0'
                }
            }
        }
        schema_path = 'type/biomaterial/donor'

        # when
        schema = MetadataSchema(schema_json, schema_path).update_refs_urls(version_map, self.schema_base_url)

        # then
        expected = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'properties': {
                'provenance': {
                    'description': 'Provenance information provided by the system.',
                    'type': 'object',
                    '$ref': 'https://schema.humancellatlas.org/system/1.0.0/provenance'
                },
            }
        }

        self.assertEqual(expected, schema)

    def test_update_refs_urls__raises_error__when_not_all_ref_versions_found(self):
        # given
        schema_json = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'properties': {
                'provenance': {
                    'description': 'Provenance information provided by the system.',
                    'type': 'object',
                    '$ref': 'system/provenance.json'
                },
            }
        }
        version_map = {
            'version_numbers': {
                'type': {
                    'biomaterial': {
                        'donor': '1.2.3'
                    }
                },
            }
        }

        schema_path = 'type/biomaterial/donor'

        # when / then
        with self.assertRaises(MetadataSchemaError):
            MetadataSchema(schema_json, schema_path).update_refs_urls(version_map, self.schema_base_url)

    def test_get_version__returns_version__when_path_is_found_in_version_map(self):
        # given
        schema_path = 'type/biomaterial/donor'
        version_map = {
            'version_numbers': {
                'type': {
                    'biomaterial': {
                        'donor': '1.2.3'
                    }
                }
            }
        }

        # when
        version = get_version(schema_path, version_map)

        # then
        self.assertEqual(version, '1.2.3')

    def test_get_version__raises_exception__when_not_found(self):
        # given
        schema_path = 'type/biomaterial/cell_suspension'
        version_map = {
            'version_numbers': {
                'type': {
                    'biomaterial': {
                        'donor': '1.2.3'
                    }
                }
            }
        }

        with self.assertRaises(MetadataSchemaError):
            get_version(schema_path, version_map)

    def test_get_relative_url__returns_path__id_is_found(self):
        # given
        schema_json = {
            '$schema': 'http://json-schema.org/draft-07/schema#'
        }
        version_map = {
            'version_numbers': {
                'type': {
                    'biomaterial': {
                        'donor': '1.2.3'
                    }
                }
            }
        }
        schema_path = 'type/biomaterial/donor'
        # when
        metadata_schema = MetadataSchema(schema_json, schema_path)
        json_schema = metadata_schema.get_json_schema(version_map, self.schema_base_url)

        # then
        self.assertEqual(get_relative_url(schema_path, version_map), 'type/biomaterial/1.2.3/donor')