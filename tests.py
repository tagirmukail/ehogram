from app import app
import unittest
from unittest import TestCase
# from flask_pymongo import PyMongo

class TestEhoCase(TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['MONGO_DBNAME'] = 'test'
        app.config['TESTING'] = True

    def tearDown(self):
        pass

    def test_auth(self):
        rv = self.app.get('/auth/')
        assert "Log in" in rv.data

    def test_register(self):
        rv = self.app.get('/register/')
        assert "Register" in rv.data

    def test_index(self):
        rv = self.app.get('/')
        assert rv.status_code == 302

    def test_recv(self):
        rv = self.app.get('/recv/')
        assert rv.status_code == 302



if __name__ == '__main__':
    unittest.main()