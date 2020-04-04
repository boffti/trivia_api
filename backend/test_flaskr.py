import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flaskr import create_app
from models import setup_db, Question, Category
import random
import math

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
        self.database_path = "postgres://{}:{}@{}/{}".format(self.database_user, self.database_password,'localhost:5432', self.database_name)
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
        category_id = random.randint(total_categories + 1, total_categories**total_categories)
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
        category_id = random.randint(total_categories + 1, total_categories**total_categories)
        res = self.client().get(f'/categories/{ category_id }/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()