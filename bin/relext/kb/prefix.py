from rdflib import Namespace
from rdflib.namespace import RDF, RDFS, XSD, DC

DCTERMS = Namespace("http://purl.org/dc/terms/")
NEE = Namespace("http://www.ics.forth.gr/isl/oae/core#")
SCHEMA = Namespace("http://schema.org/")
SIOC = Namespace("http://rdfs.org/sioc/ns#")
SIOC_T = Namespace("http://rdfs.org/sioc/types#")
ONYX = Namespace("http://www.gsi.dit.upm.es/ontologies/onyx/ns#")
WNA = Namespace("http://www.gsi.dit.upm.es/ontologies/wnaffect/ns#")
LEMON = Namespace("http://www.monnet-project.eu/lemon#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBR = Namespace("http://dbpedia.org/resource/")

all_prefixes = [("rdf", RDF),
                ("rdfs", RDFS),
                ("xsd", XSD),
                ("dc", DC),
                ("dcterms", DCTERMS),
                ("lemon", LEMON),
                ("nee", NEE),
                ("dbo", DBO),
                ("dbr", DBR),
                ("schema", SCHEMA),
                ("wna", WNA),
                ("sioc_t", SIOC_T),
                ("onyx", ONYX),
                ("sioc", SIOC)]
