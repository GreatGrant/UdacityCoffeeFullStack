# from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# https://fscoffee.us.auth0.com/authorize?audience=drink&response_type=token&client_id=LoN4MSn2sRfciWJ1TdW9jAxaLF4gcwzq&redirect_uri=https://127.0.0.1:8080/login-result

# https://fscoffee.us.auth0.com/v2/logout?%20client_id=LoN4MSn2sRfciWJ1TdW9jAxaLF4gcwzq&%20returnTo=https://127.0.0.1:8080/logout

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json
    {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks")
def get_all_drinks():
    try:
        drinks_list = Drink.query.order_by(Drink.id).all()
        drinks = []
        for drink in drinks_list:
            drinks.append(drink.short())

        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except Exception as e:
        print(e)
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json
    {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def retrieve_drinks_details(payload):
    try:
        drinks_list = Drink.query.all()
        drinks = []

        for drink in drinks_list:
            drinks.append(drink.long())
        return jsonify({"success": True, "drinks": drinks})
    except Exception as e:
        print(e)
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json
    {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@requires_auth("post:drinks")
@app.route("/drinks", methods=["POST"])
def post_drinks():
    body = request.get_json()
    recipe = body.get('recipe', None)
    title = body.get('title', None)
    if title is None or recipe is None:
        abort(422)
    else:
        title = body['title']
        recipe = json.dumps(body['recipe'])

    try:
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
        return jsonify({
            'success': True,
            'drinks:': new_drink.long()
        })
    except Exception as e:
        print(e)
        abort(404)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json
    {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@requires_auth("patch:drinks")
@app.route("/drinks/<int:id>", methods=["PATCH"])
def edit_drink(id):
    drink_to_update = Drink.query.get(id)
    body = request.get_json()
    recipe = body.get('recipe', None)
    title = body.get('title', None)

    try:
        if drink_to_update is None:
            abort(404)
        if title:
            drink_to_update.title = title

        if recipe:
            setattr(drink_to_update, 'recipe', json.dumps(body['recipe']))

        drink_to_update.update()
        return jsonify({
            'success': True,
            'drinks': [drink_to_update.long()]
        })

    except SystemError:
        abort(404)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json
    {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@requires_auth('delete:drinks')
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
def delete_drink(payload, drink_id):
    try:
        drink_to_delete = Drink.query.filter(
            Drink.id == drink_id).one_or_none()

        if drink_to_delete is None:
            abort(404)

        drink_to_delete.delete()

        return jsonify({
            'success': True,
            'delete': drink_to_delete.id
        })
    except SystemError:
        abort(404)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404


@app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allowed"
    }), 405


@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error['description']
    }), auth_error.status_code
