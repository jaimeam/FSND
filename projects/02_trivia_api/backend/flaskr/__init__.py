import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql import func

from models import db, setup_db, Question, Category

import random

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  # Set up CORS. Allow '*' for origins
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  # Use the after_request decorator to set Access-Control-Allow
  # CORS Headers 
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,PUT,POST,DELETE,OPTIONS')
      return response

  # Get list of categories from database via GET
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = [c.type for c in Category.query.all()]
    
    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success':True,
      'categories':categories
    })

  # Get paginated list of questions from database via GET (max 10 questions per page)
  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    questions = [q.format() for q in Question.query.all()]
    categories = [c.type for c in Category.query.all()]

    if (len(questions) == 0) or (len(questions)<start)or (len(categories) == 0):
      abort(404)

    return jsonify({
      'success':True,
      'questions':questions[start:end],
      'total_questions':len(questions),
      'categories':categories
    })

  # Delete question from database
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
      error = False
      try:
          Question.query.filter_by(id=question_id).delete()
          db.session.commit()
          db.session.close()
          return jsonify({ 'success': True})
      except:
          error = True
          db.session.rollback()
          db.session.close()
          abort(422)
          

  # Create new question in database via POST
  @app.route('/questions', methods=['POST'])
  def create_question():
    error = False
    try:
      req_data = request.get_json()
      new_question = Question(
        question = req_data['question'],
        answer = req_data['answer'],
        difficulty = int(req_data['difficulty']),
        category = int(req_data['category'])
      )
      db.session.add(new_question)
      db.session.commit()
      db.session.close()
      return jsonify({ 'success': True })
    except:
      error = True
      db.session.rollback()
      db.session.close()
      abort(422)
    

  # Search questions which contain search term as substring, case-insensitive, via POST
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    # Check that submitted values are correct
    try:
      search_term = request.get_json()['searchTerm']
    except:
      abort(422)
    question_matches_query = Question.query.filter(func.lower(Question.question).contains(search_term.lower())).all()
    questions = [q.format() for q in question_matches_query]

    return jsonify({
      'success':True,
      'questions':questions,
      'total_questions':len(questions),
    })

  # List questions for a given category via GET
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    #Sum 1 to category id due to bug in front-end which causes category id's to start from 0 instead of 1
    category_id = int(category_id)+1
    questions_c = [q.format() for q in Question.query.filter_by(category=category_id).all()]
    #Substract 1 from category id returned, so category icons are rendered correctly
    for question in questions_c:
      question['category'] = question['category']-1
    return jsonify({
      'success':True,
      'questions':questions_c,
      'total_questions':len(questions_c),
    })

  # Quizz question randomizer which receives previous questions and a given category via POST, and return random new question
  @app.route('/quizzes', methods=['POST'])
  def quizz_question():
    # Receive previous questions as a list of question id's
    previous_questions = request.get_json()['previous_questions']
    # Receive quiz category as a dict {'type': <category_name>, 'id': <category_id>}
    quiz_category = request.get_json()['quiz_category']

    # Check that quiz_category has a field id which can be also an integer
    try:
      int(quiz_category['id'])
    except:
      abort(422)

    # If quiz_category type = click take all categories
    if quiz_category['type'] == 'click':
      questions_c = [q.format() for q in Question.query.all()]
    else:
      quiz_category['id'] = int(quiz_category['id'])+1
      questions_c = [q.format() for q in Question.query.filter_by(category=quiz_category['id']).all()]
    
    if len(questions_c) == 0:
      abort(404)

    # Take only questions which are not in the list of previous questions
    new_questions = list(filter(lambda x: x['id'] not in previous_questions, questions_c))
    
    # Take a random question from the list of new un-asked questions
    next_question = random.choice(new_questions)

    return jsonify({
      'question':next_question
    })
  

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found'
    }), 404
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable'
    }), 422
  
  
  return app

    