import assertpy
import pytest
from assertpy import assert_that

from metadata_schema import MetadataSchema, MetadataSchemaError


def test__inserts_id_property__when_version_from_path_is_found(test_dir, version_map, schema_base_url):
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
    schema = MetadataSchema(schema_json, schema_path).insert_id_url(version_map, schema_base_url)
    # then
    assert schema.get('$id') == 'https://schema.humancellatlas.org/type/biomaterial/1.2.3/donor'


def test__raises_error__when_version_from_path_is_not_found(test_dir, version_map, schema_base_url):
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
    with pytest.raises(MetadataSchemaError):
        MetadataSchema(schema_json, schema_path).get_json_schema(version_map, schema_base_url)


def test__inserts_old_id_key__when_draft_04(test_dir, version_map, schema_base_url):
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
    schema = MetadataSchema(schema_json, schema_path).insert_id_url(version_map, schema_base_url)
    # then
    assert schema.get('id') == 'https://schema.humancellatlas.org/type/biomaterial/1.2.3/donor'

from file_util import load_json

@pytest.fixture
def project_schema_json(test_dir):
    return load_json(f'{test_dir}/files/project.json')

@pytest.fixture
def project_schema_json_with_id(test_dir):
    return load_json(f'{test_dir}/files/project_with_id.json')
def test_json_schema__returns_dict_with_schema_urls_in_id_and_refs__when_version_from_path_is_found(test_dir,
                                                                                                    version_map,
                                                                                                    schema_base_url,
                                                                                                    project_schema_json):
    # given
    schema_path = 'type/project/project'

    # when
    schema = MetadataSchema(project_schema_json, schema_path)

    # then
    expected = load_json(f'{test_dir}/files/project-schema.json')
    actual = schema.get_json_schema(version_map, schema_base_url)
    assert_that(actual).contains('$id')
    assert_that(actual).is_equal_to(expected, include='$id')
    assert_that(actual).is_equal_to(expected)


def test__when_document_contains_id_attribute(test_dir, version_map, schema_base_url, project_schema_json_with_id):
    # given
    schema_path = 'type/project/project'

    # when
    schema = MetadataSchema(project_schema_json_with_id, schema_path)

    # then
    expected = load_json(f'{test_dir}/files/project-schema.json')
    actual = schema.get_json_schema(version_map, schema_base_url)
    assert_that(actual).contains('$id')
    assert_that(actual).is_equal_to(expected, include='$id')
    assert_that(actual).is_equal_to(expected)
