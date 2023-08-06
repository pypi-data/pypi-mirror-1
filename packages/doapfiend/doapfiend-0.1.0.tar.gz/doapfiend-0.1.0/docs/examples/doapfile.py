#!/usr/bin/env python

from doapfiend.doaplib import fetch_doap, display_doap

DOAP_FILE = './doapfiend.rdf'
DOAP_URL = 'http://librdf.org/raptor/raptor.rdf'

### Fetching from a local file
doap_xml = fetch_doap(DOAP_FILE)

#Print RDF/XML
print doap_xml

#Pretty print plain text
display_doap(doap_xml)

doap_xml = fetch_doap(DOAP_FILE)


### Fetching from a URL

doap_xml = fetch_doap(DOAP_URL)

#Print RDF/XML
print doap_xml

#Pretty print plain text
display_doap(doap_xml)

doap_xml = fetch_doap(DOAP_FILE)

