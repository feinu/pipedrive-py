import unittest
from unittest import TestCase

from pipedrive import PipedriveAPI, BaseResource


class ResourceAccessorAttibute(TestCase):
    def test_registry_does_not_contain(self):
        api = PipedriveAPI('lol')
        with self.assertRaises(AttributeError):
            api.lol

    def test_registry_contains(self):
        BaseResource.API_ACESSOR_NAME = 'sms'
        PipedriveAPI.register_resource(BaseResource)
        api = PipedriveAPI('lol')
        self.assertEqual(BaseResource, api.sms.__class__)


if __name__ == '__main__':
    unittest.main()
