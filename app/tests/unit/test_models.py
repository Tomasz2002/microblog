import unittest
from app import create_app, db
from app.models import User, Post
from config import TestingConfig

class ModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

# Test hashowania hasła
    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

 # Test follow/unfollow i liczników
    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add_all([u1, u2])
        db.session.commit()
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u2.followers_count(), 0)
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)
        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))

 # Test tworzenia postów
    def test_post_creation(self):
        u = User(username='test', email='test@test.com')
        p = Post(body='my post', author=u)
        db.session.add(u)
        db.session.add(p)
        db.session.commit()
        posts = db.session.scalars(u.posts.select()).all()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].body, 'my post')