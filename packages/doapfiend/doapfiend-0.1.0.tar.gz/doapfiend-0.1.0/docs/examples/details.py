#!/usr/bin/env python

from doapfiend.doaplib import fetch_doap, load

DOAP_FILE = './doapfiend.rdf'

### Fetching from a local file
doap_xml = fetch_doap(DOAP_FILE)

#Create a RDFAlchemy Project instance
doap = load(doap_xml)

print doap.name

#This is a URI
print doap.homepage.resUri

#Note shortdesc is a list because shortdesc may have multiple language encodings
print doap.shortdesc

