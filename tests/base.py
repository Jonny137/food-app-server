import os
import unittest

from server import server, db


class BaseUnitTest(unittest.TestCase):

    def setUp(self):
        server.config['TESTING'] = True
        server.config['WTF_CSRF_ENABLED'] = False
        server.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'DB_TEST_URI')
        server.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
