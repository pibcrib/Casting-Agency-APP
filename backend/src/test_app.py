import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from database.models import setup_db, init_db_data, Movie, Actor


class CastingAgencyTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "castingagency_test"
        self.default_path = "postgresql://postgres@{}/{}".format(
            'localhost:5432', self.database_name)

        # replacing since 'postgres' is deprecated
        self.database_path = os.environ.get(
            "DATABASE_URL_TEST", self.default_path).replace(
            'postgres://', 'postgresql://')
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # #initializing test_database with dummy data
        # init_database()
        init_db_data()

        # for testing POST and PATCH ENDPOINTS
        self.movie = {
            'title': 'Hindsight-19: A Review of the COVID Pandemic',
            'release': '2023-1-15'
        }
        self.actor = {
            'name': 'Jake Gyllenhaalll',
            'age': 40,
            'gender': 'Male',
            'movie_id': 1
        }

        # used for failure tests
        self.movie_bad = {
            'release': '2040 - 05 - 05'
        }
        self.actor_bad = {
            'age': 25,
            'gender': 'Female',
            'movie_id': 1
        }

        # RBAC tokens
        self.assistant = os.getenv('ASSISTANT_TOKEN')
        self.director = os.getenv('DIRECTOR_TOKEN')
        self.producer = os.getenv('PRODUCER_TOKEN')

    def tearDown(self):
        """Executed after reach test"""
        pass

    # tests get_movies() in app.py
    def test_get_movies(self):
        res = self.client().get(
            '/movies',
            headers={
                'Authorization': f'Bearer {self.assistant}'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        self.assertTrue(data['total_num_movies'])

    # tests get_actors() in app.py
    def test_get_actors(self):
        res = self.client().get(
            '/actors',
            headers={
                'Authorization': f'Bearer {self.assistant}'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertTrue(data['total_num_actors'])

    # test create_movie() in app.py
    def test_create_movie(self):
        res = self.client().post(
            '/movies',
            headers={
                'Authorization': f'Bearer {self.producer}',
                'Content-Type': 'application/json'},
            json=self.movie)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['new_movie_id'])

    # tests failure for create_movie when 'title' field is missing
    def test_422_if_create_movie_unprocessable(self):
        res = self.client().post(
            '/movies',
            headers={
                'Authorization': f'Bearer {self.producer}',
                'Content-Type': 'application/json'},
            json=self.movie_bad)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'unprocessable')

    def test_add_actor(self):
        res = self.client().post(
            '/actors',
            headers={
                'Authorization': f'Bearer {self.director}',
                'Content-Type': 'application/json'},
            json=self.actor)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['new_actor_id'])

    def test_422_if_add_actor_unprocessable(self):
        res = self.client().post(
            '/actors',
            headers={
                'Authorization': f'Bearer {self.director}',
                'Content-Type': 'application/json'},
            json=self.actor_bad)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'unprocessable')

    def test_update_movie(self):
        movie = Movie.query.get(2).format()
        movie['title'] = 'Untitled'

        res = self.client().patch(
            '/movies/2',
            headers={
                'Authorization': f'Bearer {self.director}',
                'Content-Type': 'application/json'},
            json=movie)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['updated_movie']['title'], 'Untitled')

    # tests update_movie() if no json payload is provided
    def test_400_if_bad_request_update_movie(self):
        res = self.client().patch(
            '/movies/2',
            headers={
                'Authorization': f'Bearer {self.director}',
                'Content-Type': 'application/json'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    def test_update_actor(self):
        actor = Actor.query.get(2).format()
        actor['name'] = 'Generic Name'

        res = self.client().patch(
            '/actors/2',
            headers={
                'Authorization': f'Bearer {self.director}',
                'Content-Type': 'application/json'},
            json=actor)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['updated_actor']['name'], 'Generic Name')

    # tests update_actor() if no json payload is provided
    def test_400_if_bad_request_update_actor(self):
        res = self.client().patch(
            '/actors/2',
            headers={
                'Authorization': f'Bearer {self.director}',
                'Content-Type': 'application/json'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    def test_delete_movie(self):
        res = self.client().delete(
            '/movies/3',
            headers={
                'Authorization': f'Bearer {self.producer}'})

        data = json.loads(res.data)

        movie = Movie.query.get(3)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(movie, None)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_movie_id'], 3)

    def test_404_if_movie_not_found(self):
        res = self.client().delete(
            '/movies/5000',
            headers={'Authorization': f'Bearer {self.producer}'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_actor(self):
        res = self.client().delete(
            '/actors/3',
            headers={
                'Authorization': f'Bearer {self.director}'})

        data = json.loads(res.data)

        actor = Actor.query.get(3)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(actor, None)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_actor_id'], 3)

    def test_404_if_actor_not_found(self):
        res = self.client().delete(
            '/actors/5000',
            headers={'Authorization': f'Bearer {self.director}'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_cast_for_movie(self):
        res = self.client().get(
            '/movies/1/actors',
            headers={'Authorization': f'Bearer {self.assistant}'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertTrue(data['num_actors'])
        self.assertTrue(data['current_movie'])

    def test_404_if_movie_does_not_exist(self):
        res = self.client().get(
            '/movies/5000/actors',
            headers={'Authorization': f'Bearer {self.assistant}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    # tests for RBAC:

    # tests for assistant role, should test for failure

    def test_auth_error_add_actor(self):
        res = self.client().post(
            '/actors',
            headers={'Authorization': f'Bearer {self.assistant}'},
            json=self.actor)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 403)
        self.assertEqual(
            data['message']['description'],
            'Access Forbidden. User not allowed to access resource.')

    def test_auth_error_update_actor(self):
        actor = Actor.query.get(2).format()
        res = self.client().patch(
            '/actors/2',
            headers={'Authorization': f'Bearer {self.assistant}'},
            json=actor)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 403)
        self.assertEqual(
            data['message']['description'],
            'Access Forbidden. User not allowed to access resource.')

    # tests for casting director role, should test for failure
    def test_auth_error_create_movie(self):
        res = self.client().post(
            '/movies',
            headers={
                'Authorization': f'Bearer {self.director}',
                'Content-Type': 'application/json'},
            json=self.movie)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 403)
        self.assertEqual(
            data['message']['description'],
            'Access Forbidden. User not allowed to access resource.')

    def test_auth_error_delete_movie(self):
        res = self.client().delete(
            '/movies/1',
            headers={
                'Authorization': f'Bearer {self.director}'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 403)
        self.assertEqual(
            data['message']['description'],
            'Access Forbidden. User not allowed to access resource.')

    # tests for executive producer role, should test for success
    def test_auth_success_get_movie(self):
        res = self.client().get(
            '/movies',
            headers={
                'Authorization': f'Bearer {self.producer}'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        self.assertTrue(data['total_num_movies'])

    def test_auth_success_get_actors(self):
        res = self.client().get(
            '/actors',
            headers={
                'Authorization': f'Bearer {self.producer}'})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertTrue(data['total_num_actors'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
