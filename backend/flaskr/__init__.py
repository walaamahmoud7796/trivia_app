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
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  # CORS(app)
  cors = CORS(app,resources={"*":{"origin":"*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request 
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
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


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
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
      'current_category':None

    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      else:
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
      print(e)
      abort(422)

  '''
  @TODO:
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

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
      current_questions = paginate(request,selection)
      return jsonify({
        'success':True,
        'questions':current_questions,
        'total_questions':len(selection),
        'current_category':category
      })   
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
        print(e)
        abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
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
  @app.route('/quizzes',methods=['POST'])
  def quiz():
    try:
      body = request.get_json()
      print(body)
      previous_questions = body.get('previous_questions',[])
      quiz_category = body.get('quiz_category',None)
      print(type(quiz_category['id']),quiz_category['id'])
      print(previous_questions)

      if quiz_category['id']==0:
          rand_category = random.randint(1,5)
          question = Question.query.filter(Question.category == rand_category,Question.id.notin_(previous_questions)).first()
      else:    
          question = Question.query.filter(Question.category == quiz_category['id'],Question.id.notin_(previous_questions)).first()

      # question = Question.query.filter(Question.category == quiz_category['id']).first()


      question = question.format()
      return jsonify({"question":question})
    except Exception as e:
      abort(422)
  
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
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

    