
Sparrow
=======

Introduction
------------

Sparrow is a library that provides a very high-level abstraction for
RDF Databases. It provides support for the following basic functions:

 * Parsing RDF statements from different formats into a contextual database
 * Serializing the RDF statements for a specific context of a database
 * Removing statements from a specific context of a database
 * Performing SPARQL Queries

Sparrow is completely agnostic to which database backend is used.
RDF Statements are loaded into and from databases in specific serialization
formats like rdfxml, ntriples or turtle. 

Sparrow provides no API for Statements, URIRef and Literal objects. 
It also does not provide a graph API. This is an intentional choice, 
since the goal of Sparrow is not to provide a full RDF library, but a
lightweight wrapper that can easily be used for several backends.
 

At the moment there is support for the following backends:

 * Redland librdf
 * RDFLib
 * Sesame openrdf

Usage
-----

Normally, you will only need to import the base sparrow module

>>> import sparrow

Most of the database backends will not work out of the box. 
Since the RDFLib backend is written in python and packaged on pypi,
it is always available, and installed with Sparrow.

Let's create an in memory rdflib database

>>> sparrow.database('rdflib', 'memory')
<sparrow.rdflib_backend.RDFLibConnector ...>

This is actually not the database, but a database connector.
It manages the different connections to a database.
Let's get a connection to the database

>>> db = sparrow.database('rdflib', 'memory').connect()
>>> db
<sparrow.rdflib_backend.RDFLibDatabase ...>

Now that we have the database, we can ask it which RDF serialization
formats it supports

>>> db.formats()
['ntriples', 'rdfxml', 'turtle']

Let's add some triples to the database, we will use turtle syntax for this.
We'll make some example statements where we will state that john is a person,
and that his firstname is "John".

>>> data = """@prefix ex: <http://example.org#> .
... ex:john a ex:Person; ex:name "John" ."""

Now we can add this to the database. We will need to tell the database 
which format the data is in, and in which context to store it.
A 'base URI' for the data should also be provided. We will use the 
example.org namespace for that.

>>> db.add_triples(StringIO(data), 'turtle', 'http://example.org','persons')

We can now ask the database, which contexts it has:

>>> db.contexts()
[u'persons']

You can store data in as many different contexts as you like, or put everything
in a single context.

Lets do a simple SPARQL query on the database

>>> result = db.select('SELECT ?x {?x <http://example.org#name> "John".}')

The is only on variable in this query: `x`

>>> result.variables()
[u'x']

We can get the results as a list of dictionaries. This follows the SPARQL
JSON result format.

>>> result.results()
[{u'x': {'type': u'uri', 'value': u'http://example.org#john'}}]

Besides querying, we can also get the data back from the database in any
of the supported formats. We specify which format we want, and which context
to use.

>>> db.serialize_triples('ntriples', 'persons').read()
'<http://example.org#john> ...'

If the database backend supports it, you can ask how many triples are in a 
context.

>>> db.count('persons')
2

If you want to remove triples, you will need to supply data describing which
triples to remove.

>>> data = StringIO('<http://example.org#john> a <http://example.org#Person>.')
>>> db.remove_triples(data, 'turtle', 'http://example.org', 'persons')
>>> db.count('persons')
1

You can also remove all triples in a context

>>> db.clear('persons')
>>> db.count('persons')
0

Since the 'persons' context is now empty, it is also removed.

>>> db.contexts()
[]
