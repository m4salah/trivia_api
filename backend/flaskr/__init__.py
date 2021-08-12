import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from  sqlalchemy.sql.expression import func

from sqlalchemy.orm import query

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_categories(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    categories = [book.format() for book in selection]
    current_categories = categories[start:end]

    return current_categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
	@DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
	'''
    CORS(app)

    '''
	@DONE: Use the after_request decorator to set Access-Control-Allow
	'''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response
    '''
	@DONE: 
	Create an endpoint to handle GET requests 
	for all available categories.
	'''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by('id').all()
        current_categories = paginate_categories(request, categories)

        dict_categories = {}

        for catecories in current_categories:
            dict_categories[str(catecories['id'])] = catecories['type']

        if len(current_categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': dict_categories,
            'total_categories': len(categories)
        })

    '''
	@DONE: 
	Create an endpoint to handle GET requests for questions, 
	including pagination (every 10 questions). 
	This endpoint should return a list of questions, 
	number of total questions, current category, categories. 

	TEST: At this point, when you start the application
	you should see questions and categories generated,
	ten questions per page and pagination at the bottom of the screen for three pages.
	Clicking on the page numbers should update the questions. 
	'''
    @app.route('/questions')
    def get_questions():
        search_term = request.args.get('q', None, type=str)
        questions = Question.query.order_by('id').all()

        if search_term:
            questions = Question.query.filter(
                Question.question.ilike('%' + search_term + '%')).all()
            print(questions)

        current_questions = paginate_categories(request, questions)
        categories = Category.query.order_by('id').all()
        current_categories = paginate_categories(request, categories)
        dict_categories = {}

        for catecories in current_categories:
            dict_categories[str(catecories['id'])] = catecories['type']

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': dict_categories,
            'currentCategory': 'History'
        })

    '''
	@DONE: 
	Create an endpoint to DELETE question using a question ID. 

	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page. 
	'''
    @app.route('/questions/<int:q_id>', methods=['DELETE'])
    def delete_question(q_id):
        try:
            q = Question.query.get(q_id)
            q.delete()
            return jsonify({
                'success': True,
                'id': q_id
            })
        except:
            abort(422)

    '''
	@DONE: 
	Create an endpoint to POST a new question, 
	which will require the question and answer text, 
	category, and difficulty score.

	TEST: When you submit a question on the "Add" tab, 
	the form will clear and the question will appear at the end of the last page
	of the questions list in the "List" tab.  
	'''
    @app.route('/questions', methods=['POST'])
    def create_question():

        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        if question is None or answer is None or category is None or difficulty is None:
            abort(422)

        try:
            q = Question(question, answer, category, difficulty)
            q.insert()

            questions_after_create = Question.query.order_by('id').all()
            current_questions = paginate_categories(
                request, questions_after_create)

            return jsonify({
                'success': True,
                'created': q.id,
                'questions': current_questions,
                'totalQuestions': len(questions_after_create)
            })
        except:
            abort(422)


    '''
	@DONE: 
	Create a GET endpoint to get questions based on category. 

	TEST: In the "List" tab / main screen, clicking on one of the 
	categories in the left column will cause only questions of that 
	category to be shown. 
	'''
    @app.route('/categories/<category_id>/questions')
    def get_questions_basedon_category(category_id):
        all_q = Question.query.all()
        all_q_category = Question.query.filter(
            Question.category == category_id).all()

        all_q_category_formated = [q.format() for q in all_q_category]
        if len(all_q) == 0:
            abort(404)
        
        if len(all_q_category_formated) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': all_q_category_formated,
            'totalQuestions': len(all_q),
            'currentCategory': 'History'
        })

    '''
	@DONE: 
	Create a POST endpoint to get questions to play the quiz. 
	This endpoint should take category and previous question parameters 
	and return a random questions within the given category, 
	if provided, and that is not one of the previous questions. 

	TEST: In the "Play" tab, after a user selects "All" or a category,
	one question at a time is displayed, the user is allowed to answer
	and shown whether they were correct or not. 
	'''
    @app.route('/quizzes', methods=['POST'])
    def get_quizzs():
        body = request.get_json()

        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        if previous_questions is None:
            abort(422)
        else:
            if quiz_category == 0:
                question = Question.query.filter(
                                            Question.id.notin_(previous_questions)).order_by(func.random()).first()
            else:
                question = Question.query.filter(
                                            Question.id.notin_(previous_questions), 
                                            Question.category == quiz_category).order_by(func.random()).first()
            
            q_formated = None
            if question:
                q_formated = question.format()

            return jsonify({
                'success': True,
                'question': q_formated,
                'quiz_category': quiz_category
            })

    '''
	@DONE: 
	Create error handlers for all expected errors 
	including 404 and 422. 
	'''
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
            "message": "Unprocessable"
        }), 422

    return app
