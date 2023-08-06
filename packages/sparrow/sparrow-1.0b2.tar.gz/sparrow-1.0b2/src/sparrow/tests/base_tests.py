import os
import StringIO
from unittest import TestCase, TestSuite, makeSuite, main

from sparrow.interfaces import IConnector, IDatabase
from sparrow.error import DatabaseError, QueryError

TESTFILE = 'wine'

def open_test_file(format):
    extension = {'rdfxml': '.rdf',
                 'ntriples': '.nt',
                 'turtle': '.ttl'}
    filename = 'wine' + extension[format]
    return open(
        os.path.join(os.path.dirname(__file__), filename), 'r')

class DatabaseConnectionTest(TestCase):
    def test_connect(self):
        self.assertTrue(IConnector.providedBy(self.connector))
        db = self.connector.connect()
        self.assertTrue(IDatabase.providedBy(db))
        self.connector.disconnect(db)

class DatabaseTest(TestCase):

    def test_broken_parsing(self):
        context = 'test'
        base_uri = 'http://example.org'
        for format in self.db.formats():
            # we use '@' as fake data, because 'foo'
            # does not raise any errors in rdflib
            self.assertRaises(
                DatabaseError,
                self.db.add,
                StringIO.StringIO('@'),
                format, base_uri, context)

    def test_rdfxml_parsing(self):
        formats = self.db.formats()
        if 'rdfxml' in formats:
            self._parse('rdfxml')

    def test_ntriples_parsing(self):
        formats = self.db.formats()
        if 'ntriples' in formats:
            self._parse('ntriples')

    def test_turtle_parsing(self):
        formats = self.db.formats()
        if 'turtle' in formats:
            self._parse('turtle')

    def test_base_uri_parsing(self):
        if not 'rdfxml' in self.db.formats():
            return
        data = StringIO.StringIO('''<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
 <rdf:Description rdf:about="">
  <foo:name xmlns:foo="http://foobar.com#">bar</foo:name>
 </rdf:Description>
</rdf:RDF>''')
        self.db.add(data, 'rdfxml', 'http://example.org', 'test')
        result = self.db.serialize('ntriples', 'test').read()
        self.assertEquals(result.strip()[:-1].strip(),
                          '<http://example.org> <http://foobar.com#name> "bar"')
        
    def test_remove_statements(self):
        self._parse()

        fp = StringIO.StringIO(
            '<http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine> '
            '<http://www.w3.org/2000/01/rdf-schema#label> '
            '"Wine Ontology" .\n')
        
        self.db.remove(fp, 'ntriples', 'file://wine.rdf', 'test')
        fp = self._serialize('ntriples')
        data = fp.read()
        self.assertTrue('Wine Ontology' not in data)

    def test_ntriples_serializing(self):
        formats = self.db.formats()
        if not 'ntriples' in formats:
            return

        self._parse()
        fp = self._serialize('ntriples')
        data = fp.read()
        self.assertTrue('Wine Ontology' in data)

    def test_rdfxml_serializing(self):
        formats = self.db.formats()
        if not 'rdfxml' in formats:
            return

        self._parse()
        self.db.register_prefix(
            'vin',
            'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#')
        fp = self._serialize('rdfxml')
        data = fp.read()
        fp.close()
        self.assertTrue('Wine Ontology' in data)
        self.assertTrue('xmlns:vin' in data)

    def test_turtle_serializing(self):
        formats = self.db.formats()
        if not 'turtle' in formats:
            return
        
        self._parse()
        self.db.register_prefix(
            'vin',
            'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#')
        fp = self._serialize('turtle')
        data = fp.read()
        fp.close()
        self.assertTrue('Wine Ontology' in data)
        self.assertTrue('@prefix vin' in data)
        
    def test_clear(self):
        count = self.db.count('test')
        if count is None:
            return
        self.assertEquals(count , 0)
        self._parse()
        count = self.db.count()
        self.assertTrue(count > 1500)
        self.db.clear('test')
        count = self.db.count()
        self.assertEquals(count , 0)

    def test_contexts(self):
        self.assertEquals(list(self.db.contexts()), [])
        self._parse(format=None, context='a')
        self._parse(format=None, context='b')
        self._parse(format=None, context='c')
        self.assertEquals(sorted(list(self.db.contexts())), [u'a', u'b', u'c'])
        self.db.clear('b')
        self.assertEquals(sorted(list(self.db.contexts())), [u'a', u'c'])
        self.db.clear('a')
        self.db.clear('c')
        self.assertEquals(list(self.db.contexts()), [])

    def _serialize(self, format=None, context='test'):
        if format is None:
            formats = self.db.formats()
            for format in formats:
                if format in ['ntriples', 'rdfxml', 'turtle']:
                    break
                else:
                    return
        return self.db.serialize(format, context)
    
    def _parse(self, format=None, context='test'):
        if format is None:
            formats = self.db.formats()
            for format in formats:
                if format in ['ntriples', 'rdfxml', 'turtle']:
                    break
                else:
                    return
        fp = open_test_file(format)
        base_uri = 'file://wine.rdf'
        self.db.add(fp, format, base_uri, context)
        fp.close()
        
        triples = self.db.count(context) or self.db.count()
        if not triples is None:
            self.assertTrue(triples > 1500)
        
    
