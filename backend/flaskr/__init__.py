import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import unittest

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

    #Returns questions in sets of 10. 
def paginate_questions(request, questions):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    question = [question.format() for question in questions]
    question_set = question[start:end]

    return question_set


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)  

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origins", '*')
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,OPTIONS,DELETE")
        return response

   
    @app.route('/')
    def index():
        return 'Welcome to Trivia API'
    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
   
    @app.route("/categories", methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [Category.format() for category in categories]

        return jsonify({
            'success': True, 
            'categories': formatted_categories, 
            'current_category': None, 
        })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

TEST: At this point, when you start the application
you should see questions and categories generated,
ten questions per page and pagination at the bottom of the screen for three pages.
Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        totalQuestions = Question.query.order_by(Question.id).all()
        formatted_questions = paginate_questions(request, totalQuestions)

        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [Category.format() for category in categories]
        
        return jsonify({
            'success': True, 
            'questions': formatted_questions, 
            'total_questions': len(formatted_questions), 
            'current_category': None, 
            'all_categories': formatted_categories,             
        })



    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

TEST: When you click the trash icon next to a question, the question will be removed.
This removal will persist in the database and when you refresh the page.
"""
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(q_id):
        try:
            question = Question.query.filter(Question.id == q_id).one_or_none()

            question.delete()
            questions = Question.query.order_by(Question.id).all()
            question_set = paginate_questions(request, questions)

            return jsonify({
                'success': True, 
                'deleted': q_id,
            })
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

TEST: When you submit a question on the "Add" tab,
the form will clear and the question will appear at the end of the last page
of the questions list in the "List" tab.
"""
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

TEST: Search by any phrase. The questions list will update to include
only question that include that string within their question.
Try using the word "title" to start.
"""
    @app.route('/questions/create', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_rating = body.get('difficulty', None)
        search = body.get('search', None)

        try:
            if search:
                questions = Question.query.order(Question.id).filter(
                    Question.title.ilike("%{}%".format(search))
                )
                question_set = paginate_questions(request, questions)

                return jsonify({
                    'success': True, 
                    'books': question_set, 
                    'all_questions': len(questions.all()), 
                })
            else: 
                entry = Question(question=new_question, answer=new_answer, 
                                category=new_category, difficulty=new_rating)
                entry.insert()

                questions = Question.query.order_by(Question.id).all()
                question_set = paginate_questions(request, questions)

                return jsonify ({
                    'success': True, 
                    'question created': Question.id, 
                })
        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

TEST: In the "List" tab / main screen, clicking on one of the
categories in the left column will cause only questions of that
category to be shown.
"""
    @app.route('/categories/${id}/questions', methods=['GET'])
    def categorized_questions():
        questions = Question.query.order_by(Question.category).all()
        question_set = paginate_questions(request, questions)
        return jsonify({
            'questions': question_set,
        })
    
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

TEST: In the "Play" tab, after a user selects "All" or a category,
one question at a time is displayed, the user is allowed to answer
and shown whether they were correct or not.
"""
    @app.route('/trivia', methods=['POST'])
    def play_trivia():

        body = request.get_json()
        previous_question = body.get['previous_question']
        category_id = body['quiz_category']['id']
        questions = Question.query.all()
        question_set = paginate_questions(request, questions)
        selected = []

        for question in questions:
            if question.id not in previous_question:
                selected.append(question.format())

        return jsonify({
            'question': question
        })



    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )
    
    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    return app

