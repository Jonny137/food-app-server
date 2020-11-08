
from werkzeug.exceptions import Forbidden, BadRequest, Unauthorized
from unittest.mock import patch

from server import server
from server.models import User
from server.controller import register_user, login, logout
from tests.base import BaseUnitTest


class UserUnitTest(BaseUnitTest):

    def test_password_hashing(self):
        u = User(
            email='john@user.com',
            first_name='John',
            last_name='Jones'
        )
        u.set_password('police')

        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('police'))

    def test_invalid_registration(self):
        user_data = {
            'email': 'john@user.com',
            'last_name': 'Jones',
            'password': 'donkey'
        }

        self.assertRaises(BadRequest, register_user, user_data)

    def test_valid_registration(self):
        user_data = {
            'email': 'user@user.com',
            'first_name': 'test',
            'last_name': 'test',
            'password': 'passing'
        }

        resp = register_user(user_data)
        self.assertEqual(resp.email, user_data['email'])

    def test_duplicate_registration(self):
        user_data = {
            'email': 'john@user.com',
            'first_name': 'John',
            'last_name': 'Jones',
            'password': 'donkey'
        }
        register_user(user_data)
        self.assertRaises(BadRequest, register_user, user_data)

    def test_valid_login(self):
        with server.app_context():
            user_data = {
                'email': 'test@user.com',
                'first_name': 'test',
                'last_name': 'Jones',
                'password': 'donkey'
            }
            register_user(user_data)

            resp = login({
                'email': user_data['email'],
                'password': user_data['password']
            })

            self.assertEqual(
                list(resp.keys()), ['access_token', 'refresh_token'])

    def test_invalid_login(self):
        with server.app_context():
            user_data = {
                'email': 'test@user.com',
                'first_name': 'test',
                'last_name': 'Jones',
                'password': 'donkey'
            }
            register_user(user_data)

            self.assertRaises(BadRequest, login, {
                'password': user_data['password']
            })

    def test_wrong_pass_login(self):
        with server.app_context():
            user_data = {
                'email': 'test@user.com',
                'first_name': 'test',
                'last_name': 'Jones',
                'password': 'donkey'
            }
            register_user(user_data)

            self.assertRaises(Forbidden, login, {
                'email': user_data['email'],
                'password': 'this_aint_my_pass'
            })

    def test_unknown_user_login(self):
        with server.app_context():
            user_data = {
                'email': 'test@user.com',
                'first_name': 'test',
                'last_name': 'Jones',
                'password': 'donkey'
            }

            register_user(user_data)

            self.assertRaises(Unauthorized, login, {
                'email': 'fail@user.com',
                'password': user_data['password']
            })

    @patch('server.controller.get_jwt_identity')
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    def test_valid_logout(self, mock_jwt_required, mock_jwt_identity):
        with server.app_context():
            user_data = {
                'email': 'boogey@user.com',
                'first_name': 'Marc',
                'last_name': 'Feldman',
                'password': 'donkey'
            }

            user = register_user(user_data)
            mock_jwt_identity.return_value = str(user.id)

            resp_1 = login({
                'email': 'boogey@user.com',
                'password': 'donkey'
            })

            logout_creds = 'Bearer ' + str(resp_1['access_token'])
            resp_2 = logout(logout_creds)

            self.assertEqual(resp_2, 'Logout successful')
