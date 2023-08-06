# Copyright 2009 David Reynolds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        self.datastore.global_execute(entities_table)

    def tearDown(self):
        self.datastore.global_execute('DROP TABLE entities')
