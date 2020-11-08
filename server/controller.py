import os
import clearbit
from flask import abort
from sqlalchemy import func, desc, exc, or_
from pyhunter import PyHunter
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity, decode_token)
from server.jwt.jwt_util import (
    add_token_to_database,
    revoke_token
)

from server import db
from server.models import User, Recipe, Ingredient, recipe_ing

hunter = PyHunter(os.environ.get('HUNTER_KEY'))
clearbit.key = os.environ.get('CLEARBIT_KEY')


def check_email(email):
    check_email = hunter.email_verifier(email)

    if check_email['result'] == 'undeliverable':
        abort(400, 'Invalid email')

    response = clearbit.Person.find(email=email)

    return {
        'first_name': response['name']['givenName'],
        'last_name': response['name']['familyName']
    }


def register_user(user_info):
    keys = list(user_info.keys())

    if (
        'email' not in keys or
        'first_name' not in keys or
        'last_name' not in keys
    ):
        abort(400, 'Invalid request')

    new_user = User(
        email=user_info['email'],
        first_name=user_info['first_name'],
        last_name=user_info['last_name']
    )
    new_user.set_password(user_info['password'])

    try:
        db.session.add(new_user)
        db.session.commit()
    except exc.IntegrityError:
        abort(400, 'User already exists')
    except exc.SQLAlchemyError:
        abort(500, 'Internal server error')

    return new_user


def login(user_info):
    keys = list(user_info.keys())

    if 'email' not in keys or 'password' not in keys:
        abort(400, 'Invalid request')

    user = User.query.filter_by(email=user_info['email']).first()

    if not user:
        abort(401, 'User does not exist')

    if not user.check_password(user_info['password']):
        abort(403, 'Invalid credentials')

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    add_token_to_database(access_token)
    add_token_to_database(refresh_token)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def logout(token_id):
    user_identity = get_jwt_identity()
    token_id = token_id.split(' ', 1)[1]
    token_id = decode_token(token_id)['jti']

    try:
        revoke_token(token_id, user_identity)
        return 'Logout successful'
    except:
        abort(404, 'Logout unsuccesful')


def add_ingredient(name):
    if not name:
        abort(400, 'Ingredient name not provided')

    new_ingredient = Ingredient(name=name)

    try:
        db.session.add(new_ingredient)
        db.session.commit()
    except exc.SQLAlchemyError:
        abort(500, 'Internal server error')

    return new_ingredient


def add_recipe(recipe_info):
    ingredient_list = []

    if 'ingredients' in list(recipe_info.keys()):
        for ing in recipe_info['ingredients']:
            instance = db.session.query(Ingredient).filter(
                Ingredient.name == ing).first()
            if instance:
                ingredient_list.append(instance)
            else:
                ingredient_list.append(add_ingredient(ing))

    try:
        new_recipe = Recipe(
            name=recipe_info['name'],
            preparation=recipe_info['preparation'],
            ingredients=ingredient_list,
            user_id=recipe_info['user_id'],
            num_of_ingredients=len(ingredient_list)
        )
        db.session.add(new_recipe)
        db.session.commit()
    except exc.DataError:
        abort(400, 'Invalid user')
    except exc.SQLAlchemyError:
        abort(500, 'Internal server error')

    return new_recipe


def get_all_recipes():
    return db.session.query(Recipe).all()


def rate_recipe(data, recipe_id):
    keys = list(data.keys())

    if 'rating' not in keys or 'user_id' not in keys or not recipe_id:
        abort(400, 'Invalid request')

    user_rating = int(data['rating'])
    if user_rating > 5 or user_rating < 1:
        abort(400, 'Rating out of range')

    try:
        recipe = db.session.query(Recipe).filter(
            Recipe.id == recipe_id).first()
    except exc.DataError:
        abort(400, 'Recipe not found')

    if recipe.user_id == data['user_id']:
        abort(400, 'Users cannot rate their own recipes')

    recipe.rating = (
        (recipe.rating * recipe.num_of_ratings + user_rating) /
        (recipe.num_of_ratings + 1)
    )
    recipe.num_of_ratings += 1

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        abort(500, 'Internal server error')

    return recipe


def get_user_recipes(user_id):
    try:
        recipes = db.session.query(Recipe).filter(
            Recipe.user_id == user_id).all()
    except exc.DataError:
        abort(400, 'Invalid user')
    except exc.SQLAlchemyError:
        abort(500, 'Internal server error')

    return recipes


def get_top_five_ing():
    try:
        most_used_ing = db.session \
            .query(Ingredient) \
            .join(Ingredient.recipes) \
            .group_by(Ingredient.id) \
            .order_by(func.count().desc()) \
            .limit(5) \
            .all()
    except exc.SQLAlchemyError:
        abort(500, 'Internal server error')

    return most_used_ing


def filter_recipes():
    try:
        num_ing = db.session \
            .query(func.count(recipe_ing.c.recipe_id).label('qty')) \
            .group_by(recipe_ing.c.recipe_id) \
            .order_by(desc('qty')) \
            .all()
        arr = [
            Recipe.num_of_ingredients == num_ing[0],
            Recipe.num_of_ingredients == num_ing[-1]
        ]
        recipes = db.session \
            .query(Recipe) \
            .filter(or_(*arr)) \
            .order_by(desc(Recipe.num_of_ingredients)) \
            .all()
    except exc.SQLAlchemyError:
        abort(500, 'Internal server error')

    return recipes


def search_recipes(args):
    arr = []
    keys = list(args.keys())

    if 'name' in keys:
        arr.append(Recipe.name.contains(args['name']))
    if 'text' in keys:
        arr.append(Recipe.preparation.contains(args['text']))
    if 'ingredients' in keys:
        arr.append(or_(
            *[Ingredient.name.contains(ingredient)
              for ingredient in args['ingredients'].split(',')]
        ))

    try:
        recipes = db.session.query(Recipe).join(Recipe.ingredients).filter(
            or_(*arr)).all()
    except exc.SQLAlchemyError:
        abort(500, 'Internal server error')

    return recipes
