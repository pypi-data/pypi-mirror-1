#!/usr/bin/env python

from doapfiend.doaplib import query_by_homepage, display_doap, fetch_doap


#Get URL for first DOAP if multiple found
url = query_by_homepage('http://news.tiker.net/software/tagpy')[0][1]

#Print RDF/XML
print fetch_doap(url)

#Pretty print plain text
display_doap(fetch_doap(url))
