import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from jose import jwt

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

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
      new_drink = Drink(
        title = req_data['title'],
        recipe = json.dumps(req_data['recipe'])
      )
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

@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt,id):
    try:
      req_data = request.get_json()
      drink = Drink.query.filter(Drink.id == id).one_or_none()
      if drink == None:
          abort(404)

      drink.title = req_data['title']
      drink.recipe = json.dumps(req_data['recipe'])
      drink.update()
      db.session.close()
      return jsonify({
          'success':True,
          'drinks': drink.long()
      })
    except:
      db.session.rollback()
      db.session.close()
      abort(422)


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
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt,id):
    try:
      req_data = request.get_json()
      drink = Drink.query.filter(Drink.id == id).one_or_none()
      if drink == None:
          abort(404)
      drink.delete()
      db.session.close()
      return jsonify({
          'success':True,
          'delete': id
      })
    except:
      db.session.rollback()
      db.session.close()
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

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
