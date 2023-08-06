import os
from unittest import TestCase, TestSuite, makeSuite, main

import sparrow
from sparrow.error import ConnectionError
from sparrow.tests.base_tests import (DatabaseConnectionTest,
                                      DatabaseTest,
                                      DatabaseQueryTest,
                                      open_test_file)


# To run these tests, make sure the allegro.cfg buildout profile is used
# this will export a 'ALLEGRO_HOST' and 'ALLEGRO_PORT' variable to
# the environ dict which is used by this test to determine where
# the allegro server is running.

# The allegro server will need to be configured with a repository called
# 'test' this repository can be a simple in memory database.
# Run the configure_allegro tool to generate the test repository, and add the
# working repository as specified in the buildout profile

class AllegroConnectionTest(DatabaseConnectionTest):
    def setUp(self):
        self.connector = sparrow.database('allegro', get_allegro_url())

    def tearDown(self):
        del self.connector

class AllegroTest(DatabaseTest):
    def setUp(self):
        self.connector = sparrow.database('allegro', get_allegro_url())
        self.db = self.connector.connect()

    def tearDown(self):
        self.db.clear('test')
        self.connector.disconnect(self.db)
        del self.db
        del self.connector

class AllegroQueryTest(DatabaseQueryTest):
    def setUp(self):
        self.connector = sparrow.database('allegro', get_allegro_url())
        self.db = self.connector.connect()
        fp = open_test_file('ntriples')
        self.db.add(fp, 'ntriples','file://wine.nt', 'test')
        fp.close()
        
    def tearDown(self):
        self.db.clear('test')
        self.connector.disconnect(self.db)
        del self.db
        del self.connector
    
def get_allegro_url():
    # host and port variables are set from
    # the buildout script (see profiles/allegro.cfg)
    url = 'http://%s:%s/test' % (os.environ.get('ALLEGRO_HOST', 'localhost'),
                                 os.environ.get('ALLEGRO_PORT', '8000'))
    return url

def test_suite():
    try:
        sparrow.database('allegro', get_allegro_url())
    except ConnectionError, err:
        # allegro not running?
        return TestSuite()

    suite = TestSuite()
    suite.addTest(makeSuite(AllegroConnectionTest))
    suite.addTest(makeSuite(AllegroTest))
    #suite.addTest(makeSuite(AllegroQueryTest))
    return suite

if __name__ == '__main__':

    main(defaultTest='test_suite')
