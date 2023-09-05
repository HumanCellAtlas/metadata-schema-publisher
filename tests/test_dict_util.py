from unittest import TestCase

from dict_util import find_values_with_key



def test_find_values_with_key__return_values__when_in_obj():
    # given
    dikt = {'ref': 'value'}

    # when
    result = find_values_with_key('ref', dikt)

    # then
    assert list(result) == ['value']

def test_find_values_with_key__return_empty_generator__when_not_in_obj():
    # given
    dikt = {'key': 'value'}

    # when
    result = find_values_with_key('ref', dikt)

    # then
    assert list(result) == []


def test_find_values_with_key__return_values__when_in_nested_obj():
    # given
    dikt = {'key': {'ref': 'value'}}

    # when
    result = find_values_with_key('ref', dikt)

    # then
    assert list(result) == ['value']


def test_find_values_with_key__return_values__when_in_nested_obj_2_levels():
    # given
    dikt = {
        'key': {
            'key': {
                'ref': 'value'
            }
        }
    }

    # when
    result = find_values_with_key('ref', dikt)

    # then
    assert list(result) == ['value']

def test_find_values_with_key__return_values__when_in_nested_obj_4_levels():
    # given
    dikt = {
        'key': {
            'key': {
                'key': {
                    'key': {
                        'ref': 'value'
                    }
                }
            }
        }
    }

    # when
    result = find_values_with_key('ref', dikt)

    # then
    assert list(result) == ['value']

def test_find_values_with_key__return_values__when_found_many_in_nested_obj_4_levels():
    # given
    dikt = {
        'key': {
            'key': {
                'key': {
                    'key': {
                        'ref': 'value'
                    },
                    'ref': 'value5'
                },
                'ref': 'value4'
            },
            'ref': 'value3'
        },
        'ref': 'value2'
    }

    # when
    result = find_values_with_key('ref', dikt)

    # then
    assert sorted(list(result)) == sorted(['value', 'value2', 'value3', 'value4', 'value5'])

def test_find_values_with_key__return_values__when_found_many_non_unique_in_nested_obj_4_levels():
    # given
    dikt = {
        'key': {
            'key': {
                'key': {
                    'key': {
                        'ref': 'value'
                    },
                    'ref': 'value3'
                },
                'ref': 'value3'
            },
            'ref': 'value3'
        },
        'ref': 'value2'
    }

    # when
    result = find_values_with_key('ref', dikt)

    # then
    assert sorted(list(result)) == sorted(['value', 'value2', 'value3', 'value3', 'value3'])

def test_find_values_with_key__return_values__when_obj_in_list():
    # given
    dikt = {
        'key': [
            {'ref': 'value'}
        ]
    }

    # when
    result = find_values_with_key('ref', dikt)

    # then
    assert list(result) == ['value']

def test_find_values_with_key__return_values__when_obj_in_nested_list():
    # given
    dikt = {
        'key': [{
            'key': [{
                'key': [{
                    'ref': 'value'
                }]
            }]
        }]
    }

    # when
    result = find_values_with_key('ref', dikt)

    # then
    assert list(result) == ['value']

def test_find_values_with_key__return_values__when_obj_in_many_nested_list():
    # given
    dikt = {
        'key': [
            {
                'key': [{
                    'key': [{
                        'ref': 'value0'
                    }]
                }]
            },
            {
                'key': [{
                    'key': [{
                        'ref': 'value1'
                    }]
                }]
            },
            {
                'key': [{
                    'key': [{
                        'ref': 'value2'
                    }]
                }]
            },
            {
                'key': [{
                    'key': [{
                        'ref': 'value3'
                    }]
                }]
            },
            {
                'key': [{
                    'key': [{
                        'ref': 'value3'
                    }]
                }]
            },
            {
                'key': [{
                    'key': [{
                        'ref': 'value3'
                    }]
                }]
            }
        ]
    }

    # when
    result = find_values_with_key('ref', dikt)

    # then
    assert list(result) == ['value0', 'value1', 'value2', 'value3', 'value3', 'value3']
