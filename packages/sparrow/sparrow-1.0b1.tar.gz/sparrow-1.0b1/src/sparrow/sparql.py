from lxml import etree
from simplejson import JSONEncoder
from zope.interface import implements

from sparrow.interfaces import ISPARQLResult

SPARQLNS = u'http://www.w3.org/2005/sparql-results#'

class SPARQLXMLResult(object):
    implements(ISPARQLResult)
    
    def __init__(self, xml):
        self._doc = etree.fromstring(xml)
        self._dict = self._make_dict()

    def _make_dict(self):
        vars = []
        for var in self._doc.xpath('/s:sparql/s:head/s:variable/@name',
                                   namespaces={'s': SPARQLNS}):
            vars.append(unicode(var))
            
        results = []
        for result in self._doc.xpath('/s:sparql/s:results/s:result',
                                      namespaces={'s': SPARQLNS}):
            data = {}
            for binding in result:
                name = unicode(binding.attrib['name'])
                for value in binding:
                    type = unicode(value.tag.split('}')[-1])
                    text = value.text
                    if not text is None and not isinstance(text, unicode):
                        text = text.decode('utf8')
                    data[name] = {'value': text,
                                  'type': type}
            results.append(data)
        
        return {"head" :{"link": [],
                         "vars": vars},
                "results": {"bindings": results }}

    def variables(self):
        return self._dict['head']['vars']

    def results(self):
        return self._dict['results']['bindings']
    
    def __iter__(self):
        for binding in self._dict['results']['bindings']:
            yield binding
    
    def to_json(self):
        encoder = JSONEncoder(sort_keys=True, indent=2)
        return encoder.encode(self._dict)
