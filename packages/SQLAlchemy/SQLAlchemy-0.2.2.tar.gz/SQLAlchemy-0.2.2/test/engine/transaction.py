
import testbase
import unittest, sys, datetime
import tables
db = testbase.db
from sqlalchemy import *


class TransactionTest(testbase.PersistTest):
    def setUpAll(self):
        global users, metadata
        metadata = MetaData()
        users = Table('query_users', metadata,
            Column('user_id', INT, primary_key = True),
            Column('user_name', VARCHAR(20)),
        )
        users.create(testbase.db)
    
    def tearDown(self):
        testbase.db.connect().execute(users.delete())
    def tearDownAll(self):
        users.drop(testbase.db)
    
    @testbase.unsupported('mysql')
    def testrollback(self):
        """test a basic rollback"""
        connection = testbase.db.connect()
        transaction = connection.begin()
        connection.execute(users.insert(), user_id=1, user_name='user1')
        connection.execute(users.insert(), user_id=2, user_name='user2')
        connection.execute(users.insert(), user_id=3, user_name='user3')
        transaction.rollback()
        
        result = connection.execute("select * from query_users")
        assert len(result.fetchall()) == 0
        connection.close()

    @testbase.unsupported('mysql')
    def testnesting(self):
        connection = testbase.db.connect()
        transaction = connection.begin()
        connection.execute(users.insert(), user_id=1, user_name='user1')
        connection.execute(users.insert(), user_id=2, user_name='user2')
        connection.execute(users.insert(), user_id=3, user_name='user3')
        trans2 = connection.begin()
        connection.execute(users.insert(), user_id=4, user_name='user4')
        connection.execute(users.insert(), user_id=5, user_name='user5')
        trans2.commit()
        transaction.rollback()
        self.assert_(connection.scalar("select count(1) from query_users") == 0)

        result = connection.execute("select * from query_users")
        assert len(result.fetchall()) == 0
        connection.close()
        
class AutoRollbackTest(testbase.PersistTest):
    def setUpAll(self):
        global metadata
        metadata = MetaData()
    
    def tearDownAll(self):
        metadata.drop_all(testbase.db)
        
    @testbase.unsupported('sqlite')
    def testrollback_deadlock(self):
        """test that returning connections to the pool clears any object locks."""
        conn1 = testbase.db.connect()
        conn2 = testbase.db.connect()
        users = Table('deadlock_users', metadata,
            Column('user_id', INT, primary_key = True),
            Column('user_name', VARCHAR(20)),
        )
        users.create(conn1)
        conn1.execute("select * from deadlock_users")
        conn1.close()
        # without auto-rollback in the connection pool's return() logic, this deadlocks in Postgres, 
        # because conn1 is returned to the pool but still has a lock on "deadlock_users"
        # comment out the rollback in pool/ConnectionFairy._close() to see !
        users.drop(conn2)
        conn2.close()

