#!/usr/bin/env python
#pylint: disable-msg=C0103

"""

Library for parsing, displaying, querying and serializing DOAP

"""

import sys
import xmlrpclib
from cStringIO import StringIO
from xml.sax._exceptions import SAXParseException

from rdfalchemy import rdfSubject
from rdflib import ConjunctiveGraph, Namespace

from doapfiend.utils import fetch_file
from doapfiend.model import Project
from doapfiend.plugins import load_plugins

XMLRPC_SERVER = xmlrpclib.ServerProxy('http://doapspace.org/xmlrpc/')
DOAP_NS = Namespace('http://usefulinc.com/ns/doap#')


def follow_homepages(rdf_xml):
    '''
    If there is a 'doap:Project homepage' it will be looked up
    on doapspace.org using get_by_homepage to find any other
    DOAP. This is useful if we're looking at FOAF and a project
    is mentioned by homepage. It can also be used on DOAP files
    to search for additional DOAP files about the same project.

    @param rdf_xml: RDF serialized as XML
    @type : string

    @rtype: int
    @returns: 0 on sucess or 1 if there was no DOAP in the RDF
    '''
    homepages = list(get_homepages(rdf_xml))
    nbr_homepage_urls = len(homepages)
    if nbr_homepage_urls >= 1:
        print_doap_by_homepages(homepages)
    else:
        print 'No DOAP found in that RDF.'
        return 1


def show_links(rdf):
    '''
    If there is a 'doap:Project homepage' it will be looked up
    on doapspace.org using get_by_homepage to find any other
    DOAP. This is useful if we're looking at FOAF and a project
    is mentioned by homepage. It can also be used on DOAP files
    to search for additional DOAP files about the same project.

    @param rdf: RDF serialized as XML
    @type : string

    @rtype: int
    @returns: 0 on sucess or 1 if there was no DOAP in the RDF
    '''
    homepages = list(get_homepages(rdf))
    nbr_homepage_urls = len(homepages)
    if nbr_homepage_urls >= 1:
        for hpage_url in homepages:
            print "Found project homepage:", hpage_url
            #Search for DOAP by project homepage.
            hpages = query_by_homepage(hpage_url)
            for _src, hpage_url in hpages:
                print '  Found DOAP: ', hpage_url
    else:
        print 'No DOAP found in that RDF.'
        return 1


def print_doap_by_homepages(homepages):
    '''
    Given a list of homepage URLs, search for DOAP for each and print

    @param homepages: Project homepage
    @type : list

    @rtype: None
    @returns: None
    '''
    for hpage_url in homepages:
        print "Found project homepage", hpage_url
        #Search for DOAP by project homepage. There may be none, one or multiple
        hpages = query_by_homepage(hpage_url)
        for _src, hpage_url in hpages:
            print 'Found DOAP at ', hpage_url
            doap_xml = fetch_doap(hpage_url)
            print_doap(doap_xml)

def get_homepages(rdf, format='xml'):
    '''
    Find all doap:homepage in RDF

    @param rdf: RDF
    @type rdf: string

    @param format: Serialization format
    @type format: string

    @rtype: generator
    @returns: homepages
    '''
    store = ConjunctiveGraph()
    store.parse(StringIO(rdf), publicID=None, format=format)
    if rdf_has_doap(store):
        for _s, o in store.subject_objects(DOAP_NS["homepage"]):
            yield(str(o))

def rdf_has_doap(store):
    '''
    Returns True if triplestore has the DOAP namespace defined

    @param store: triplestore
    @type store: rdflib ConjunctiveGraph

    @rtype: boolean
    @returns: True if triplestore contains DOAP namespace

    '''
    for namespace in store.namespaces():
        if namespace[1] == DOAP_NS:
            return True

def load_graph(doap, format="xml", next=True):
    '''
    Load a DOAP profile into a RDFAlchemy/rdflib graph

    Supports any serialization format rdflib can parse (xml, n3, etc.)

    @param doap: DOAP
    @type doap: string

    @param format: Serialization format we're parsing
    @type format: string

    @rtype: Project
    @returns: a Project{rdfSubject}

    '''
    rdfSubject.db = ConjunctiveGraph()
    try:
        rdfSubject.db.parse(StringIO(doap), format)
    except SAXParseException:
        sys.stderr.write("Error: Can't parse RDF/XML.\n")
        sys.exit(2)

    if next:
        try: 
            return Project.ClassInstances().next()
        except StopIteration:
            sys.stderr.write('No DOAP found in that RDF.\n')
            sys.exit(2)
    else:
        return Project


def get_by_pkg_index(index, project_name, proxy=None):
    '''
    Get DOAP for a package index project name

    Builtin indexes:

       - 'sf' SourceForge
       - 'fm' Freshmeat
       - 'py' Python Package Index

    Note there can be other package indexes available by 
    third party plugins.

    @param index: Package index two letter abbreviation
    @type index: string

    @param project_name: project name
    @type project_name: string

    @param proxy: Optional HTTP proxy URL
    @type proxy: string

    @rtype: string
    @return: text of file retrieved

    '''
    for plugin_obj in list(load_plugins()):
        plugin = plugin_obj()
        if hasattr(plugin, 'prefix'):
            if plugin.prefix == index:
                plugin.query = project_name
                return plugin.search(proxy)


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
       - 'oh' Packages listed on Ohloh

    @param url: URL of homepage of a project
    @type url: string

    @rtype: list
    @return: A list of tuples containing URLs for DOAP found by homepage

    '''
    #Should check for env variable for alternate xmplrpc server for testing?
    return XMLRPC_SERVER.query_by_homepage(url)


def print_doap(doap_xml, color=None, format='text', serializer=None,
        filename=None):
    '''
    Print DOAP as text, xml, or n3 etc. or to stdout or a file
    A callable serializer object may be passed or a name of a serializer
    plugin.

    @param doap_xml: DOAP profile in RDF/XML
    @type doap_xml: string

    @param format: Serialization syntax formatter name
    @type format: string

    @param serializer: Instance of a serializer
    @type serializer: callable

    @param filename: Optional filename to write to
    @type filename: string

    @return: `serializer` or 1 if invalid serialization request

    '''
    #If we were passed a callable serializer object use it,
    #otherwise lookup serializer by name in list of plugins
    if not serializer:
        serializer = get_serializer(format)
        if not serializer:
            sys.stderr.write('Unknown serialization requested: %s\n' % format)
            return 1

    doap = serializer(doap_xml, color)
    if filename:
        try:
            open(filename, 'w').write(doap.encode('utf-8'))
        except UnicodeDecodeError:
            open(filename, 'w').write(doap)
    else:
        print doap


def get_serializer(format):
    '''
    Return a serializer instance given its name

    @param format: Name of serializer
    @type format: string

    @rtype: function
    @returns: Instance of a serializer
    '''
    #Get all plugins with a `serialize` method
    for plugin_obj in get_plugin('serialize'):
        plugin = plugin_obj()
        if plugin.name == format:
            return plugin.serialize


def get_plugin(method):
    """
    Return plugin object if `method` exists

    @param method: name of plugin's method we're calling
    @type method: string

    @returns: list of plugins with `method`

    """
    all_plugins = []
    for plugin in load_plugins():
        #plugin().configure(None, None)
        if not hasattr(plugin, method):
            plugin = None
        else:
            all_plugins.append(plugin)
    return all_plugins


def fetch_doap(url, proxy=None):
    '''
    Fetch DOAP by its URL or filename

    @param url: URL of DOAP profile in RDF/XML serialization
    @type url: string

    @rtype: text
    @return: DOAP
    '''
    return fetch_file(url, proxy)
