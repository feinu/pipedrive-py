import unittest
from unittest import TestCase
from schematics.exceptions import ValidationError
from pipedrive import Deal, User, dict_to_model
from .utils import get_test_data


class DealModelTest(TestCase):
    def test_required(self):
        deal = Deal()
        self.assertRaises(ValidationError, deal.validate, [])

    def test_title_only(self):
        deal = Deal(raw_data={'title': 'Hello!'})
        self.assertIsNone(deal.validate())

    def test_nested_user(self):
        for json in ['deal-detail.json', 'deal-detail-numeric-user-id.json']:
            data = get_test_data(json)
            model = dict_to_model(data, Deal)
            self.assertTrue(isinstance(model.user, User))


if __name__ == '__main__':
    unittest.main()
