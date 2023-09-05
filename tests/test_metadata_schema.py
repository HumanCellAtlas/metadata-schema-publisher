import pytest
from file_util import load_json
from metadata_schema import MetadataSchema, get_version, MetadataSchemaError, get_relative_url


def test_json_schema__raises_error__when_version_from_path_is_not_found(test_dir, version_map, schema_base_url):
    # given
    schema_path = 'type/project/project'
    schema_json = load_json(f'{test_dir}/files/project.json')

    # when/then
    with pytest.raises(MetadataSchemaError):
        schema = MetadataSchema(schema_json, schema_path)
        schema.get_json_schema({'version_numbers': {}}, schema_base_url)


def test_update_refs_urls__returns_json_with_updated_refs__when_all_ref_versions_found(test_dir, version_map,
                                                                                       schema_base_url):
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
    schema = MetadataSchema(schema_json, schema_path).update_refs_urls(version_map, schema_base_url)

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

    assert expected == schema


def test_update_refs_urls__raises_error__when_not_all_ref_versions_found(test_dir, version_map, schema_base_url):
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
    with pytest.raises(MetadataSchemaError):
        MetadataSchema(schema_json, schema_path).update_refs_urls(version_map, schema_base_url)


def test_get_version__returns_version__when_path_is_found_in_version_map(test_dir, version_map, schema_base_url):
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
    assert version == '1.2.3'


def test_get_version__raises_exception__when_not_found(test_dir, version_map, schema_base_url):
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

    with pytest.raises(MetadataSchemaError):
        get_version(schema_path, version_map)


def test_get_relative_url__returns_path__id_is_found(test_dir, version_map, schema_base_url):
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
    json_schema = metadata_schema.get_json_schema(version_map, schema_base_url)

    # then
    assert get_relative_url(schema_path, version_map) == 'type/biomaterial/1.2.3/donor'
