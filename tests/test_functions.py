import os
import unittest
from unittest.mock import patch, Mock

import requests
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv('.env.testing')
        cls.app = Flask(__name__)
        cls.app.config['TESTING'] = True
        cls.app.config['CSRF_ENABLED'] = False
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = (f'postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}'
                                         f'@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}')
        cls.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        cls.db = SQLAlchemy(cls.app)

        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.db.create_all()
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.db.session.remove()
        cls.db.drop_all()
        cls.app_context.pop()

    def test_page_not_found(self):
        response = self.app.test_client().get('/not-found')
        self.assertEqual(response.status_code, 404)

    @patch('app.requests.get')
    def test_get_people_data_success(self, mock_get):
        from app import get_people_data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {"gender": "male",
                 "name": {"title":"Mr","first":"Umut","last":"Taşçı"},
                 "location": {
                     "street": {"number":3586,"name":"Doktorlar Cd"},
                     "city": "Bartın",
                     "state": "Yozgat",
                     "country": "Turkey",
                     "postcode": 78304,
                     "coordinates": {"latitude":"70.9871","longitude":"-176.4181"},
                     "timezone": {"offset":"-1:00","description":"Azores, Cape Verde Islands"}
                 },
                 "email": "umut.tasci@example.com",
                 "dob": {"date":"1982-12-21T08:40:47.355Z","age":42},
                 "registered": {"date":"2018-09-19T13:45:46.115Z","age":6},
                 "phone": "(761)-613-4386",
                 "cell": "(539)-014-3220",
                 "picture": {
                     "large": "https://randomuser.me/api/portraits/men/83.jpg",
                     "medium": "https://randomuser.me/api/portraits/med/men/83.jpg",
                     "thumbnail": "https://randomuser.me/api/portraits/thumb/men/83.jpg"},
                 "nat":"TR"}
            ]
        }

        mock_get.return_value = mock_response

        people = get_people_data(1)
        print(people)

        self.assertEqual(len(people), 1)
        self.assertEqual(people[0]['gender'], 'male')
        self.assertEqual(people[0]['name']['first'], 'Umut')

    @patch('app.requests.get')
    def test_get_people_data_error(self, mock_get):
        from app import get_people_data
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("Test error")
        mock_get.return_value = mock_response

        people = get_people_data(1)

        self.assertIsNone(people)


if __name__ == '__main__':
    unittest.main()