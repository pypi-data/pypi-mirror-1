from simplestore.tests import config
from simplestore.tests import gen_uuid, Person, DataStoreTestCase

class TestBlankEntitiesTable(DataStoreTestCase):

    def test_creation(self):
        scalar = self.datastore.query("""
        SELECT COUNT(*) AS count
            FROM entities
        """)[0]

        assert scalar['count'] == 0

class TestDataStoreOperations(DataStoreTestCase):

    def test_put_get(self):
        p = Person(id=gen_uuid(), firstname='David', lastname='Reynolds')
        self.datastore.put(p)

        entity = self.datastore.get(p.id)
        assert isinstance(entity, dict)
        assert entity['firstname'] == 'David'
        assert entity['lastname'] == 'Reynolds'

    def test_update(self):
        p = Person(id=gen_uuid(), firstname='David', lastname='Reynolds')
        self.datastore.put(p)

        entity = self.datastore.get(p.id)
        p = Person(**entity)
        p.firstname = 'Foo'
        p.lastname = 'Bar'

        self.datastore.update(p)

        entity = self.datastore.get(p.id)
        assert entity['firstname'] == 'Foo'
        assert entity['lastname'] == 'Bar'

    def test_put_get_list(self):
        persons = [Person(id=gen_uuid(), firstname='David', lastname='Reynolds'),
                   Person(id=gen_uuid(), firstname='Foo', lastname='Bar')]
        self.datastore.put_list(persons)

        entities = self.datastore.get_list([p.id for p in persons])
        assert len(entities) == 2
