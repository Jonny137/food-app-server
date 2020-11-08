from flask import request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from server import server, jwt
from server.controller import (register_user, add_recipe, get_all_recipes,
                               rate_recipe, get_user_recipes, get_top_five_ing,
                               check_email, login, logout, filter_recipes,
                               search_recipes)

from server.jwt.jwt_util import is_token_revoked


@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


@server.route('/user/check/<email>')
def check_given_email(email):
    return check_email(email)


@server.route('/user/register', methods=['POST'])
def add_new_user():
    if request.is_json:
        data = request.get_json()
        result = register_user(data)

        new_user = {
            'id': result.id,
            'email': result.email,
            'first_name': result.first_name,
            'last_name': result.last_name
        }

        return {'message': new_user}


@server.route('/login', methods=['POST'])
def user_login():
    if request.is_json:
        data = request.get_json()
        token = login(data)

        return {'message': token}


@server.route('/logout', methods=['PUT'])
@jwt_required
def user_logout():
    token_id = request.headers.get('Authorization')
    result = logout(token_id)

    return {'message': result}


@server.route('/recipe', methods=['POST'])
def add_new_recipe():
    if request.is_json:
        data = request.get_json()
        result = add_recipe(data)

        return {'message': f'{result.name} created succesfully'}


@server.route('/recipe/<user_id>', methods=['GET'])
@jwt_required
def user_recipes(user_id):
    current_user = get_jwt_identity()

    if current_user != user_id:
        abort(401, 'Unauthorized')

    result = get_user_recipes(user_id)
    result = [
        {
            'name': recipe.name,
            'preparation': recipe.preparation,
            'rating': recipe.rating,
            'num_of_ratings': recipe.num_of_ratings,
            'num_of_ingredients': recipe.num_of_ingredients,
            'ingredients': [ing.name for ing in recipe.ingredients]
        } for recipe in result]

    return {'message': result}


@server.route('/recipe/all')
def all_recipes():
    recipes = get_all_recipes()
    result = [
        {
            'name': recipe.name,
            'preparation': recipe.preparation,
            'rating': recipe.rating,
            'num_of_ratings': recipe.num_of_ratings,
            'num_of_ingredients': recipe.num_of_ingredients,
            'ingredients': [ing.name for ing in recipe.ingredients]
        } for recipe in recipes]

    return {'message': result}


@server.route('/rate/<recipe_id>', methods=['PATCH'])
@jwt_required
def rate(recipe_id):
    if request.is_json:
        data = request.get_json()
        result = rate_recipe(data, recipe_id)

        return {'message': f'{result.name} rated succesfully'}
    else:
        return {'error': 'Unable to rate recipe'}


@server.route('/ingredients')
@jwt_required
def top_five_ing():
    result = get_top_five_ing()
    result = [ing.name for ing in result]

    return {'message': result}


@server.route('/recipe/filter')
@jwt_required
def get_filter_recipes():
    recipes = filter_recipes()
    result = [
        {
            'name': recipe.name,
            'preparation': recipe.preparation,
            'rating': recipe.rating,
            'num_of_ratings': recipe.num_of_ratings,
            'num_of_ingredients': recipe.num_of_ingredients,
            'ingredients': [ing.name for ing in recipe.ingredients]
        } for recipe in recipes]

    return {'message': result}


@server.route('/recipe/search')
@jwt_required
def get_search_recipes():

    recipes = search_recipes(request.args)
    result = [
        {
            'name': recipe.name,
            'preparation': recipe.preparation,
            'rating': recipe.rating,
            'num_of_ratings': recipe.num_of_ratings,
            'num_of_ingredients': recipe.num_of_ingredients,
            'ingredients': [ing.name for ing in recipe.ingredients]
        } for recipe in recipes]

    return {'message': result}
