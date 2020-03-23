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
# Get list of all drinks via GET
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

# Get drink details via GET, with required authorization
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

# Create a new drink via POST, with required authorization
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drink(jwt):
    try:
      req_data = request.get_json()
      new_title = req_data.get('title', None)
      new_recipe = req_data.get('recipe', None)
      new_drink = Drink(
        title = new_title,
        recipe = json.dumps([new_recipe])
      )
      new_drink.insert()
      return jsonify({
          'success':True,
          'drinks': [new_drink.long()]
      })
    except:
      db.session.rollback()
      abort(422)

# Modify a given drink via PATCH using drink ID, with required authorization
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt,id):
    try:
      drink = Drink.query.filter(Drink.id == id).one_or_none()
      if drink == None:
          abort(404)
      req_data = request.get_json()
      new_title = req_data.get('title', None)
      new_recipe = req_data.get('recipe', None)
      if new_title:
        drink.title = new_title
      if new_recipe:
        drink.recipe = json.dumps([new_recipe])
      drink.update()
      return jsonify({
          'success':True,
          'drinks': [drink.long()]
      })
    except:
      db.session.rollback()
      abort(422)

# Delete a given drink via DELETE using drink ID, with required authorization
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt,id):
    try:
      req_data = request.get_json()
      drink = Drink.query.filter(Drink.id == id).one_or_none()
      if drink == None:
          abort(404)
      drink.delete()
      return jsonify({
          'success':True,
          'delete': id
      })
    except:
      db.session.rollback()
      abort(422)

## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "Unprocessable"
                    }), 422

@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Resource not found"
                    }), 404

@app.errorhandler(AuthError)
def authorizationerror(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "Authorization error"
                    }), 401