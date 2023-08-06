from zope.interface import Interface, Attribute

class IConnector(Interface):
    def connect():
        """
        Connect to database, retrieve an IDatabase instance
        """
    def disconnect(db):
        """
        Disconnect the database
        """

class IDatabase(Interface):

    def formats():
        """
        Return a list of string identifiers describing the
        different rdf serialization formats that the database
        supports. Examples are:
        ntriples, rdfxml, rdfxml-abbrev, turtle, n3
        """
        
    def contexts():
        """
        Return a list of context names
        """
    
    def add(file, format_name, base_uri, context_name):
        """
        Add triples from filestream with triples data in a
        specific format. A base_uri should be supplied.
        Triples are always added in a specific context
        """

    def remove(file, format_name, base_uri, context_name):
        """
        Remove triples from a filestream with triples data in
        a specifc format.
        """

    def serialize(format_name, context_name):
        """
        Return a filestream object with triples data in a
        specific format
        """
        
    def clear(context_name):
        """
        Remove all triples from a context
        """

    def register_prefix(prefix, namespace):
        """
        Register a namespace with a specific prefix
        These will be used in serializing rdfxml
        if backend supports this
        """

    def count(context_name=None):
        """
        Return the number of triples in the database or
        None if the backend does not support this
        Optionally a context_name can be specified
        """

    def select(sparql_query):
        """
        Run a sparql SELECT query, returns a list
        of dictionaries in sparql result format (json-like)
        """

    def ask(sparql_query):
        """
        Run a sparql ASK query, returns a boolean
        """
    def construct(sparql_query, format):
        """
        Run a sparql CONSTRUCT query, returns a
        filestream with triples in the specifed format
        or None if no result was found
        """
        
