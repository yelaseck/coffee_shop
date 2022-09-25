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
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)

    print(drinks)

    drink = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drink
    }), 200


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
def get_drinks_details(f):
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)

    drink = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drink
    }), 200

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
def new_drink(f):
    data = request.get_json()
    
    if data == None:
        abort(404)

    title = data.get('title', '')
    recipe = data.get('recipe', [])
    if len(title) < 1 or len(recipe) < 1:
        abort(422)

    drink_list = Drink.query.all()
    for drink in drink_list:
        print(drink.short())
        if drink.short()['title'] == title :
            abort(422)

    print("________________________data___________________________")
    print(data)
    print(title)
    print(recipe)
    try:
        drink = Drink(
            title=title, 
            recipe=json.dumps([recipe]) #'[{"name": "water", "color": "blue", "parts": 1}]'
        )
        drink.insert()
    except:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


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
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(f, drink_id):

    if drink_id == 0:
        abort(422)

    try:
        drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if not drink:
            abort(404)
        data = request.get_json()
        new_title = data.get('title', None)
        print("________________________new_title___________________________")
        print(new_title)
        if len(new_title) < 1:
            abort(404)
        drink.title = new_title
        drink.update()
        
    except:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


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
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(f, drink_id):
    if drink_id == 0:
        abort(422)

    try:
        drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if not drink:
            abort(404)

        drink.delete()
        
    except:
        abort(422)

    return jsonify({
        'success': True,
        'delete': drink_id
    }), 200


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
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
