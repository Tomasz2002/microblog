import unittest
from app import create_app, db
from app.models import User
from config import TestingConfig

class AuthRoutesCase(unittest.TestCase):
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

    def test_registration_and_login(self):
        # Teset rejestacja i logowanie
        response = self.client.post('/auth/register', data={
            'username': 'newuser', 'email': 'new@example.com',
            'password': 'pass', 'password2': 'pass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)

        #logowanie
        response = self.client.post('/auth/login', data={
            'username': 'newuser', 'password': 'pass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hi, newuser!', response.data)

    def test_login_error(self):
        # Błędne hasło
        response = self.client.post('/auth/login', data={
            'username': 'wrong', 'password': 'bad'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)

    def test_registration_duplicates(self):
        # Blokada duplikatów maila albo nicku
        u = User(username='duplicate', email='dup@test.com')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()
        response = self.client.post('/auth/register', data={
            'username': 'duplicate', 'email': 'other@test.com',
            'password': 'pass', 'password2': 'pass'
        }, follow_redirects=True)
        self.assertIn(b'Please use a different username', response.data)