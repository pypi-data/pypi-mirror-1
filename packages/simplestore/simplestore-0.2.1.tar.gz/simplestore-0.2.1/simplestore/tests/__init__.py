import unittest
import uuid

from simplestore import model, entities_table
from simplestore.datastore import DataStore

def gen_uuid():
    return str(uuid.uuid4()).replace('-', '')

class Person(model.Model):

    id = model.KeyProperty(required=True)
    firstname = model.StringProperty()
    lastname = model.StringProperty()

class User(Person):

    username = model.StringProperty()

class Entry(model.Model):

    id = model.KeyProperty(required=True)
    user_id = model.KeyProperty(required=True)
    title = model.StringProperty()
    content = model.StringProperty()

class DataStoreTestCase(unittest.TestCase):

    def setUp(self):
        self.datastore = DataStore(**config.datastore_params)
        self.datastore.execute(entities_table)

    def tearDown(self):
        self.datastore.execute('DROP TABLE entities')
