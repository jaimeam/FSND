import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from jose import jwt
import logging

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

logging.basicConfig(filename='test.log',level=logging.DEBUG)

## ROUTES
@app.route('/drinks', methods=['GET'])
def show_drinks():
    try:
        drinks = [drink.short() for drink in Drink.query.all()]
        return jsonify({
            'success':True,
            'drinks':drinks
        })
    except:
        abort (404)
    
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def show_drinks_detail(jwt):
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        logging.debug(drinks)
        return jsonify({
            'success':True,
            'drinks':drinks
        })
    except:
        abort (404)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drink(jwt):
    try:
      req_data = request.get_json()
      logging.debug(req_data)
      new_drink = Drink(
        title = req_data['title'],
        recipe = json.dumps(req_data['recipe'])
      )
      logging.debug(new_drink)
      new_drink.insert()
      db.session.close()
      return jsonify({
          'success':True,
          'drinks': new_drink.long()
      })
    except:
      db.session.rollback()
      db.session.close()
      abort(422)

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

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
