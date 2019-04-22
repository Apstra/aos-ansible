from ansible.compat.tests import unittest
from ansible.compat.tests.mock import patch, MagicMock
from ansible.module_utils import basic
from nose.tools import assert_equals
from module_utils.aos import find_resource_item, \
    find_resource_by_name, find_resource_by_id

mock_data = {
    "items": [
        {
            "display_name": "test-one",
            "id": "test-1"
        },
        {
            "display_name": "test-two",
            "id": "test-2"
        }
    ]
}


class TestFindResource(unittest.TestCase):
    def test_find_resource_by_name(self):
        mock_name = 'test-one'
        resp = find_resource_by_name(mock_data, mock_name)

        return_data = {'display_name': 'test-one', 'id': 'test-1'}

        self.assertEqual(resp, return_data)

    def test_find_resource_by_name_not_found(self):
        mock_name = 'test-three'
        resp = find_resource_by_name(mock_data, mock_name)

        self.assertEqual(resp, {})

    def test_find_resource_by_id(self):
        mock_id = 'test-1'
        resp = find_resource_by_id(mock_data, mock_id)

        return_data = {'display_name': 'test-one', 'id': 'test-1'}

        self.assertEqual(resp, return_data)

    def test_find_resource_by_id_not_found(self):
        mock_id = 'test-3'
        resp = find_resource_by_id(mock_data, mock_id)

        self.assertEqual(resp, {})

    @patch('module_utils.aos.aos_get')
    def test_find_resource_item_name(self, test_patch):
        test_patch.return_value = mock_data
        session = {"server": "foo",
                   "token": "bar"}
        endpoint = '/foo'
        resource_name = "test-one"

        resp = find_resource_item(session, endpoint,
                                  resource_name=resource_name)

        return_data = {'display_name': 'test-one', 'id': 'test-1'}

        self.assertEqual(resp, return_data)

    @patch('module_utils.aos.aos_get')
    def test_find_resource_item_id(self, test_patch):
        test_patch.return_value = mock_data
        session = {"server": "foo",
                   "token": "bar"}
        endpoint = '/foo'
        resource_id = "test-1"

        resp = find_resource_item(session, endpoint,
                                  resource_id=resource_id)

        return_data = {'display_name': 'test-one', 'id': 'test-1'}

        self.assertEqual(resp, return_data)

    @patch('module_utils.aos.aos_get')
    def test_find_resource_item_not_found(self, test_patch):
        test_patch.return_value = mock_data
        session = {"server": "foo",
                   "token": "bar"}
        endpoint = '/foo'
        resource_id = "test-3"

        resp = find_resource_item(session, endpoint,
                                  resource_id=resource_id)

        return_data = {}

        self.assertEqual(resp, return_data)
