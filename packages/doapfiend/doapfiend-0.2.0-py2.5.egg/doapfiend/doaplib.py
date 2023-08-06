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

from doapfiend.utils import fetch_file
from doapfiend.model import Project
from doapfiend.plugins import load_plugins

XMLRPC_SERVER = xmlrpclib.ServerProxy('http://doapspace.org/xmlrpc/')


def load_graph(doap, format="xml"):
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
    rdfSubject.db.parse(StringIO(doap), format)
    return Project.ClassInstances().next()


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
