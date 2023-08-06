import os
from os.path import abspath, dirname, join, exists
import unittest
import sys
import site

_libDir = abspath(join(dirname(abspath(__file__)), '..', '..'))

# make sure virtual env paths get precidence over any global libraries from
# system site-packages dir
_backupSysPath = sys.path
sys.path = []
site.addsitedir(_libDir)
sys.path.extend(_backupSysPath)

# now do other imports that might come from local virtual env
from sqlalchemy import Table, MetaData, String, Integer, create_engine, \
    Column, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlitefktg4sa import SqliteFkTriggerGenerator, auto_assign

dbconn = 'sqlite:///test.sqlite'
dbconn = 'sqlite://'

class TestBase(unittest.TestCase):
    
    def connect(self):
        if os.path.exists('test.sqlite'):
            os.remove('test.sqlite')
        self.md = MetaData()
        
        self.md.bind = create_engine(dbconn)
    
    def setUp(self):
        self.connect()
        
        # setup tables
        persons = Table('persons', self.md, 
            Column('id', Integer, primary_key = True),
            Column('name', String(16), nullable = False)
        )
        
        addresses = Table('addresses', self.md, 
            Column('id', Integer, primary_key=True),
            Column('persons_id', Integer, ForeignKey("persons.id"), nullable=False),
            Column('street', String(40), nullable=False)
        )
        
        phones = Table('phones', self.md, 
            Column('id', Integer, primary_key=True),
            Column('persons_id', Integer, ForeignKey("persons.id", ondelete='cascade'), nullable=True),
            Column('number', String(10), nullable=False)
        )
        
        # set FK triggers to be generated manually on each table
        #addresses.append_ddl_listener('after-create', SqliteFkTriggerGenerator)
        #phones.append_ddl_listener('after-create', SqliteFkTriggerGenerator)
        
        # set FK triggers to be genereated on all tables in the metadata
        auto_assign(self.md)
        
        # create tables
        self.md.create_all()
        
        # create a single person record
        persons.insert(values={'id': 1, 'name':'test person'}).execute()
        
    def tearDown(self):
        self.md.bind.dispose()
        self.md.bind = None
        self.md = None

class FkTests(TestBase):
    
    def _update_setup(self):
        self.md.tables['persons'].insert(values={'id': 2, 'name':'2nd person'}).execute()
        self.md.tables['addresses'].insert(values={'id':1, 'persons_id':1, 'street':'123 main street'}).execute()
        self.md.tables['phones'].insert(values={'id':1, 'persons_id':2, 'number':'123456789'}).execute()
        
    def testGoodInsert(self):
        """Make sure we can insert a valid address & phone records"""
        self.md.tables['addresses'].insert(values={'persons_id':1, 'street':'123 main street'}).execute()
        self.md.tables['phones'].insert(values={'persons_id':1, 'number':'123456789'}).execute()
        
    def testBadInsert(self):
        """ inserting with missing persons id should fail """
        
        try:
            self.md.tables['addresses'].insert(values={'persons_id':2, 'street':'123 main street'}).execute()
        except IntegrityError:
            pass
        else:
            self.fail("insert foreign key did not work")
            
    def testGoodNullInsert(self):
        """ inserting with null persons id is ok for phone numbers """
        self.md.tables['phones'].insert(values={'persons_id':None, 'number':'123456789'}).execute()
    
    def testGoodUpdate(self):
        """ updating to an existing person should work """
        self._update_setup()
        addresses = self.md.tables['addresses']
        addresses.update(values={'persons_id':2}, id=1).execute()
        rs = self.md.tables['addresses'].select(addresses.c.id == 1).execute()
        row = rs.fetchone()
        self.assertEqual(row['persons_id'], 2)
    
    def testBadUpdate(self):
        """ updating to a non-existant person should fail """
        self._update_setup()
        try:
            addresses = self.md.tables['addresses']
            addresses.update(values={'persons_id':3}, id=1).execute()
        except IntegrityError:
            pass
        else:
            self.fail("update foreign key did not work")
    
    def testGoodNullUpdate(self):
        """ updating to a NULL value should be ok for phone numbers """
        self._update_setup()
        phones = self.md.tables['phones']
        phones.update(values={'persons_id':None}, id=1).execute()
        
        rs = phones.select(phones.c.id == 1).execute()
        row = rs.fetchone()
        self.assertEqual(row['persons_id'], None)
    
    def testGoodDelete(self):
        """ deleting main record when no children records exist is ok """
        self._update_setup()
        persons = self.md.tables['persons']
        self.assertEqual( persons.count().execute().fetchone()['tbl_row_count'], 2)
        persons.delete(persons.c.id == 2).execute()
        self.assertEqual( persons.count().execute().fetchone()['tbl_row_count'], 1)
    
    def testBadDelete(self):
        """ deleting main record when children exist is an error """
        self._update_setup()
        persons = self.md.tables['persons']
        
        try:
            persons.delete(persons.c.id == 1).execute()
        except IntegrityError:
            pass
        else:
            self.fail("delete foreign key did not work")
    
    def testCascadingDelete(self):
        """ deleting main record forces children to be deleted """
        self._update_setup()
        persons = self.md.tables['persons']
        phones = self.md.tables['phones']
        
        try:
            self.assertEqual( phones.count().execute().fetchone()['tbl_row_count'], 1)
            persons.delete(persons.c.id == 2).execute()
            self.assertEqual( phones.count().execute().fetchone()['tbl_row_count'], 0)
        except IntegrityError:
            self.fail('cascading delete failed')
    
    def testTableDeletionAndTriggerRecreate(self):
        """
            this tests the deletion of a table and recreation of tables
            which can be a problem since the delete FK is put on a different
            table than what might have been deleted
        """
        
        # drop the child tables, which should leave a delete FKs still on
        # the persons table
        self.md.tables['phones'].drop()
        self.md.tables['addresses'].drop()
        
        # re-create the tables, which if not handled properly, would
        # cause an SQL error b/c the triggers already exists
        self.md.create_all()

        
if __name__ == "__main__":
    unittest.main()