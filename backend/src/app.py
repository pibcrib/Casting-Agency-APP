import os
from flask import Flask, request, abort, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from database.models import setup_db, Movie, Actor
from auth.auth import AuthError, requires_auth, AUTH0_DOMAIN, API_AUDIENCE


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # Sets up CORS. Allows '*' for origins.
    # Uses after_request decorator to sets Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/', methods=['GET'])
    def welcome():
        return jsonify({
            'success': True,
            'message': 'Welcome'
        })

    @app.route('/login', methods=['GET'])
    def login():
        #endpoint to login to Auth0. Can create account but token returned wont have valid permissions to access endpoints
        AUTH0_CLIENT_ID = os.environ.get('AUTH0_CLIENT_ID')
        AUTH0_CALLBACK_URL = os.environ.get('AUTH0_CALLBACK_URL')

        login_url = f'https://{AUTH0_DOMAIN}/authorize?audience={API_AUDIENCE}&response_type=token&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK_URL}'

        print(login_url)
        return redirect(login_url)

    @app.route('/movies', methods=['GET'])
    @requires_auth(permission='get:movies')
    def get_movies():
        movies = Movie.query.all()

        if movies:
            return jsonify({
                'success': True,
                'movies': [movie.format() for movie in movies],
                'total_num_movies': len(movies)})
        else:
            abort(404)

    @app.route('/actors', methods=['GET'])
    @requires_auth(permission='get:actors')
    def get_actors():
        actors = Actor.query.all()

        if not actors:
            abort(404)

        return jsonify({
            'success': True,
            'actors': [actor.format() for actor in actors],
            'total_num_actors': len(actors)
        })

    @app.route('/movies/<int:movie_id>/actors', methods=['GET'])
    @requires_auth(permission='get:actors')
    def get_cast_for_movie(movie_id):
        actors = Actor.query.filter(Actor.movie_id == movie_id).all()

        if not actors:
            abort(404)

        movie = Movie.query.get(movie_id)
        return jsonify({
            'success': True,
            'actors': [actor.format() for actor in actors],
            'num_actors': len(actors),
            'current_movie': movie.format()
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth(permission='post:movies')
    def create_movie():
        body = request.get_json()

        try:
            new_movie = Movie(
                title=body.get('title', None),
                release=body.get('release', None)
            )
            new_movie.insert()
            return jsonify({
                'success': True,
                'new_movie_id': new_movie.id
            })

        except Exception as e:
            print(e)
            abort(422)

    @app.route('/actors', methods=['POST'])
    @requires_auth(permission='post:actors')
    def add_actor():
        body = request.get_json()

        # debug errors adding movie id
        try:
            new_actor = Actor(
                name=body.get('name', None),
                age=body.get('age', None),
                gender=body.get('gender', None),
            )
            new_actor.movie_id = body.get('movie_id', None)

            new_actor.insert()
            return jsonify({
                'success': True,
                'new_actor_id': new_actor.id
            })

        except Exception as e:
            print(e)
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth(permission='patch:movies')
    def update_movie(movie_id):
        movie = Movie.query.get(movie_id)

        if not movie:
            abort(404)

        body = request.get_json()
        try:
            movie.title = body.get('title', movie.title)
            movie.release = body.get('release', movie.release)
            movie.update()
            return jsonify({
                'success': True,
                'updated_movie': movie.format()
            })

        except Exception as e:
            print(e)
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth(permission='patch:actors')
    def update_actor(actor_id):
        actor = Actor.query.get(actor_id)

        if not actor:
            abort(404)

        # consider taking movie title and then searching databse for ID for 4th
        # attribute
        body = request.get_json()
        try:
            actor.name = body.get('name', actor.name)
            actor.age = body.get('age', actor.age)
            actor.gender = body.get('gender', actor.gender)
            actor.movie_id = body.get('movie_id', actor.movie_id)
            actor.update()
            return jsonify({
                'success': True,
                'updated_actor': actor.format()
            })

        except Exception as e:
            print(e)
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth(permission='delete:movies')
    def delete_movie(movie_id):
        movie = Movie.query.get(movie_id)

        if not movie:
            abort(404)

        try:
            movie.delete()
            return jsonify({
                'success': True,
                'deleted_movie_id': movie.id
            })
        except Exception as e:
            print(e)
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth(permission='delete:actors')
    def delete_actor(actor_id):
        actor = Actor.query.get(actor_id)

        if not actor:
            abort(404)

        try:
            actor.delete()
            return jsonify({
                'success': True,
                'deleted_actor_id': actor.id
            })

        except Exception as e:
            print(e)
            abort(422)

    # error handlers
    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(AuthError)
    def authentication_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error,
        }), error.status_code

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
