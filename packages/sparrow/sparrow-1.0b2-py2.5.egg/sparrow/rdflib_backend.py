from cStringIO import StringIO

from zope.interface import implements

try:
    import rdflib
    from rdflib.Graph import Graph, ConjunctiveGraph
    from rdflib.store.IOMemory import IOMemory
except ImportError:
    rdflib = None

from sparrow.error import ConnectionError, DatabaseError, QueryError
from sparrow.interfaces import IConnector, IDatabase
from sparrow.utils import parse_sparql_result

class RDFLibConnector(object):
    implements(IConnector)
    
    def __init__(self, dburi):
        if rdflib is None:
            raise ConnectionError('RDFLib backend is not installed')
        if dburi == 'memory':
            self._store = IOMemory()
        else:
            raise ConnectionError('Unknown database config: %s' % dburi)

    def connect(self):
        return RDFLibDatabase(self._store)
    
    def disconnect(self, db):
        pass

class RDFLibDatabase(object):
    implements(IDatabase)
    def __init__(self, store):
        self._store = store
        self._nsmap = {}
        
    def _rdflib_format(self, format):
        return {'ntriples': 'nt',
                'rdfxml': 'xml',
                'turtle': 'n3',
                'n3': 'n3'}[format]
            
    def formats(self):
        return ['ntriples', 'rdfxml', 'turtle']

    def contexts(self):
        return [c._Graph__identifier.decode('utf8') for c in
                self._store.contexts()]

    def _get_context(self, context_name):
        for ctxt in self._store.contexts():
            if ctxt._Graph__identifier == context_name:
                return ctxt
    
    def register_prefix(self, prefix, namespace):
        self._nsmap[prefix] = namespace


    def _parse(self, graph, file, format, base_uri):
        format = self._rdflib_format(format)
        try:
            graph.parse(file, base_uri, format)
        except rdflib.exceptions.ParserError, err:
            # not sure if this ever happens
            raise DatabaseError(err)
        except Exception, err:
            # each parser throws different errors,
            # there's an ntriples error, but the rdfxml
            # parser throws no errors so you end up with
            # a saxparser exception.
            # The n3 parser just silently fails
            # without any traceback
            raise DatabaseError(err)
        

        
    def add(self, file, format, base_uri, context):
        graph = Graph(self._store, identifier=context)
        self._parse(graph, file, format, base_uri)
        
    def _serialize(self, graph, format):
        format = self._rdflib_format(format)
        for prefix, namespace in self._nsmap.items():
            graph.bind(prefix, namespace)
        return StringIO(graph.serialize(format=format))
        
    def serialize(self, format, context):
        return self._serialize(self._get_context(context), format)
    
    def remove(self, file, format, base_uri, context):
        graph = Graph()
        self._parse(graph, file, format, base_uri)
        context = self._get_context(context)        
        for triple in graph:
            self._store.remove(triple, context)
        
    def clear(self, context):
        context = self._get_context(context)
        self._store.remove((None, None, None), context)
        
    def count(self, context=None):
        context = self._get_context(context)
        
        if not context is None:
            return len(context)
        
        return len(self._store)

    def _query(self, sparql):
        try:
            result = ConjunctiveGraph(self._store).query(sparql)
        except SyntaxError, err:
            raise QueryError(err)
        return result
        
    def select(self, sparql):
        result = self._query(sparql)
        return parse_sparql_result(result.serialize())
        
    def ask(self, sparql):
        result = self._query(sparql)
        return result.askAnswer[0]
    
    def construct(self, sparql, format):
        result = self._query(sparql)
        if not result.construct:
            raise QueryError('CONSTRUCT Query did not return a graph')

        return self._serialize(result.result, format)
        
        
