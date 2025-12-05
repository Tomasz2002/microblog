import unittest
from app import create_app, db
from app.models import User
from config import TestingConfig

class APICase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, token):
        return {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def test_get_user_api(self):
        u = User(username='apiuser', email='api@example.com')
        u.set_password('pass')
        token = u.get_token()
        db.session.add(u)
        db.session.commit()
        headers = self.get_api_headers(token)
        response = self.client.get(f'/api/users/{u.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['username'], 'apiuser')