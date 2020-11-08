from werkzeug.exceptions import BadRequest

from server import server
from server.controller import (register_user, add_recipe, get_all_recipes,
                               rate_recipe, get_user_recipes,
                               login)
from tests.base import BaseUnitTest


class RecipeUnitTest(BaseUnitTest):

    def test_valid_add_recipe(self):
        with server.app_context():
            user_data = {
                'email': 'test@user.com',
                'first_name': 'test',
                'last_name': 'Jones',
                'password': 'donkey'
            }

            reg_user = register_user(user_data)

            resp = login({
                'email': user_data['email'],
                'password': user_data['password']
            })

            recipe_info = {
                'name': 'Pork',
                'preparation': 'Everybodys favorite dish',
                'ingredients': ['Pork', 'Oil', 'Seasoning', 'Beer'],
                'user_id': reg_user.id
            }

            resp = add_recipe(recipe_info)

            self.assertEqual(resp.name, recipe_info['name'])
            self.assertEqual(resp.preparation, recipe_info['preparation'])
            self.assertEqual(
                [ing.name for ing in resp.ingredients],
                recipe_info['ingredients']
            )
            self.assertEqual(resp.rating, 0)
            self.assertEqual(resp.num_of_ratings, 0)
            self.assertEqual(
                resp.num_of_ingredients,
                len(recipe_info['ingredients'])
            )

    def test_invalid_add_recipe(self):
        with server.app_context():
            user_data = {
                'email': 'test@user.com',
                'first_name': 'test',
                'last_name': 'Jones',
                'password': 'donkey'
            }

            register_user(user_data)

            login({
                'email': user_data['email'],
                'password': user_data['password']
            })

            self.assertRaises(BadRequest, add_recipe, {
                'name': 'Pork',
                'preparation': 'Everybodys favorite dish',
                'ingredients': ['Pork', 'Oil', 'Seasoning', 'Beer'],
                'user_id': 'this aint my id'
            })

    def test_get_all_recipe(self):
        with server.app_context():
            resp = get_all_recipes()

            self.assertEqual(type(resp), type([]))

    def test_valid_rate_recipe(self):
        with server.app_context():
            user_data_1 = {
                'email': 'mi6@user.com',
                'first_name': 'Ethan',
                'last_name': 'Hunt',
                'password': 'agent'
            }

            user_data_2 = {
                'email': 'blackwidow@user.com',
                'first_name': 'Natasha',
                'last_name': 'Romanov',
                'password': 'avenger'
            }

            reg_user_1 = register_user(user_data_1)
            reg_user_2 = register_user(user_data_2)

            login({
                'email': user_data_1['email'],
                'password': user_data_1['password']
            })

            login({
                'email': user_data_2['email'],
                'password': user_data_2['password']
            })

            recipe_info = {
                'name': 'Pork',
                'preparation': 'Everybodys favorite dish',
                'ingredients': ['Pork', 'Oil', 'Seasoning', 'Beer'],
                'user_id': reg_user_1.id
            }

            recipe = add_recipe(recipe_info)

            self.assertEqual(0, recipe.rating)
            self.assertEqual(0, recipe.num_of_ratings)

            res = rate_recipe({
                'rating': 5,
                'user_id': reg_user_2.id
            }, recipe.id)

            self.assertEqual(recipe.name, res.name)
            self.assertEqual(5, res.rating)
            self.assertEqual(1, res.num_of_ratings)

    def test_own_rate_recipe(self):
        with server.app_context():
            user_data_1 = {
                'email': 'mi6@user.com',
                'first_name': 'Ethan',
                'last_name': 'Hunt',
                'password': 'agent'
            }

            reg_user_1 = register_user(user_data_1)

            login({
                'email': user_data_1['email'],
                'password': user_data_1['password']
            })

            recipe_info = {
                'name': 'Pork',
                'preparation': 'Everybodys favorite dish',
                'ingredients': ['Pork', 'Oil', 'Seasoning', 'Beer'],
                'user_id': reg_user_1.id
            }

            recipe = add_recipe(recipe_info)

            self.assertRaises(BadRequest, rate_recipe, {
                'rating': 5,
                'user_id': reg_user_1.id
            }, recipe.id)

    def test_rate_recipe_bad_recipe_id(self):
        with server.app_context():
            user_data_1 = {
                'email': 'mi6@user.com',
                'first_name': 'Ethan',
                'last_name': 'Hunt',
                'password': 'agent'
            }

            reg_user_1 = register_user(user_data_1)

            login({
                'email': user_data_1['email'],
                'password': user_data_1['password']
            })

            recipe_info = {
                'name': 'Pork',
                'preparation': 'Everybodys favorite dish',
                'ingredients': ['Pork', 'Oil', 'Seasoning', 'Beer'],
                'user_id': reg_user_1.id
            }

            add_recipe(recipe_info)

            self.assertRaises(BadRequest, rate_recipe, {
                'rating': 5,
                'user_id': reg_user_1.id
            }, 'this aint recipe id')

    def test_rate_recipe_invalid_request(self):
        with server.app_context():
            self.assertRaises(BadRequest, rate_recipe, {
                'rating': 5,
                'user_id': 'some id'
            }, None)

    def test_rate_recipe_out_of_range(self):
        with server.app_context():
            user_data_1 = {
                'email': 'mi6@user.com',
                'first_name': 'Ethan',
                'last_name': 'Hunt',
                'password': 'agent'
            }

            reg_user_1 = register_user(user_data_1)

            login({
                'email': user_data_1['email'],
                'password': user_data_1['password']
            })

            recipe_info = {
                'name': 'Pork',
                'preparation': 'Everybodys favorite dish',
                'ingredients': ['Pork', 'Oil', 'Seasoning', 'Beer'],
                'user_id': reg_user_1.id
            }

            recipe = add_recipe(recipe_info)

            self.assertRaises(BadRequest, rate_recipe, {
                'rating': -1,
                'user_id': reg_user_1.id
            }, recipe.id)
            self.assertRaises(BadRequest, rate_recipe, {
                'rating': 9000,
                'user_id': reg_user_1.id
            }, recipe.id)

    def test_get_valid_user_recipes(self):
        with server.app_context():
            user_data_1 = {
                'email': 'mi6@user.com',
                'first_name': 'Ethan',
                'last_name': 'Hunt',
                'password': 'agent'
            }

            reg_user_1 = register_user(user_data_1)

            login({
                'email': user_data_1['email'],
                'password': user_data_1['password']
            })

            recipe_info = {
                'name': 'Pork',
                'preparation': 'Everybodys favorite dish',
                'ingredients': ['Pork', 'Oil', 'Seasoning', 'Beer'],
                'user_id': reg_user_1.id
            }

            add_recipe(recipe_info)
            add_recipe(recipe_info)

            resp = get_user_recipes(reg_user_1.id)

            self.assertEqual(2, len(resp))

    def test_get_invalid_user_recipes(self):
        with server.app_context():
            user_data_1 = {
                'email': 'mi6@user.com',
                'first_name': 'Ethan',
                'last_name': 'Hunt',
                'password': 'agent'
            }

            register_user(user_data_1)

            login({
                'email': user_data_1['email'],
                'password': user_data_1['password']
            })

            self.assertRaises(
                BadRequest, get_user_recipes,
                'this aint valid id'
            )
