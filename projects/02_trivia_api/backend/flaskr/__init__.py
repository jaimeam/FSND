import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql import func

from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  # CORS Headers 
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,PUT,POST,DELETE,OPTIONS')
      return response

  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = [c.type for c in Category.query.all()]
    return jsonify({
      'success':True,
      'categories':categories
    })

  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    questions = [q.format() for q in Question.query.all()]
    categories = [c.type for c in Category.query.all()]
    return jsonify({
      'success':True,
      'questions':questions[start:end],
      'total_questions':len(questions),
      'categories':categories
    })

  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
      error = False
      try:
          Question.query.filter_by(id=question_id).delete()
          db.session.commit()
      except:
          error = True
          db.session.rollback()
      finally:
          db.session.close()
      return jsonify({ 'success': True })

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
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()

    return jsonify({ 'success': True })

  @app.route('/questions/search', methods=['POST'])
  def search_question():
    search_term = request.get_json()['searchTerm']
    question_matches_query = Question.query.filter(func.lower(Question.question).contains(search_term.lower())).all()
    questions = [q.format() for q in question_matches_query]
    categories = [c.type for c in Category.query.all()]

    return jsonify({
      'success':True,
      'questions':questions,
      'total_questions':len(questions),
      'currentCategory':categories[0]
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    