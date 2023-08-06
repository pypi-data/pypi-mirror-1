from cStringIO import StringIO

from zope.interface import implements

try:
    import RDF
except ImportError:
    RDF = None

from sparrow.error import ConnectionError, DatabaseError, QueryError
from sparrow.interfaces import IConnector, IDatabase
from sparrow.utils import parse_sparql_result

class RedlandConnector(object):
    implements(IConnector)
    
    def __init__(self, dburi):
        self._model = model_from_uri(dburi, contexts='yes')

    def connect(self):
        return RedlandDatabase(self._model)
    
    def disconnect(self, db):
        pass

class RedlandDatabase(object):
    implements(IDatabase)
    
    def __init__(self, model):
        self._model = model
        self._nsmap = {}
        
    def formats(self):
        return ['ntriples', 'rdfxml', 'turtle']

    def contexts(self):
        return [c.literal_value['string'].decode('utf8') for c in
                self._model.get_contexts()]

    def register_prefix(self, prefix, namespace):
        self._nsmap[prefix] = namespace
        
    def _parse(self, file, format, base_uri):
        if format == 'turtle':
            parser = RDF.TurtleParser()
        else:
            parser = RDF.Parser(format)

        if isinstance(base_uri, unicode):
            base_uri = base_uri.encode('utf8')
        try:
            stream = parser.parse_string_as_stream(file.read(), base_uri)
        except RDF.RedlandError, err:
            raise DatabaseError(err)
        if stream is None:
            raise DatabaseError('Parsing RDF Failed')
        return stream

    def _serialize(self, stream, format):
        # this sucks, we need a temp model because contexts can not
        # be serialized :(

        temp = model_from_uri('memory')
        temp.add_statements(stream)
        serializer = RDF.Serializer(name=format)
        for prefix, ns in self._nsmap.items():
            serializer.set_namespace(prefix, ns)
        return StringIO(serializer.serialize_model_to_string(temp))
        
    def add(self, file, format, base_uri, context):
        if isinstance(context, unicode):
            context = unicode.encode('utf8')
        
        stream = self._parse(file, format, base_uri)
        self._model.add_statements(stream, RDF.Node(context))

    def serialize(self, format, context):

        if isinstance(context, unicode):
            context = unicode.encode('utf8')
            
        stream = self._model.as_stream(RDF.Node(context))

        return self._serialize(stream, format)

    def remove(self, file, format, base_uri, context):
        if isinstance(context, unicode):
            context = context.encode('utf8')
        context = RDF.Node(context)
        
        stream = self._parse(file, format, base_uri)
        for statement in stream:
            self._model.remove_statement(statement, context)
        
    def clear(self, context):
        if isinstance(context, unicode):
            context = context.encode('utf8')
        self._model.remove_statements_with_context(RDF.Node(context))
    
    def count(self, context=None):
        result = None
        if context is None:
            result = len(self._model)
        return result

    def _query(self, sparql):
        if isinstance(sparql, unicode):
            sparql = sparql.encode('utf8')
        query = RDF.SPARQLQuery(sparql)
        
        try:
            result = query.execute(self._model)
        except RDF.RedlandError, err:
            raise QueryError(err)
        return result

    def select(self, sparql):
        result = self._query(sparql)
        if not result.is_bindings():
            raise QueryError('SELECT Query did not return bindings')
        return parse_sparql_result(result.to_string())
        
    def ask(self, sparql):
        result = self._query(sparql)
        if not result.is_boolean():
            raise QueryError('ASK Query did not return a boolean')
        
        return result.get_boolean()

    def construct(self, sparql, format):
        result = self._query(sparql)
        if not result.is_graph():
            raise QueryError('CONSTRUCT Query did not return a graph')
        
        m = RDF.Model()
        stream = result.as_stream()
        if stream is None:
            return
        return self._serialize(stream, format)

    
def model_from_uri(uri=None, **opts):
    if RDF is None:
        raise ConnectionError(
            'Redland support is not available, install from librdf.org')
    
    options = []
    for key, val in opts.items():
        options.append("%s='%s'" % (key, val))
        
    options = ','.join(options)
    if uri == None or uri == 'memory':
        options += ",hash-type='memory'"
        store = RDF.Storage(storage_name='hashes',
                            name='memory_store',
                            options_string=options)
    elif uri.startswith('sqlite://'):
        file = uri[9:]
        try:
            store = RDF.Storage(storage_name='sqlite',
                                name=file,
                                options_string=options)
        except RDF.RedlandError:
            raise ConnectionError("Can't connect to %s" % uri)
    elif uri.startswith('bdb://'):
        file = uri[6:]
        if not os.path.isfile(file+'-sp2o.db') and not 'new=' in options:
            options += ",new='yes'"
        options += ",hash-type='bdb'"
        store = RDF.Storage(storage_name='hashes',
                            name=file,
                            options_string=options)
    elif uri.startswith('mysql://'):
        uri = uri[8:]
        userpass, hostdb = uri.split('@')
        user, pwd = userpass.split(':')
        host, db = hostdb.split('/')
        if ':' in host:
            host, port = host.split(':')
        else:
            port = '3306'
        if '#' in db:
            db, name = db.split('#')
        else:
            name = 'main'

        options += (",host='%s',port='%s',database='%s',user='%s',"
                    "password='%s'" % (host, port, db, user, pwd))
        try:
            store = RDF.Storage(storage_name='mysql',
                                name=name,
                                options_string=options)
        except RDF.RedlandError:
            raise ConnectionError("Can't connect to %s" % uri)
    else:
        raise ConnectionError('Unknown dburi: %s' % uri)
        
    return RDF.Model(store)

    
