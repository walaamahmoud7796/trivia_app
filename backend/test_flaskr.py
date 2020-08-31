import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = "postgres://gubmhgwnolmfcw:ed80bf89a8a919284128e462eee4a2646fefea5be84bd7b0f8738dedaaf01351@ec2-3-223-9-166.compute-1.amazonaws.com:5432/d4vfjr2h0el6ab"

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_search(self):
        response = self.client().post('/questions',json={'search':'egypt'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)

    def test_add_question(self):
     
        response = self.client().post('/questions',json={'question':'What is the capital of Greece','answer':'Athens','difficutly':1,'category':3})
        data = json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        

    
    def test_quiz_all_categories(self):
        questions_response = self.client().get('/questions')
        questions_data = json.loads(questions_response.data)
        # Test all categories
        previous_questions = []
        for i in range(6):
            
            question_response = self.client().post('/quizzes',json={'previous_questions':previous_questions,'quiz_category':{'id':questions_data['questions'][i]['category']}})
            question_data = json.loads(question_response.data)
            print(question_data)
            self.assertNotIn(question_data['question']['id'],previous_questions)
            previous_questions.append(questions_data['questions'][i]['id'])


    def test_quiz_single_category(self):
        questions_response = self.client().get('/categories/2/questions')
        questions_data = json.loads(questions_response.data)
        # Test all categories
        previous_questions = []
        for i in range(len(questions_data)):
            
            question_response = self.client().post('/quizzes',json={'previous_questions':previous_questions,'quiz_category':{'id':questions_data['questions'][i]['category']}})
            question_data = json.loads(question_response.data)
            print(question_data)
            self.assertNotIn(question_data['question']['id'],previous_questions)
            previous_questions.append(questions_data['questions'][i]['id'])
                
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()