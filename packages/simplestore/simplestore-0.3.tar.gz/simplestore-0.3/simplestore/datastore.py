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

import zlib
from hashlib import md5

try:
    import cPickle as pickle
except ImportError:
    import pickle

from MySQLdb import escape_string

from simplestore.connection import Connection
from simplestore.object_proxy import ObjectProxy

__entities_table__ = 'entities'

class DataStore(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.indexes = {}
        self._conns = {}

        self.shards = kwargs.get('shards', [kwargs.get('host')])
        for i, shard in enumerate(self.shards):
            self._conns[shard] = ObjectProxy('_conn_%d' % i)

    def choose_shard(self, id):
        i = hash(md5(id).hexdigest()) % len(self.shards)
        return self.shards[i]

    def get_connection(self, host=None):
        if not host:
            host = self.shards[0]

        if not hasattr(self._conns[host], '_db'):
            self._conns[host].set(Connection(host,
                                             self.kwargs.get('db'),
                                             self.kwargs.get('user'),
                                             self.kwargs.get('passwd')))
        return self._conns[host]._obj()

    def add_index(self, index):
        if not self.indexes.has_key(index.table):
            self.indexes[index.table] = index

    def index_entity(self, entity):
        shard_sql = {}

        def attrs_in_entity(entity):
            def _mapper(attr):
                return hasattr(entity, attr)
            return _mapper

        for index in self.indexes.values():
            bools = map(attrs_in_entity(entity), index.properties)
            res = reduce(lambda x, y: x == y == True, bools)
            if res:
                shard_on_value = getattr(entity, index.shard_on)
                index_shard = self.choose_shard(shard_on_value)

                sql = index.index_sql(entity)
                if sql:
                    if not shard_sql.has_key(index_shard):
                        shard_sql[index_shard] = []
                    shard_sql[index_shard].append(sql)

        for shard, sql_list in shard_sql.iteritems():
            conn = self.get_connection(shard)
            for sql in sql_list:
                conn.execute(sql)

    def index_entity_list(self, entity_list):
        for entity in entity_list:
            self.index_entity(entity)

    def update_entity_indexes(self, entity):
        shard_sql = {}

        def attrs_in_entity(entity):
            def _mapper(attr):
                return hasattr(entity, attr)
            return _mapper

        for index in self.indexes.values():
            bools = map(attrs_in_entity(entity), index.properties)
            res = reduce(lambda x, y: x == y == True, bools)
            if res:
                shard_on_value = getattr(entity, index.shard_on)
                index_shard = self.choose_shard(shard_on_value)

                sql = index.update_index_sql(entity)
                if sql:
                    if not shard_sql.has_key(index_shard):
                        shard_sql[index_shard] = []
                    shard_sql[index_shard].append(sql)

        for shard, sql_list in shard_sql.iteritems():
            conn = self.get_connection(shard)
            for sql in sql_list:
                conn.execute(sql)

    def put(self, entity):
        id = getattr(entity, 'id', None)
        if id is None:
            raise Exception("Entity objects are required to have "
                            "an `id` attribute.")

        fields = entity.compressed_fields()

        sql = "INSERT INTO %s" % __entities_table__
        sql+= " (id, fields) VALUES (%s, %s)"

        shard = self.choose_shard(id)
        conn = self.get_connection(shard)

        conn.execute(sql, id, fields)

        self.index_entity(entity)

    def put_list(self, entity_list):
        entity_shards = {}

        for entity in entity_list:
            shard = self.choose_shard(entity.id)
            if not entity_shards.has_key(shard):
                entity_shards[shard] = []

            fields = entity.compressed_fields()
            entity_shards[shard].append((entity.id, fields))

        for shard, values in entity_shards.iteritems():
            conn = self.get_connection(shard)
            sql = "INSERT INTO %s" % __entities_table__
            sql+= " (id, fields) VALUES (%s, %s)"
            conn.executemany(sql, values)

        self.index_entity_list(entity_list)

    def update(self, entity, **kwargs):
        id = getattr(entity, 'id', None)
        if id is None:
            raise Exception("Entity objects are required to have "
                            "an `id` attribute.")

        fields = entity.compressed_fields()

        sql = "UPDATE %s" % __entities_table__
        sql+= " SET fields = %s WHERE id = %s"

        shard = self.choose_shard(id)
        conn = self.get_connection(shard)

        conn.execute(sql, fields, id)

        if not kwargs.get('noindex', False):
            self.update_entity_indexes(entity)

    def get(self, id):
        if not id:
            return None

        shard = self.choose_shard(id)
        conn = self.get_connection(shard)

        sql = "SELECT * FROM %s WHERE id = '%s'" % (
            __entities_table__,
            escape_string(id)
        )

        obj = conn.get(sql)
        if obj is None:
            return None

        fields = zlib.decompress(obj['fields'])
        fields = pickle.loads(fields)

        return fields

    def get_list(self, id_list, **kwargs):
        if not id_list:
            return []

        order_by = kwargs.get('order', None)
        limit = kwargs.pop('limit', None)

        entity_shards = {}
        for id in id_list:
            shard = self.choose_shard(id)
            if not entity_shards.has_key(shard):
                entity_shards[shard] = []
            entity_shards[shard].append(id)

        objs = []
        for shard, ids in entity_shards.iteritems():
            sql = "SELECT * FROM %s" % __entities_table__
            sql+= " WHERE id IN (%s)" % ', '.join(["'%s'" % id for id in ids])

            if order_by:
                sql += " ORDER BY %s" % order_by

            if limit:
                sql += " LIMIT %d" % limit

            conn = self.get_connection(shard)
            objs.extend(conn.query(sql))

        entities = []
        for obj in objs:
            fields = zlib.decompress(obj['fields'])
            fields = pickle.loads(fields)
            entities.append(fields)

        return entities

    def delete(self, entity):
        id = getattr(entity, 'id', None)
        if not id:
            raise Exception('Entity objects are required to have an '
                            '`id` attribute.')

        shard = self.choose_shard(id)
        conn = self.get_connection(shard)

        sql = "DELETE FROM %s" % __entities_table__
        sql+= " WHERE id = %s"
        conn.execute(sql, id)

        self.deindex_entity(entity)

    def delete_list(self, entity_list):
        """modified this to accept a list of entity objects
        rather than a list of dicts"""

        id_list = [e['id'] for e in entity_list_of_dicts if hasattr(e, 'id')]

        id_shards = {}
        for id in id_list:
            shard = self.choose_shard(id)
            if not id_shards.has_key(shard):
                id_shards[shard] = []
            id_shards[shard].append(id)

        for shard, ids in id_shards.iteritems():
            conn = self.get_connection(shard)

            sql = "DELETE FROM %s" % __entities_table__
            sql+= " WHERE id IN (%s)" % ','.join(["'%s'" % id for id in ids])

            conn.execute(sql)

        self.deindex_entity_list(entity_list)

    def deindex_entity(self, entity):
        id = getattr(entity, 'id', None)
        if not id:
            raise Exception('Entity objects are required to have an '
                            '`id` attribute.')

        for index in self.indexes.values():
            sql = "DELETE FROM %s" % index.table
            sql+= " WHERE entity_id = %s"

            # if there's only one database instance, there's pretty much
            # no point to using shard_on, right?
            if len(self.shards) == 1:
                shard = self.shards[0]
            else:
                shard_on_value = getattr(entity, index.shard_on, None)
                if not shard_on_value:
                    continue

                shard = self.choose_shard(shard_on_value)

            conn = self.get_connection(shard)
            conn.execute(sql, id)

    def deindex_entity_list(self, entity_list):
        # probably not very efficient at all.
        # maybe come up with something else.
        for e in entity_list:
            self.deindex_entity(e)

    def global_execute(self, sql, *parameters):
        """execute `sql` across all shards."""
        for shard in self.shards:
            conn = self.get_connection(shard)
            conn.execute(sql, *parameters)

    def close(self):
        for shard in self._conns.keys():
            db = getattr(self._conns[shard], '_db', None)
            if db is not None:
                self._conns[shard]._db.close()
                self._conns[shard]._db = None
