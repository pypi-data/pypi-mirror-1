
from sparrow.redland_backend import RedlandConnector
from sparrow.rdflib_backend import RDFLibConnector
from sparrow.sesame_backend import SesameConnector
from sparrow.allegro_backend import AllegroConnector

def database(backend, dburi):
    if backend == 'redland':
        return RedlandConnector(dburi)
    elif backend == 'rdflib':
        return RDFLibConnector(dburi)
    elif backend == 'sesame':
        return SesameConnector(dburi)
    elif backend == 'allegro':
        return AllegroConnector(dburi)        
    else:
        raise ValueError('Unknown database backend: "%s"' % backend)
