#!/usr/bin/env python

from doapfiend.doaplib import get_by_pkg_index, print_doap


doap_xml = get_by_pkg_index(index='sf', project_name='nut')

#Print RDF/XML
print doap_xml

#Pretty print plain text
print_doap(doap_xml)

