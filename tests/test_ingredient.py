from werkzeug.exceptions import BadRequest

from server import server
from server.controller import add_ingredient
from tests.base import BaseUnitTest


class IngredientUnitTest(BaseUnitTest):

    def test_valid_add_ingredient(self):
        with server.app_context():
            ing = add_ingredient('Onion')
            self.assertEqual(ing.name, 'Onion')

    def test_invalid_add_ingredient(self):
        with server.app_context():
            self.assertRaises(BadRequest, add_ingredient, '')
            self.assertRaises(BadRequest, add_ingredient, None)
