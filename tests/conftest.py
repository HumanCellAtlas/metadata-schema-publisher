import os

import pytest

from file_util import load_json


@pytest.fixture
def schema_base_url():
    return 'https://schema.humancellatlas.org/'


@pytest.fixture
def version_map(test_dir):
    return load_json(f'{test_dir}/files/versions.json')


@pytest.fixture
def test_dir():
    return os.path.dirname(os.path.realpath(__file__))
