import os
import unittest

from dotenv import load_dotenv

# Import individual test classes
from tests.test_user import UserUnitTest
from tests.test_ingredient import IngredientUnitTest
from tests.test_recipe import RecipeUnitTest

# Enable use of os.environ
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
