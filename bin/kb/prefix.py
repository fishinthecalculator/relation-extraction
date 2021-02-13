from rdflib import Namespace
from rdflib.namespace import RDF, RDFS, XSD, DC

NEE = Namespace("http://www.ics.forth.gr/isl/oae/core#")
SCHEMA = Namespace("http://schema.org/")
SIOC = Namespace("http://rdfs.org/sioc/ns#")
SIOC_T = Namespace("http://rdfs.org/sioc/types#")
ONYX = Namespace("http://www.gsi.dit.upm.es/ontologies/onyx/ns#")
WNA = Namespace("http://www.gsi.dit.upm.es/ontologies/wnaffect/ns#")
LEMON = Namespace("http://www.monnet-project.eu/lemon#")
DBO = Namespace("http://dbpedia.org/ontology/")

all_prefixes = [("rdf", RDF),
                ("rdfs", RDFS),
                ("xsd", XSD),
                ("dc", DC),
                ("lemon", LEMON),
                ("nee", NEE),
                ("dbo", DBO),
                ("schema", SCHEMA),
                ("wna", WNA),
                ("sioc_t", SIOC_T),
                ("onyx", ONYX),
                ("sioc", SIOC)]
