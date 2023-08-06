from unittest import TestCase, TestSuite, makeSuite, main

import sparrow
from sparrow.error import ConnectionError
from sparrow.tests.base_tests import (DatabaseConnectionTest,
                                      DatabaseTest,
                                      DatabaseQueryTest,
                                      open_test_file)

class RedlandConnectionTest(DatabaseConnectionTest):
    def setUp(self):
        self.connector = sparrow.database('redland', 'memory')

    def tearDown(self):
        del self.connector

class RedlandTest(DatabaseTest):
    def setUp(self):
        self.connector = sparrow.database('redland', 'memory')
        self.db = self.connector.connect()

    def tearDown(self):
        self.connector.disconnect(self.db)
        del self.db
        del self.connector

class RedlandQueryTest(DatabaseQueryTest):
    def setUp(self):
        self.connector = sparrow.database('redland', 'memory')
        self.db = self.connector.connect()
        fp = open_test_file('ntriples')
        self.db.add_triples(fp, 'ntriples','wine.nt', 'test')
        fp.close()
        
    def tearDown(self):
        self.connector.disconnect(self.db)
        del self.db
        del self.connector
    

def test_suite():
    try:
        sparrow.database('redland', 'memory')
    except ConnectionError:
        # redland / librdf not installed?
        return TestSuite()
    suite = TestSuite()
    suite.addTest(makeSuite(RedlandConnectionTest))
    suite.addTest(makeSuite(RedlandTest))
    suite.addTest(makeSuite(RedlandQueryTest))
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
