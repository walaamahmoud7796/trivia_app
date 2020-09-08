import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate(request,selection):
  page = request.args.get('page',1,type = int)
  start = (page-1)* QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE 
  questions = [question.format() for question in selection]
  return questions[start:end]




def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  
  # CORS(app)
  cors = CORS(app,resources={"*":{"origin":"*"}})
 

  @app.after_request 
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  
  @app.route('/categories',methods = ['GET'])
  def get_categories():
    categs = Category.query.all()
    if categs is None:
      abort(404)
    else:
      categories = [category.format() for category in categs]
      
      return jsonify({
        'categories': categories
      })


  
  @app.route('/questions',methods=['GET'])
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate(request,selection)
    categs = Category.query.all()
    categories = [category.format() for category in categs]
   
    return jsonify({
      'questions':current_questions,
      'categories':categories,
      'total_questions':len(selection),
      'current_category':categories

    })
 
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
    
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      else:
        try:
          question.delete()
          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate(request,selection)
          return jsonify({
            'success':True,
            'questions':current_questions,
            'total_questions':len(Question.query.all()),
            'current_category':None


          })
        except Exception as e:
          abort(422)

  

  @app.route('/questions',methods= ['POST'])
  def add_or_search_question():
    body = request.get_json()
    new_question = body.get('question',None)
    answer = body.get('answer',None)
    difficulty = body.get('difficulty',None)
    category = body.get('category',None)
    search = body.get('searchTerm',None)
    if search:

      selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).all()
      if len(selection)==0:
        abort(404)
      else:
        current_questions = paginate(request,selection)
        return jsonify({
          'success':True,
          'questions':current_questions,
          'total_questions':len(selection),
          'current_category':category
        })   
    else:
        if None in [new_question,answer,difficulty,category]:
          abort(422)
        else:
          try:
            question = Question(question= new_question,answer = answer , difficulty = difficulty,category = category)
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate(request,selection)
            categs = Category.query.all()

            categories = [category.format() for category in categs]

            return jsonify(
              {'success':True,
              'questions':current_questions,
              'total_questions':len(Question.query.all()),
              'current_category':category,
              'categories': categories
              })
          except Exception as e:
            abort(422)
 
  @app.route('/categories/<int:category_id>/questions',methods=['GET'])
  def get_questions_per_category(category_id):
    try:
      selection = Question.query.order_by(Question.id).filter(Question.category== category_id).all()
      current_questions = paginate(request,selection)

      return jsonify({
        'success':True,
        'questions': current_questions,
        'totalQuestions':len(selection),
        'currentCategory':category_id
      })
    except:
      abort(404)
  
  @app.route('/quizzes',methods=['POST'])
  def quiz():
    try:
      body = request.get_json()
      previous_questions = body.get('previous_questions',[])
      quiz_category = body.get('quiz_category',None)
     

      if quiz_category['id']==0:
          rand_category = random.randint(1,5)
          question = Question.query.filter(Question.category == rand_category,Question.id.notin_(previous_questions)).first()
      else:    
          question = Question.query.filter(Question.category == quiz_category['id'],Question.id.notin_(previous_questions)).first()

      
      
      return jsonify({"question":question.format() if question else None})
    except Exception as e:
      abort(422)
  
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success':False,
      'error':422,
      "message":"unprocessable"
    }),422

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success':False,
      'error':404,
      'message':"resource not found"
    }),404
  
  return app

    