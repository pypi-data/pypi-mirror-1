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

from simplestore import entities_table
from simplestore.index import Index
from simplestore.datastore import DataStore

from simplestore.tests import config
from simplestore.tests import gen_uuid, User, Entry

class ShardTestCase(unittest.TestCase):

    def setUp(self):
        self.datastore = DataStore(**config.sharded_datastore_params)
        self.datastore.global_execute(entities_table)

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

        self.datastore.add_index(Index('index_user',
                                       properties=['username'],
                                       shard_on='username'))

        # distribute entries across shards based on user_id
        self.datastore.add_index(Index('index_user_entries',
                                       properties=['user_id'],
                                       shard_on='user_id'))

    def tearDown(self):
        self.datastore.global_execute('DROP TABLE entities')
        self.datastore.global_execute('DROP TABLE index_user')
        self.datastore.global_execute('DROP TABLE index_user_entries')

    def test_put_get(self):
        user = User(id=gen_uuid(), firstname='David', lastname='Reynolds')
        user.username = 'david'
        self.datastore.put(user)

        index = self.datastore.indexes['index_user']
        user = index.get(self.datastore, username='david')

        entries = []
        for i in xrange(10):
            entry = Entry(id=gen_uuid(),
                          user_id=user['id'],
                          title='%s' % i,
                          content='Hello, world')
            entries.append(entry)
        self.datastore.put_list(entries)

        # the entries and their indexes are distributed across the two test shards
        entry_index = self.datastore.indexes['index_user_entries']
        user_entries = entry_index.get_all(self.datastore, user_id=user['id'])

        assert len(user_entries) == 10
