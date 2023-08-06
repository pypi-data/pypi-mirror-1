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

import urllib
try:
    import cPickle as pickle
except ImportError:
    import pickle

import datetime

from MySQLdb import escape_string

class Index(object):

    def __init__(self, table, properties=[], shard_on=None):
        """`shard_on` determines which shard the index is stored on"""
        self.table = table
        self.properties = properties
        self.shard_on = shard_on

    def index_sql(self, entity):
        """
        Indexes are strict about only indexing entities that have
        all the properties required for indexing.

        Example:
            (Just an example, the actual indexer doesn't index dict objs)

            user_id_index = Index(table="index_user_id",
                                  properties=["user_id")
            ent = Entity()
            ent['id'] = 'foo'
            ent['user_id'] = 'bar'

            sql = user_id_index.index_sql(ent)
            sql:
                INSERT INTO index_user_id (entity_id, user_id) VALUES (
                    'foo', 'bar'
                )
        """
        attrs, values = self._attrs_and_values(entity)
        if not attrs:
            return None

        values = ["'%s'" % escape_string(entity.id)] + values

        sql = "INSERT INTO %s (entity_id, %s) VALUES (%s)" % (
            self.table,
            ', '.join(attrs),
            ', '.join(values)
        )

        return sql

    def update_index_sql(self, entity):
        """Only generates SQL for changed index values"""

        if not entity._has_changed:
            # immediately return if this entity hasn't even changed.
            return None

        attrs, values = self._attrs_and_values(entity)

        if not attrs:
            return None

        def values_have_changed(entity):
            def _mapper(attr):
                ent_value = getattr(entity, attr)
                orig_value = entity._original_attrs.get(attr)
                # True if changed, False if equal
                return ent_value != orig_value
            return _mapper

        bools = map(values_have_changed(entity), attrs)
        res = reduce(lambda x, y: x or y, bools)
        if not res: return

        updates = ['%s=%s' % (attr, value)
                   for attr, value in zip(attrs, values)]

        sql = "UPDATE %s" % self.table
        sql+= " SET %s" % ', '.join(updates)
        sql+= " WHERE entity_id = '%s'" % escape_string(entity.id)

        return sql

    def _attrs_and_values(self, entity):
        values = []
        attrs = []

        # map/reduce bool changes first, then if there are changes,
        # continue stringifying values.
        for attr in self.properties:
            value = getattr(entity, attr)

            # generally if a value is None it isn't required
            # by the index, but this is a bad assumption...
            if value is None:
                continue

            if isinstance(value, bool):
                value = str(int(value))

            if isinstance(value, datetime.datetime) or \
               isinstance(value, datetime.date):
                value = str(value)

            if isinstance(value, basestring):
                value = "'%s'" % escape_string(value)

            values.append(value)
            attrs.append(attr)

        return (attrs, values)

    def get_all(self, datastore, **kwargs):
        offset = kwargs.pop('offset', None)
        limit = kwargs.pop('limit', None)
        order_by = kwargs.pop('order', None)

        # unquote_plus because inserting url-encoded strings is a bad
        # idea... python treats them as format strings. the reason
        # to do it here instead of all escape_string calls is because
        # get_all is generally used with arguments passed from the url
        # or forms. general rule: if you're inserting user input in your
        # sql, unquote and escape.

        values = []

        shard_on_value = kwargs.pop(self.shard_on, None)
        if not shard_on_value:
            raise Exception("Index doesn't have a value to shard on")

        shard_on_value = escape_string(urllib.unquote_plus(shard_on_value))
        values.append(shard_on_value)

        where_clause = []
        s = "%s=" % self.shard_on
        s+= "%s"
        where_clause.append(s)

        for k, v in kwargs.iteritems():
            if k in self.properties():
                if isinstance(v, basestring):
                    s = "%s=" % k
                    s+= "%s"
                    where_clause.append(s)
                    values.append(v)

        sql = "SELECT entity_id FROM %s" % self.table

        if values:
            sql += " WHERE "
            sql += " AND ".join(where_clause)

        if order_by:
            sql += " ORDER BY %s " % order_by

        if limit:
            sql += " LIMIT %d " % limit

        if offset:
            sql += " OFFSET %d " % offset

        shard = datastore.choose_shard(shard_on_value)
        conn = datastore.get_connection(shard)

        index_objs = conn.query(sql, *values)
        if not index_objs:
            return []

        ids = [obj['entity_id'] for obj in index_objs]
        return datastore.get_list(ids)

    def get(self, datastore, **kwargs):
        kwargs['limit'] = 1
        entity = self.get_all(datastore, **kwargs)
        if entity:
            return entity[0]
