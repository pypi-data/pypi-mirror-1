#!/usr/bin/env python

from doapfiend.doaplib import query_by_homepage, print_doap, fetch_doap


#Get URL for first DOAP if multiple found
url = query_by_homepage('http://trac.doapspace.org/doapfiend')[0][1]

#Print RDF/XML
print fetch_doap(url)

#Pretty print plain text
print_doap(fetch_doap(url))
