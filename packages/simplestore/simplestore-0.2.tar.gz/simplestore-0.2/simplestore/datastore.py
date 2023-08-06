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

        self._conn = ObjectProxy('_conn')

    def _get_db(self):
        if not hasattr(self._conn, '_db'):
            self._conn.set(Connection(self.kwargs['host'],
                                      self.kwargs['db'],
                                      self.kwargs['user'],
                                      self.kwargs['passwd']))
        return self._conn._obj()
    conn = property(_get_db)

    def add_index(self, index):
        if not self.indexes.has_key(index.table):
            self.indexes[index.table] = index

    def index_entity(self, entity):
        index_sql = []

        def attrs_in_entity(entity):
            def _mapper(attr):
                return hasattr(entity, attr)
            return _mapper

        for index in self.indexes.values():
            bools = map(attrs_in_entity(entity), index.properties)
            res = reduce(lambda x, y: x == y == True, bools)
            if res:
                sql = index.index_sql(entity)
                if sql:
                    index_sql.append(sql)

        for sql in index_sql:
            self.execute(sql)

    def index_entity_list(self, entity_list):
        for entity in entity_list:
            self.index_entity(entity)

    def update_entity_indexes(self, entity):
        index_sql = []

        def attrs_in_entity(entity):
            def _mapper(attr):
                return hasattr(entity, attr)
            return _mapper

        for index in self.indexes.values():
            bools = map(attrs_in_entity(entity), index.properties)
            res = reduce(lambda x, y: x == y == True, bools)
            if res:
                sql = index.update_index_sql(entity)
                if sql:
                    index_sql.append(sql)

        for sql in index_sql:
            self.execute(sql)

    def put(self, entity):
        id = getattr(entity, 'id', None)
        if id is None:
            raise Exception("Entity objects are required to have "
                            "an `id` attribute.")

        fields = entity.compressed_fields()

        sql = "INSERT INTO %s" % __entities_table__
        sql+= " (id, fields) VALUES (%s, %s)"

        self.execute(sql, id, fields)

        self.index_entity(entity)

    def put_list(self, entity_list):
        values = []
        for entity in entity_list:
            fields = entity.compressed_fields()
            values.append((entity.id, fields))

        sql = "INSERT INTO %s" % __entities_table__
        sql+= " (id, fields) VALUES (%s, %s)"
        self.executemany(sql, values)

        self.index_entity_list(entity_list)

    def update(self, entity, **kwargs):
        id = getattr(entity, 'id', None)
        if id is None:
            raise Exception("Entity objects are required to have "
                            "an `id` attribute.")

        fields = entity.compressed_fields()

        sql = "UPDATE %s" % __entities_table__
        sql+= " SET fields = %s WHERE id = %s"

        self.execute(sql, fields, id)

        if not kwargs.get('noindex', False):
            self.update_entity_indexes(entity)

    def get(self, id):
        if not id:
            return None

        sql = "SELECT * FROM %s WHERE id = '%s'" % (
            __entities_table__,
            escape_string(id)
        )

        obj = self.conn.get(sql)
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

        sql = "SELECT * FROM %s" % __entities_table__
        sql+= " WHERE id IN (%s)" % ','.join(["'%s'" % id for id in id_list])

        if order_by:
            sql += " ORDER BY %s" % order_by

        if limit:
            sql += " LIMIT %d" % limit

        objs = self.query(sql)

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

        sql = "DELETE FROM %s" % __entities_table__
        sql+= " WHERE id = %s"
        self.execute(sql, id)

        self.deindex_entity(entity)

    def delete_list(self, entity_list_of_dicts):
        ids = [e['id'] for e in entity_list_of_dicts if e.has_key('id')]
        sql = "DELETE FROM %s" % __entities_table__
        sql+= " WHERE id IN (%s)" % ','.join(["'%s'" % id for id in ids])

        self.execute(sql)
        self.deindex_entity_list(entity_list_of_dicts)

    def deindex_entity(self, entity):
        id = entity.get('id')
        if not id:
            raise Exception('Entity objects are required to have an '
                            '`id` attribute.')

        for key in self.indexes.keys():
            sql = "DELETE FROM %s" % key
            sql+= " WHERE entity_id = %s"
            self.execute(sql, id)

    def deindex_entity_list(self, entity_list_of_dicts):
        ids = [e['id'] for e in entity_list_of_dicts if e.has_key('id')]
        for key in self.indexes.keys():
            sql = "DELETE FROM %s" % key
            sql+= " WHERE entity_id IN (%s)" % ','.join(["'%s'" % id for id in ids])
            self.execute(sql)

    def execute(self, sql, *parameters):
        return self.conn.execute(sql, *parameters)

    def executemany(self, sql, parameters):
        return self.conn.executemany(sql, parameters)

    def query(self, sql, *parameters):
        return self.conn.query(sql, *parameters)

    def close(self):
        db = getattr(self._conn, '_db', None)
        if db is not None:
            self._conn._db.close()
            self._conn._db = None
