import unittest
from app import create_app, db
from app.models import User
from config import TestingConfig

class MainRoutesCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        u = User(username='mainuser', email='main@test.com')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()
        self.client.post('/auth/login', data={'username': 'mainuser', 'password': 'pass'}, follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    #test dodawnaia postu
    def test_post_submission(self):

        response = self.client.post('/index', data={'post': 'Test Post Content'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post Content', response.data)

    # test wchodzenia na profil
    def test_profile_access(self):

        response = self.client.get('/user/mainuser')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User: mainuser', response.data)