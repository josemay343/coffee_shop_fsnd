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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def drinks():
    try:
        drinks = list(map(Drink.short, Drink.query.all()))

        return jsonify({
            'success': True,
            'drinks': [drinks]
        })
    except:
        abort(400)
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        drinks_long = [drinks.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_long
        }), 200
    except:
        abort(400)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    drink_data = request.get_json()
    if 'title' and 'recipe' not in drink_data:
        abort(422)
    title = drink_data['title']
    recipe = json.dumps(drink_data['recipe'])
    new_drink = Drink(title=title, recipe=recipe)
    new_drink.insert()
    return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    })
    # try:
    #     if request.data:
    #         new_drink_data = json.loads(request.data.decode('utf-8'))
    #         new_drink = Drink(title=new_drink_data['title'], recipe=json.dumps(new_drink_data['recipe']))
    #         Drink.insert(new_drink)
    #         drinks = list(map(Drink.long, Drink.query.all()))
    #         return jsonify({
    #             'success': True,
    #             'drinks': [drinks]
    #             }), 200
    # except:
    #     abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(token, drink_id):
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')

    drink = Drink.query.filter(Drink.id == drink_id).one()

    if drink is None:
        abort(404)
    try:
        if title:
            drink.title = title
        if recipe:
            drink.recipe = json.dumps(recipe)
        
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    
    except:
        abort(400)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one()
        if drink is None:
            abort(404)
        else:
            drink.delete()
            return jsonify({
                'status_code': 200,
                'success': True,
                'drink': [drink.id]
            }), 200
    except:
        abort(422)

## Error Handling
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
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def hanle_auth_error(error):
    print(error)
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response