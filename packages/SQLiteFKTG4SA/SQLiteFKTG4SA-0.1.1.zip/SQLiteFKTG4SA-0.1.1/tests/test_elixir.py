import os
from os.path import abspath, dirname, join, exists
import unittest
import sys
import site
from test_sq import TestBase, dbconn

# now do other imports that might come from local virtual env
import elixir
from elixir import *
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlitefktg4sa import SqliteFkTriggerGenerator, auto_assign
import sqlalchemy

# set FK triggers to be genereated on all tables in the metadata
#auto_assign(metadata)
elixir.mycount = 0
class ElixirTests(TestBase):
    count = 0
    def setUp(self):
        if metadata.bind:
            metadata.bind.dispose()
        if os.path.exists('test.sqlite'):
            os.remove('test.sqlite')
        metadata.bind = dbconn
        #metadata.bind.echo = True

        cleanup_all(True)
        
        sys.modules.pop('orm', None)

        from orm import Person
        from orm import Address
        from orm import Phone
        from orm import Email
        from orm import Email2
        from orm import Email3
        from orm import Email4
        
        self.P = Person
        self.A = Address
        self.Ph = Phone
        self.E = Email
        self.E2 = Email2
        self.E3 = Email3
        self.E4 = Email4
        setup_all()
        
        # create foreign keys in meta data
        auto_assign(metadata)
        
        # create tables
        metadata.create_all()
        
        Person(name=u'person 1')
        session.commit()
        session.clear()
    
    def testGoodInsert(self):
        Address = self.A
        Phone = self.Ph
        Person = self.P 
        
        a = Address(street=u'123 main', person_id=1)
        p = Phone(number=u'123456', person_id=1)
        session.commit()
        session.clear()
        
        self.assertEqual(1, Address.query.count())
        self.assertEqual(1, Phone.query.count())
        
        p = Person.get_by(id=1)
        a = Address(street=u'test 2', person=p)
        session.commit()
        
        self.assertEqual(2, Address.query.count())
        
    def testBadInsert(self):
        """ inserting with missing persons id should fail """
        Address = self.A
        Phone = self.Ph
        
        try:
            a = Address(street=u'123 main')
            session.commit()
        except IntegrityError:
            session.rollback()
            pass
        else:
            self.fail("insert null foreign key did not work")
            
        try:
            a = Address(street=u'123 main', person_id=-1)
            session.commit()
        except IntegrityError:
            session.rollback()
            pass
        else:
            self.fail("insert null foreign key did not work")

    def testGoodNullInsert(self):
        Phone = self.Ph
        p = Phone(number=u'123456')
        session.commit()
        self.assertEqual(1, Phone.query.count())

    def testGoodUpdate(self):
        Address = self.A
        Person = self.P
        Phone = self.Ph
        
        a = Address(street=u'1234 main', person_id=1)
        ph = Phone(number=u'12345', person_id=1)
        p = Person(name=u'p2')
        session.commit()
        
        a.person_id = 2
        session.commit()
        a = Address.get_by(id=1)
        self.assertEqual(a.person_id, 2)
        
        ph.person_id = 2
        session.commit()
        ph = Phone.get_by(id=1)
        self.assertEqual(ph.person_id, 2)
        
        ph.person_id = None
        session.commit()
        ph = Phone.get_by(id=1)
        self.assertEqual(ph.person_id, None)        

        self.assertEqual(1, Address.query.count())
        self.assertEqual(2, Person.query.count())
        
    def testBadUpdate(self):
        Address = self.A
        
        a = Address(street=u'1234 main', person_id=1)
        session.commit()
        
        # try to set null
        try:
            a.person_id = None
            session.commit()
        except IntegrityError:
            session.rollback()
            pass
        else:
            self.fail("update FK check failed when setting to None")
        
        # try to set to invalid
        try:
            a.person_id = -2
            session.commit()
        except IntegrityError:
            session.rollback()
            pass
        else:
            self.fail("update FK check failed when setting to invalid number")
    
    def testGoodDelete(self):
        """ deleting main record when no children records exist is ok """
        Person = self.P
        
        p = Person(name=u'p2')
        session.commit()
        
        self.assertEqual(2, Person.query.count())
        
        p.delete()
        session.commit()
        
        self.assertEqual(1, Person.query.count())
        
    def testBadDelete(self):
        """ deleting main record when children exist is an error """
        Address = self.A
        Person = self.P
        
        a = Address(street=u'1234 main', person_id=1)
        session.commit()
            
        self.assertEqual(1, Address.query.count())
        self.assertEqual(1, Person.query.count())
        
        p = Person.get_by(id=1)
        
        try:
            p.delete()
            session.commit()
        except IntegrityError:
            session.rollback()
            pass
        else:
            self.fail("delete foreign key did not work")
            
        self.assertEqual(1, Address.query.count())
        self.assertEqual(1, Person.query.count())
    
    def testNonPassiveNullOkCascadingDelete(self):
        """
            This test actually doesn't work as expected.  The phone
            record *should* be deleted b/c of the cascading delete FK.
            However, sqlalchemy tries to "help" us by setting phone.person_id
            = NULL when the Person record gets deleted.  You have to tell
            sqlalchemy to do passive deletes in order to get this working,
            which we do in future tests.
        """
        Phone = self.Ph
        Person = self.P
        
        ph = Phone(number=u'12345', person_id=1)
        session.commit()
            
        self.assertEqual(1, Phone.query.count())
        self.assertEqual(1, Person.query.count())
        
        p = Person.get_by(id=1)
        p.delete()
        session.commit()
        
        self.assertEqual(0, Person.query.count())
        # Phone count should be 0 if cascading deletes worked as expected,
        # but see note above for this test
        self.assertEqual(1, Phone.query.count())
    
    def testNonPassiveRequiredCascadingDelete(self):
        """
            this shows SQLalchemy trying to be helpful by setting parent_id
            = NULL, but our FK makes that invalid
        """
        Email = self.E
        Person = self.P
        
        e = Email(email=u'a@c.com', person_id=1)
        session.commit()
            
        self.assertEqual(1, Person.query.count())
        self.assertEqual(1, Email.query.count())
        
        p = Person.get_by(id=1)
        p.delete()
        try:
            session.commit()
        except IntegrityError, e:
            session.rollback()
            if 'update on table "emails" violates foreign key' not in str(e):
                raise
        else:
            self.fail("sqlalchemy didn't try to set the child's FK column to NULL as expected")
        
        self.assertEqual(1, Person.query.count())
        self.assertEqual(1, Email.query.count())
    
    def testOraphanedCascadingDelete(self):
        """
            You would think this test shows the FK is working, but really
            sqlalchemy is issuing delete statements for the child objects.
            We need to set it to passive deletes in order to check the FK.
        """
        Email2 = self.E2
        Person = self.P
        
        p = Person.get_by(id=1)
        e = Email2(email=u'a@c.com', person=p)
        session.commit()
            
        self.assertEqual(1, Person.query.count())
        self.assertEqual(1, Email2.query.count())
        
        p.delete()
        session.commit()
        
        self.assertEqual(0, Person.query.count())
        self.assertEqual(0, Email2.query.count())
    
    def testFkWithPassiveDeletes(self):
        """
            This should make SQA stop sending delete statements and
            also allow our FK delete cascade to do its job.
        """
        Email3 = self.E3
        Person = self.P
        
        p = Person.get_by(id=1)
        e = Email3(email=u'a@c.com', person=p)
        session.commit()
            
        self.assertEqual(1, Person.query.count())
        self.assertEqual(1, Email3.query.count())
        
        p.delete()
        session.commit()
        
        self.assertEqual(0, Person.query.count())
        self.assertEqual(0, Email3.query.count())
    
    def testNullOkFkWithPassiveDeletes(self):
        """
            This should make SQA stop sending delete statements and
            also allow our FK delete cascade to do its job.
            
        """
        Email4 = self.E4
        Person = self.P
        
        p = Person.get_by(id=1)
        e = Email4(email=u'a@c.com', person=p)
        session.commit()
            
        self.assertEqual(1, Person.query.count())
        self.assertEqual(1, Email4.query.count())
        
        p.delete()
        session.commit()
        
        self.assertEqual(0, Person.query.count())
        self.assertEqual(0, Email4.query.count())
    
    def tearDown(self):
        self.P = None
        self.A = None
        self.Ph = None
        
if __name__ == "__main__":
    unittest.main()