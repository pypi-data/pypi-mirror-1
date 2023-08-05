__version__ = "0.1.6"
__date__ = "2007/10/18"

import logging, sys
 
_logger = logging.getLogger("stellaris")
_logger.setLevel(logging.INFO) # DEBUG
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter('%(asctime)s (%(levelname)s) %(name)s:%(module)s:%(message)s'))
_logger.addHandler(_hdlr)

# define namespaces
try:
    from rdflib import Namespace
    STELLARIS = Namespace("http://www.gac-grid.org/schema/stellaris#")
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
except:
    pass
