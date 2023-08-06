import os, sys
from os.path import join
from urllib import quote, urlencode

import httplib2
from zope.interface import implements

from sparrow.error import ConnectionError, DatabaseError, QueryError
from sparrow.interfaces import IConnector, IDatabase
from sparrow.utils import parse_sparql_result
from sparrow.sesame_backend import SesameDatabase

class AllegroConnector(object):
    implements(IConnector)
        
    def __init__(self, dburi):
        self._host, rest = dburi[7:].split(':', 1)
        self._port, self._name = rest.split('/', 1)
        
        self._url = 'http://%s:%s/sesame' % (self._host, self._port)
        http = httplib2.Http()
        params = urlencode({'id': self._name,
                            'if-exists': 'open'})
        try:
            resp, content = http.request(
                '%s/repositories?%s' % (self._url, params),
                "POST")
        except socket.error:
            raise ConnectionError(
                'Can not connect to repository, is it running?')
        
        if resp['status'] != '204':
            raise ConnectionError(
                'Can not connect to server: %s' % resp['status'])
        
    def connect(self):
        return AllegroDatabase(self._url, self._name)
    
    def disconnect(self, db):
        del db._http

class AllegroDatabase(SesameDatabase):
    def formats(self):
        return ['rdfxml', 'ntriples']


def start_server(host, port, path):
    part_dir = join(path ,'parts', 'allegro-install')
    allegro_dir = join(part_dir,
                       [d for d in os.listdir(part_dir) if
                        d.startswith('agraph')][0])

    allegro_cmd = join(allegro_dir, 'AllegroGraphServer')
    os.system('%s --http-port %s' % (allegro_cmd, port))
    fp = open(join(allegro_dir, 'agraph.pid'), 'r')
    pid = fp.read().strip()
    fp.close()
    
    print >> sys.stderr, 'Started Allegro server on port %s (pid %s)' % (
        port, pid)
    
    
