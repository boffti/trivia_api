import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flaskr import create_app
from models import setup_db, Question, Category
import random
import math
import string

load_dotenv()

QUESTIONS_PER_PAGE = 10


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_user = os.getenv('DB_USER')
        self.database_password = os.getenv('DB_PASSWORD')
        self.database_path = "postgres://{}:{}@{}/{}".format(
            self.database_user, self.database_password,
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': self.random_string(50),
            'answer': self.random_string(10),
            'difficulty': self.random_int(1, 5),
            'category': self.random_int(1, 5)
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_get_questions_by_category(self):
        categories = Category.query.all()

        for category in categories:
            res = self.client().get(f'/categories/{ category.id }/questions')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertTrue(len(data['questions']))
            self.assertTrue(data['total_questions'])
            self.assertTrue(data['current_category'])

    def test_404_get_response_for_invalid_category(self):
        total_categories = math.ceil(len(Category.query.all()))
        category_id = random.randint(
            total_categories + 1, total_categories**total_categories)
        res = self.client().get(f'/categories/{ category_id }')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_404_get_questions_for_invalid_page(self):
        total_pages = math.ceil(len(Question.query.all() * QUESTIONS_PER_PAGE))
        page = random.randint(total_pages, total_pages**total_pages)
        res = self.client().get(f'/questions?page={ page }')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_404_get_questions_for_invalid_category(self):
        total_categories = math.ceil(len(Category.query.all()))
        category_id = random.randint(
            total_categories + 1, total_categories**total_categories)
        res = self.client().get(f'/categories/{ category_id }/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz(self):
        new_quiz_round = {'previous_questions': [],
                          'quiz_category': {'type': 'Science', 'id': 1}}

        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_play_quiz_bad_request(self):
        new_quiz_round = {'previous_questions_abc': [],
                          'quiz_category_abc': {'type': 'Science', 'id': 1}}

        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])

    def test_add_new_question(self):
        old_question_count = len(Question.query.all())

        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        new_question_count = len(Question.query.all())

        self.assertEqual(new_question_count, old_question_count + 1)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_422_add_question(self):
        question = {
            'question': self.random_string(50),
            'answer': self.random_string(10),
            'category': 1,
            'difficulty': self.random_string(5)
        }
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "unprocessable")

    def test_search_question(self):
        search = {'searchTerm': 'first'}
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertFalse(data['current_category'])

    def test_404_search_question(self):
        search = {'searchTerm': ''}
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data['message'], 'resource not found')

    def test_question_delete(self):
        first_record = Question.query.first()
        res = self.client().delete(f'/questions/{ first_record.id }')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], first_record.id)

    def test_404_question_delete(self):
        res = self.client().delete(f'/questions/{ self.random_string(2) }')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def random_string(self, n):
        return ''.join(random.choices(string.ascii_uppercase, k=n))

    def random_int(self, m, n):
        return random.randint(m, n)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
