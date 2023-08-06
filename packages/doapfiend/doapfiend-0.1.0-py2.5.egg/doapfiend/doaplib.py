#!/usr/bin/env python
#pylint: disable-msg=C0103

"""

Library for parsing, displaying, querying and serializing DOAP

"""

import sys
import xmlrpclib
from cStringIO import StringIO

from rdfalchemy import rdfSubject
from rdflib import ConjunctiveGraph

from doapfiend.utils import fetch_file, get_n3, DoapPrinter
from doapfiend.model import Project

XMLRPC_SERVER = xmlrpclib.ServerProxy('http://doapspace.org/xmlrpc/')
PKG_INDEX_URI = 'http://doapspace.org/doap'


def load(doap, format="xml"):
    '''
    Load a DOAP profile into a graph

    Supports any serialization format rdflib can parse (xml, n3, etc.)

    @param doap: DOAP
    @type doap: string

    @param format: Serialization format we're parsing
    @type format: string

    @rtype: Project
    @returns: a Project{rdfSubject}

    '''
    rdfSubject.db = ConjunctiveGraph()
    rdfSubject.db.parse(StringIO(doap), format)
    return Project.ClassInstances().next()


def get_by_pkg_index(index, project_name, proxy=None):
    '''
    Get DOAP for a package index project name

    Current indexes:

       - 'sf' SourceForge
       - 'fm' Freshmeat
       - 'py' Python Package Index

    Raises doaplib.utils.NotFound exception on HTTP 404 error

    @param index: Package index two letter abbreviation
    @type index: string

    @param project_name: project name
    @type project_name: string

    @param proxy: Optional HTTP proxy URL
    @type proxy: string

    @rtype: string
    @return: text of file retrieved

    '''
    url = '%s/%s/%s' % (PKG_INDEX_URI, index, project_name)
    return fetch_file(url, proxy)


def query_by_homepage(url):
    '''
    Get list of URL's for DOAP given a project's homepage.
    The list can contain zero or multiple URLs.

    The return format is:
    [(source, URL), (source, URL)...]

    'source' is the two letter package index abbreviation or 'ex' for external.
    'external' meaning the DOAP was spidered on the web.
    Possible package indexes:

    Current indexes:

       - 'sf' SourceForge
       - 'fm' Freshmeat
       - 'py' Python Package Index

    @param url: URL of homepage of a project
    @type url: string

    @rtype: list
    @return: A list of tuples containing URLs for DOAP found by homepage

    '''
    #Should check for env variable for alternate xmplrpc server for testing?
    return XMLRPC_SERVER.query_by_homepage(url)


def display_doap(doap_xml, serialize='text', brief=False):
    '''
    Print DOAP as text, xml, or n3

    @param doap_xml: DOAP profile in RDF/XML
    @type doap_xml: string

    @param serialize: Serialization syntax
    @type serialize: string

    @param brief: Only show brief info when serializing as plain text
    @type brief: boolean

    @return: None on success, 2 on invalid serialization request

    '''
    if serialize == 'text':
        printer = DoapPrinter(load(doap_xml), brief)
        printer.print_doap()
    elif serialize == 'xml':
        print doap_xml
    elif serialize == 'n3':
        print get_n3(doap_xml)
    else:
        sys.stderr.write('Unknown serialization requested: %s' % serialize)
        return 2


def fetch_doap(url, proxy=None):
    '''
    Fetch DOAP by its URL or filename

    @param url: URL of DOAP profile in RDF/XML serialization
    @type url: string

    @rtype: text
    @return: DOAP
    '''
    return fetch_file(url, proxy)