class DatabaseQueryTest(TestCase):
    def test_ask(self):
        q = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>        
        ASK { ?x rdfs:label "Wine Ontology"}
        """
        self.assertTrue(self.db.ask(q))
        q = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>        
        ASK { ?x rdfs:label "FooBar"}
        """
        self.assertFalse(self.db.ask(q))

    def test_select(self):
        q = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX vin: <http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#>
        SELECT ?grape
        WHERE { ?grape a vin:WineGrape .}
        """
        result = self.db.select(q)
        self.assertEquals(len(result), 16)
        grapes = sorted(
            [r['grape']['value'].split('#')[-1] for r in result])
        
        self.assertEquals(grapes, [
            u'CabernetFrancGrape', u'CabernetSauvignonGrape',
            u'ChardonnayGrape', u'CheninBlancGrape', u'GamayGrape',
            u'MalbecGrape', u'MerlotGrape', u'PetiteSyrahGrape',
            u'PetiteVerdotGrape', u'PinotBlancGrape', u'PinotNoirGrape',
            u'RieslingGrape', u'SangioveseGrape', u'SauvignonBlancGrape',
            u'SemillonGrape', u'ZinfandelGrape'])

    def test_select_literal_language(self):
        q = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX vin: <http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#>
        SELECT ?label
        WHERE { vin:Wine rdfs:label ?label .}
        """
        result = self.db.select(q)
        self.assertEquals(sorted(result),
                          [{u'label': {'type': u'literal',
                                       'value': u'vin',
                                       'xml:lang': u'fr'}},
                           {u'label': {'type': u'literal',
                                       'value': u'wine',
                                       'xml:lang': u'en'}}])

    def test_select_literal_datatype(self):
        q = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX vin: <http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#>
        SELECT ?year
        WHERE { vin:Year1998 vin:yearValue ?year .}
        """
        result = self.db.select(q)
        self.assertEquals(
            sorted(result),
            [{u'year': {
            'type': u'literal',
            'value': u'1998',
            'datatype': u'http://www.w3.org/2001/XMLSchema#positiveInteger'}}])
        
    def test_construct(self):
        q = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>        
        CONSTRUCT {?x rdfs:label "Wine Ontology"}
        WHERE { ?x rdfs:label "Wine Ontology" .}
        """
        fp = self.db.construct(q, 'ntriples')
        self.assertEquals(
            fp.read().strip()[:-1].strip(),
            ('<http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine> '
             '<http://www.w3.org/2000/01/rdf-schema#label> "Wine Ontology"'))
        fp.close()
        
    def test_broken_query(self):
        self.assertRaises(QueryError,
                          self.db.select,
                          'foo')
        self.assertRaises(QueryError,
                          self.db.ask,
                          'foo')
        self.assertRaises(QueryError,
                          self.db.construct,
                          'foo', 'rdfxml')
        
