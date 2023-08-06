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

from simplestore.index import Index
from simplestore.tests import gen_uuid, User, Entry, DataStoreTestCase

class IndexTestCase(DataStoreTestCase):

    def setUp(self):
        super(IndexTestCase, self).setUp()

        # create index table
        self.datastore.global_execute("""
        CREATE TABLE index_user (
            username VARCHAR(255) NOT NULL UNIQUE,
            entity_id CHAR(32) NOT NULL UNIQUE,
            PRIMARY KEY (username, entity_id)
        ) ENGINE=InnoDB;
        """)

        self.datastore.global_execute("""
        CREATE TABLE index_user_entries (
            user_id CHAR(32) NOT NULL,
            entity_id CHAR(32) NOT NULL UNIQUE,
            PRIMARY KEY (user_id, entity_id)
        ) ENGINE=InnoDB;
        """)

        # store entities with the `username` property
        self.datastore.add_index(Index('index_user',
                                       properties=['username'],
                                       shard_on='username'))

        # store entities with the `user_id` property
        self.datastore.add_index(Index('index_user_entries',
                                       properties=['user_id'],
                                       shard_on='user_id'))

    def tearDown(self):
        super(IndexTestCase, self).tearDown()

        self.datastore.global_execute('DROP TABLE index_user')
        self.datastore.global_execute('DROP TABLE index_user_entries')

    def test_put_get(self):
        user = User(id=gen_uuid(), firstname='David', lastname='Reynolds')
        user.username = 'david'

        self.datastore.put(user)

        index = self.datastore.indexes['index_user']

        # Get operations on indexes perform two queries. One to get the entity_id
        # from the index table and another for pulling results from the entities table
        # using that entity_id.
        user = index.get(self.datastore, username='david')
        assert user['firstname'] == 'David'
        assert user['lastname'] == 'Reynolds'

    def test_put_get_list(self):
        user = User(id=gen_uuid(), firstname='David', lastname='Reynolds')
        user.username = 'david'
        self.datastore.put(user)

        entry1 = Entry(id=gen_uuid(),
                       user_id=user.id,
                       title='Foo',
                       content='Hello, World')

        entry2 = Entry(id=gen_uuid(),
                       user_id=user.id,
                       title='Bar',
                       content='Test entry number 2')

        self.datastore.put_list([entry1, entry2])

        index = self.datastore.indexes['index_user_entries']

        # get all entries that have this user_id. Like before, there are two SELECTs.
        # get_all selects the entity_id's of all entries where
        # index_user_entries.user_id == user.id and then gets a list of entities
        # that match the entity_id's from the entities table.
        entries = index.get_all(self.datastore, user_id=user.id)
        assert len(entries) == 2
