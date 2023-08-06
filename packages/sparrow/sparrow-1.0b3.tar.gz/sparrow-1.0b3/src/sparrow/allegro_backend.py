import os, sys
from os.path import join
from urllib import quote, urlencode
import socket
from StringIO import StringIO
import httplib2
from zope.interface import implements

from sparrow.error import ConnectionError, TripleStoreError, QueryError
from sparrow.interfaces import ITripleStore, ISPARQLEndpoint
from sparrow.utils import (parse_sparql_result,
                           ntriples_to_json,
                           ntriples_to_dict)

from sparrow.sesame_backend import SesameTripleStore

class AllegroTripleStore(SesameTripleStore):
    def connect(self, dburi):
        host, rest = dburi[7:].split(':', 1)
        port, self._name = rest.split('/', 1)
        
        self._url = 'http://%s:%s/sesame' % (host, port)
        self._http = httplib2.Http()
        params = urlencode({'id': self._name,
                            'if-exists': 'open'})
        try:
            resp, content = self._http.request(
                '%s/repositories?%s' % (self._url, params),
                "POST")
        except socket.error:
            raise ConnectionError(
                'Can not connect to repository, is it running?')
        
        if resp['status'] != '204':
            raise ConnectionError(
                'Can not connect to server: %s' % resp['status'])
        
    def _turtle_to_ntriples(self, data):
        # Turtle syntax is not supported by allegro graph
        # HACK workaround using redland
        import RDF
        model = RDF.Model()
        parser = RDF.TurtleParser()
        try:
            parser.parse_string_into_model(model, data.read(),'-')
        except RDF.RedlandError, err:
            raise TripleStoreError(err)
        
        serializer = RDF.Serializer(name='ntriples')
        return StringIO(serializer.serialize_model_to_string(model))
        
    def _rdfxml_to_ntriples(self, data):
        # Ntriples syntax is not supported by allegro graph
        # as a result format for SPARQL Construct Queries
        # HACK workaround using redland
        import RDF
        model = RDF.Model()
        parser = RDF.Parser()
        try:
            parser.parse_string_into_model(model, data.read(),'-')
        except RDF.RedlandError, err:
            raise TripleStoreError(err)
        
        serializer = RDF.Serializer(name='ntriples')
        return StringIO(serializer.serialize_model_to_string(model))
        
    def _ntriples_to_turtle(self, data):
        # Turtle syntax is not supported by allegro graph
        # HACK workaround using redland
        import RDF
        model = RDF.Model()
        parser = RDF.Parser('ntriples')
        data = data.read()
        data = (data.strip() + '\n')
        try:
            parser.parse_string_into_model(model, data,'-')
        except RDF.RedlandError, err:
            raise TripleStoreError(err)
        
        serializer = RDF.Serializer(name='turtle')
        for prefix, ns in self._nsmap.items():
            serializer.set_namespace(prefix, ns)
        return StringIO(serializer.serialize_model_to_string(model))

    def add_turtle(self, data, context):
        data = self._get_file(data)
        data = self._turtle_to_ntriples(data)
        self.add_ntriples(data, context)
        
    def remove_turtle(self, data, context):
        data = self._get_file(data)
        data = self._turtle_to_ntriples(data)
        self.remove_ntriples(data, context)

    def get_turtle(self, context):
        data = self.get_ntriples(context)
        return self._ntriples_to_turtle(data)

    def construct(self, query, format):
        result =  super(AllegroTripleStore, self).construct(query, 'rdfxml')
        if format == 'rdfxml':
            return result
        
        result = self._rdfxml_to_ntriples(result)
        if format == 'ntriples':
            return result
        elif format == 'json':
            return  ntriples_to_json(result)
        elif format == 'dict':
            return ntriples_to_dict(result)
        elif format == 'turtle':
            return self._ntriples_to_turtle(result)



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

    # create storage directory for test repository
    if not os.path.isdir('test'):
        os.mkdir('test')
    
    print >> sys.stderr, 'Started Allegro server on port %s (pid %s)' % (
        port, pid)
    
    
