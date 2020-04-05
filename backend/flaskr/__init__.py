import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_items(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    items = [item.format() for item in selection]
    current_items = items[start:end]

    return current_items


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {cat.id: cat.type for cat in categories}
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        formatted_questions = paginate_items(request, questions)
        categories = Category.query.order_by(Category.type).all()

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'current_category': None,
            'categories': {cat.id: cat.type for cat in categories}
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def add_question():
        try:
            body = request.get_json()
            question = body.get('question')
            answer = body.get('answer')
            difficulty = body.get('difficulty')
            category = body.get('category')

            if ((question is None) or (question is None) or
                    (question is None) or (question is None)):
                abort(400)

            question = Question(question=question, answer=answer,
                                difficulty=difficulty, category=category)
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id
            })
        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            searchTerm = request.get_json().get('searchTerm', None)
            if searchTerm:
                search_result = Question.query.filter(
                    Question.question.ilike(f'%{searchTerm}%')).all()
                return jsonify({
                    'success': True,
                    'questions': paginate_items(request, search_result),
                    'total_questions': len(search_result),
                    'current_category': None
                })
            else:
                abort(404)
        except:
            abort(404)

    @app.route('/categories/<int:category>/questions', methods=['GET'])
    def get_questions_by_category(category):
        questions = Question.query.filter_by(category=category).all()
        formatted_questions = paginate_items(request, questions)

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'current_category': category,
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            cat = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if cat is None or previous_questions is None:
                abort(400)

            if (cat['id'] == 0):
                q_pool = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                q_pool = Question.query.filter_by(category=cat['id']).filter(
                    Question.id.notin_((previous_questions))).all()

            if len(q_pool) > 0:
                random_question = q_pool[random.randint(
                    0, len(q_pool))].format()
            else:
                random_question = None

            return jsonify({
                'success': True,
                'question': random_question
            })
        except:
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app
