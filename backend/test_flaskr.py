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
        self.database_path = "postgresql://{}@{}/{}".format('mohamed', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Who is Mohamed?',
            'answer': 'Ther greatest man on the universe',
            'category': 4,
            'difficulty': 1
        }

        self.new_question_not_valid = {
            'answer': 'Ther greatest man on the universe',
            'category': 4,
            'difficulty': 1
        }

        self.quizze = {
            'previous_questions': [10, 11],
            'quiz_category': 6,
        }

        self.quizze_not_valid = {
            'previous_questions': None,
            'quiz_category': 6,
        }
        
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
    DONE
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))
    
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['currentCategory'])
        self.assertTrue(len(data['questions']))

    q_id_delete = 25
    def test_delete_question(self):
        res = self.client().delete('/questions/{}'.format(self.q_id_delete))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == self.q_id_delete).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], self.q_id_delete)
        self.assertEqual(question, None)
    
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
    
    def test_get_paginated_questions_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])
        self.assertTrue(len(data['questions']))

    def test_get_quizze(self):
        res = self.client().post('/quizzes', json=self.quizze)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['quiz_category'])
        self.assertEqual(data['question'], None)
    
    def test_get_search_q(self):
        res = self.client().get('/questions?q=mohamed')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['currentCategory'])
        self.assertTrue(len(data['questions']))
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/categories?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_404_sent_requesting_beyond_valid_page_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_422_if_questions_does_not_created(self):
        res = self.client().post('/questions', json=self.new_question_not_valid)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable') 
    
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable') 
    
    def test_422_if_quizzes_not_valid(self):
        res = self.client().post('/quizzes', json=self.quizze_not_valid)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable') 
    
    def test_404_if_category_does_not_have_questions(self):
        res = self.client().get('/categories/10000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()