class TLTransactionTest(testbase.PersistTest):
    def setUpAll(self):
        global users, metadata, tlengine
        tlengine = create_engine(testbase.db_uri, strategy='threadlocal', echo=True)
        metadata = MetaData()
        users = Table('query_users', metadata,
            Column('user_id', INT, primary_key = True),
            Column('user_name', VARCHAR(20)),
        )
        users.create(tlengine)
    def tearDown(self):
        tlengine.execute(users.delete())
    def tearDownAll(self):
        users.drop(tlengine)
        tlengine.dispose()
        
    @testbase.unsupported('mysql')
    def testrollback(self):
        """test a basic rollback"""
        tlengine.begin()
        tlengine.execute(users.insert(), user_id=1, user_name='user1')
        tlengine.execute(users.insert(), user_id=2, user_name='user2')
        tlengine.execute(users.insert(), user_id=3, user_name='user3')
        tlengine.rollback()

        external_connection = tlengine.connect()
        result = external_connection.execute("select * from query_users")
        try:
            assert len(result.fetchall()) == 0
        finally:
            external_connection.close()

    @testbase.unsupported('mysql')
    def testcommit(self):
        """test a basic commit"""
        tlengine.begin()
        tlengine.execute(users.insert(), user_id=1, user_name='user1')
        tlengine.execute(users.insert(), user_id=2, user_name='user2')
        tlengine.execute(users.insert(), user_id=3, user_name='user3')
        tlengine.commit()

        external_connection = tlengine.connect()
        result = external_connection.execute("select * from query_users")
        try:
            assert len(result.fetchall()) == 3
        finally:
            external_connection.close()

    @testbase.unsupported('mysql', 'sqlite')
    def testnesting(self):
        """tests nesting of tranacstions"""
        external_connection = tlengine.connect()
        self.assert_(external_connection.connection is not tlengine.contextual_connect().connection)
        tlengine.begin()
        tlengine.execute(users.insert(), user_id=1, user_name='user1')
        tlengine.execute(users.insert(), user_id=2, user_name='user2')
        tlengine.execute(users.insert(), user_id=3, user_name='user3')
        tlengine.begin()
        tlengine.execute(users.insert(), user_id=4, user_name='user4')
        tlengine.execute(users.insert(), user_id=5, user_name='user5')
        tlengine.commit()
        tlengine.rollback()
        try:
            self.assert_(external_connection.scalar("select count(1) from query_users") == 0)
        finally:
            external_connection.close()

    @testbase.unsupported('mysql')
    def testmixednesting(self):
        """tests nesting of transactions off the TLEngine directly inside of 
        tranasctions off the connection from the TLEngine"""
        external_connection = tlengine.connect()
        self.assert_(external_connection.connection is not tlengine.contextual_connect().connection)
        conn = tlengine.contextual_connect()
        trans = conn.begin()
        trans2 = conn.begin()
        tlengine.execute(users.insert(), user_id=1, user_name='user1')
        tlengine.execute(users.insert(), user_id=2, user_name='user2')
        tlengine.execute(users.insert(), user_id=3, user_name='user3')
        tlengine.begin()
        tlengine.execute(users.insert(), user_id=4, user_name='user4')
        tlengine.begin()
        tlengine.execute(users.insert(), user_id=5, user_name='user5')
        tlengine.execute(users.insert(), user_id=6, user_name='user6')
        tlengine.execute(users.insert(), user_id=7, user_name='user7')
        tlengine.commit()
        tlengine.execute(users.insert(), user_id=8, user_name='user8')
        tlengine.commit()
        trans2.commit()
        trans.rollback()
        conn.close()
        try:
            self.assert_(external_connection.scalar("select count(1) from query_users") == 0)
        finally:
            external_connection.close()

    @testbase.unsupported('mysql')
    def testmoremixednesting(self):
        """tests nesting of transactions off the connection from the TLEngine
        inside of tranasctions off thbe TLEngine directly."""
        external_connection = tlengine.connect()
        self.assert_(external_connection.connection is not tlengine.contextual_connect().connection)
        tlengine.begin()
        connection = tlengine.contextual_connect()
        connection.execute(users.insert(), user_id=1, user_name='user1')
        tlengine.begin()
        connection.execute(users.insert(), user_id=2, user_name='user2')
        connection.execute(users.insert(), user_id=3, user_name='user3')
        trans = connection.begin()
        connection.execute(users.insert(), user_id=4, user_name='user4')
        connection.execute(users.insert(), user_id=5, user_name='user5')
        trans.commit()
        tlengine.commit()
        tlengine.rollback()
        connection.close()
        try:
            self.assert_(external_connection.scalar("select count(1) from query_users") == 0)
        finally:
            external_connection.close()

    def testsessionnesting(self):
        class User(object):
            pass
        try:
            mapper(User, users)

            sess = create_session(bind_to=tlengine)
            print "STEP1"
            tlengine.begin()
            print "STEP2"
            u = User()
            sess.save(u)
            print "STEP3"
            sess.flush()
            print "STEP4"
            tlengine.commit()
            print "STEP5"
        finally:
            clear_mappers()

    def testconnections(self):
        """tests that contextual_connect is threadlocal"""
        c1 = tlengine.contextual_connect()
        c2 = tlengine.contextual_connect()
        assert c1.connection is c2.connection
        c2.close()
        assert c1.connection.connection is not None
        
if __name__ == "__main__":
    testbase.main()        
