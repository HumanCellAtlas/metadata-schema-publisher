from collections import OrderedDict
from unittest import TestCase

from dict_util import ImmutableDict


class ImmutableDictTest(TestCase):
    def test_insert_obj_at__return_obj_with_obj_at_pos_and_original_obj_unchanged(self):
        # given
        dic = {'key': 'value'}
        obj = {'$id': 'id'}

        # when
        idic = ImmutableDict(dic)
        result = idic.insert_obj_at(obj, 0)

        # then
        expected = OrderedDict({
            '$id': 'id',
            'key': 'value'
        })
        self.assertEqual(result, expected)
        self.assertEqual(dic, {'key': 'value'})

    def test_insert_obj_at__return_obj_and_didnt_change_orig_obj__when_valid_pos(self):
        # given
        dic = {
            'key': 'value',
            'key2': 'value'
        }
        obj = {'$id': 'id'}

        # when
        idic = ImmutableDict(dic)
        result = idic.insert_obj_at(obj, 1)

        # then
        expected = OrderedDict({
            'key': 'value',
            '$id': 'id',
            'key2': 'value'
        })
        self.assertEqual(list(expected.keys()), list(result.keys()))
        self.assertEqual(list(expected.values()), list(result.values()))
        self.assertEqual(dic, {
            'key': 'value',
            'key2': 'value'
        })

    def test_insert_obj_at__return_obj_as_last_key__when_pos_is_gt_size(self):
        # given
        dic = {
            'key': 'value',
            'key2': 'value'
        }
        obj = {'$id': 'id'}

        # when
        idic = ImmutableDict(dic)
        result = idic.insert_obj_at(obj, 5)

        # then
        expected = OrderedDict({
            'key': 'value',
            'key2': 'value',
            '$id': 'id'
        })
        self.assertEqual(list(expected.keys()), list(result.keys()))
        self.assertEqual(list(expected.values()), list(result.values()))
        self.assertEqual(dic, {
            'key': 'value',
            'key2': 'value'
        })

    def test_insert_obj_at__insert_obj_at_the_end__when_pos_eq_size(self):
        # given
        dic = {
            'key': 'value',
            'key2': 'value'
        }
        obj = {'$id': 'id'}

        # when
        idic = ImmutableDict(dic)
        result = idic.insert_obj_at(obj, 2)

        # then
        expected = OrderedDict({
            'key': 'value',
            'key2': 'value',
            '$id': 'id'
        })

        self.assertEqual(list(expected.keys()), list(result.keys()))
        self.assertEqual(list(expected.values()), list(result.values()))
        self.assertEqual(dic, {
            'key': 'value',
            'key2': 'value'
        })

    def test_insert_obj_at__insert_obj_at_the_top__when_pos_abs_val_gt_size(self):
        # given
        dic = {
            'key': 'value',
            'key2': 'value'
        }
        obj = {'$id': 'id'}

        # when
        idic = ImmutableDict(dic)
        result = idic.insert_obj_at(obj, -3)

        # then
        expected = OrderedDict({
            '$id': 'id',
            'key': 'value',
            'key2': 'value'
        })
        self.assertEqual(list(expected.keys()), list(result.keys()))
        self.assertEqual(list(expected.values()), list(result.values()))
        self.assertEqual(dic, {
            'key': 'value',
            'key2': 'value'
        })

    def test_insert_obj_at__insert_obj_at_the_top__when_pos_abs_val_eq_size(self):
        # given
        dic = {
            'key': 'value',
            'key2': 'value'
        }
        obj = {'$id': 'id'}

        # when
        idic = ImmutableDict(dic)
        result = idic.insert_obj_at(obj, -2)

        # then
        expected = OrderedDict({
            '$id': 'id',
            'key': 'value',
            'key2': 'value'
        })
        self.assertEqual(list(expected.keys()), list(result.keys()))
        self.assertEqual(list(expected.values()), list(result.values()))
        self.assertEqual(dic, {
            'key': 'value',
            'key2': 'value'
        })

    def test_insert_obj_at__insert_obj_after_elem_at_pos_from_end__when_pos_abs_val_lt_size(self):
        # given
        dic = {
            'key': 'value',
            'key2': 'value',
            'key3': 'value'
        }

        obj = {'$id': 'id'}

        # when
        idic = ImmutableDict(dic)
        result = idic.insert_obj_at(obj, -2)

        # then
        expected = OrderedDict({
            'key': 'value',
            '$id': 'id',
            'key2': 'value',  # -2
            'key3': 'value'   # -1
        })
        self.assertEqual(list(expected.keys()), list(result.keys()))
        self.assertEqual(list(expected.values()), list(result.values()))
        self.assertEqual(dic, {
            'key': 'value',
            'key2': 'value',
            'key3': 'value'
        })

    def test_replace_key_with_values__return_obj_with_new_values_and_original_obj_unchanged(self):
        # given
        dic = {'key': 'old_value'}
        changes = {'old_value': 'new_value'}

        # when
        idic = ImmutableDict(dic)
        result = idic.replace_key_with_values('key', changes)

        # then
        self.assertEqual(result, {'key': 'new_value'})
        self.assertEqual(dic, {'key': 'old_value'})

    def test_replace_key_with_values__return_obj_with_new_values__when_many_new_values(self):
        # given
        dic = {
            'key': 'old_value',
            'key2': {
                'key': 'old_value2'
            },
            'key3': 'unchanged'
        }

        changes = {
            'old_value': 'new_value',
            'old_value2': 'new_value2'
        }

        # when
        idic = ImmutableDict(dic)
        result = idic.replace_key_with_values('key', changes)

        # then
        expected = {
            'key': 'new_value',
            'key2': {
                'key': 'new_value2'
            },
            'key3': 'unchanged'
        }

        self.assertEqual(result, expected)

    def test_replace_key_with_values__return_unchanged_obj__when_values_not_found(self):
        # given
        dic = {
            'key': 'unchanged',
            'key2': {
                'key': 'unchanged'
            },
            'key3': 'unchanged'
        }

        changes = {
            'old_value': 'new_value',
            'old_value2': 'new_value2'
        }

        # when
        idic = ImmutableDict(dic)
        result = idic.replace_key_with_values('key', changes)

        # then
        expected = {
            'key': 'unchanged',
            'key2': {
                'key': 'unchanged'
            },
            'key3': 'unchanged'
        }

        self.assertEqual(result, expected)

    def test_replace_key_with_values__return_obj_with_new_values__when_given_nested_obj(self):
        # given
        dic = {
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

        changes = {
            'value': 'new_value',
            'value2': 'new_value2',
            'value3': 'new_value3',
            'value4': 'new_value4',
            'value5': 'new_value5'
        }

        # when
        idic = ImmutableDict(dic)
        result = idic.replace_key_with_values('ref', changes)

        # then
        expected = {
            'key': {
                'key': {
                    'key': {
                        'key': {
                            'ref': 'new_value'
                        },
                        'ref': 'new_value5'
                    },
                    'ref': 'new_value4'
                },
                'ref': 'new_value3'
            },
            'ref': 'new_value2'
        }

        self.assertEqual(result, expected)

    def test_replace_key_with_values__return_obj_with_new_values__when_given_nested_obj_list(self):
        # given
        dic = {
            'key': [
                {
                    'key': [{
                        'key': [{
                            'ref': 'value'
                        }]
                    }]
                },
                {
                    'key': [{
                        'key': [{
                            'ref': 'value'
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

        changes = {
            'value': 'new_value',
            'value2': 'new_value2',
            'value3': 'new_value3'
        }

        # when
        idic = ImmutableDict(dic)
        result = idic.replace_key_with_values('ref', changes)

        # then
        expected = {
            'key': [
                {
                    'key': [{
                        'key': [{
                            'ref': 'new_value'
                        }]
                    }]
                },
                {
                    'key': [{
                        'key': [{
                            'ref': 'new_value'
                        }]
                    }]
                },
                {
                    'key': [{
                        'key': [{
                            'ref': 'new_value2'
                        }]
                    }]
                },
                {
                    'key': [{
                        'key': [{
                            'ref': 'new_value3'
                        }]
                    }]
                },
                {
                    'key': [{
                        'key': [{
                            'ref': 'new_value3'
                        }]
                    }]
                },
                {
                    'key': [{
                        'key': [{
                            'ref': 'new_value3'
                        }]
                    }]
                },
                {
                    'key': [{
                        'key': [{
                            'ref': 'new_value3'
                        }]
                    }]
                }
            ]
        }

        self.assertEqual(result, expected)




