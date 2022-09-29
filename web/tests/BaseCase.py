import unittest

from app import app
from ..database.client import mongoEngine


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.database = mongoEngine.get_db()

    def tearDown(self):
        # Delete Database collections after the test is done
        for collection in self.database.list_collection_names():
            self.database.drop_collection(collection)
