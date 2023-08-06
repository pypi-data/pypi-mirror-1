from lxml import etree

SPARQLNS = u'http://www.w3.org/2005/sparql-results#'

def parse_sparql_result(xml):
    doc = etree.fromstring(xml)
    results = []
    for result in doc.xpath('/s:sparql/s:results/s:result',
                            namespaces={'s': SPARQLNS}):
        data = {}
        for binding in result:
            name = unicode(binding.attrib['name'])
            for value in binding:
                type = unicode(value.tag.split('}')[-1])
                lang = value.attrib.get(
                    '{http://www.w3.org/XML/1998/namespace}lang')
                datatype = value.attrib.get('datatype')
                text = value.text
                if not text is None and not isinstance(text, unicode):
                    text = text.decode('utf8')

                if type == 'uri':
                    # allegro graph returns context uri's with <> chars
                    if text.startswith('<'):
                        text = text[1:]
                    if text.endswith('>'):
                        text = text[:-1]
                    
                data[name] = {'value': text,
                              'type': type}
                if not lang is None:
                    data[name]['xml:lang'] = lang.decode('utf8')
                if not datatype is None:
                    data[name]['datatype'] = datatype.decode('utf8')

        results.append(data)
    return results
