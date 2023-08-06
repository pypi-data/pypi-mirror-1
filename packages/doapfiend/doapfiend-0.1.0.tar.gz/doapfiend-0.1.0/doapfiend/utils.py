
"""

utils.py
========

Misc utilities for doapfiend
----------------------------

General purpose helper functions and classes for doapfiend
You'll probably want to use doaplib for most cases.

License: BSD-2

"""

#pylint: disable-msg=C0103

import urllib
import logging
import textwrap
import urlparse
from cStringIO import StringIO
from httplib import HTTPConnection
from urllib2 import build_opener, HTTPError, ProxyHandler

from rdflib import ConjunctiveGraph, Namespace
from rdfalchemy import rdfSubject


FOAF = Namespace("http://xmlns.com/foaf/0.1/")

__docformat__ = 'epytext'

LOG = logging.getLogger('doapfiend')

color = {'normal': "\033[0m",
          'bold': "\033[1m",
          'underline': "\033[4m",
          'blink': "\033[5m",
          'reverse': "\033[7m",
          'black': "\033[30m",
          'red': "\033[31m",
          'green': "\033[32m",
          'yellow': "\033[33m",
          'blue': "\033[34m",
          'magenta': "\033[35m",
          'cyan': "\033[36m",
          'white': "\033[37m"}


class NotFoundError(Exception):

    '''DOAP not found'''

    #pylint: disable-msg=W0231
    def __init__(self, err_msg):
        '''Initialize attributes'''
        self.err_msg = err_msg

    def __str__(self):
        return repr(self.err_msg)


def http_filesize(url):
    """
    Get the size of file without downloading it.
    bla bla bla
    blaba

    @param url: URL of file
    @type  url: string

    @rtype: string
    @return: Size of file

    Usage:

    >>> http_filesize('http://trac.doapspace.org/test_file.txt')
    '160'
    """

    host, path = urlparse.urlsplit(url)[1:3]
    if ':' in host:
        # port specified, try to use it
        host, port = host.split(':', 1)
        try:
            port = int(port)
        except ValueError:
            LOG.error('invalid port number %r' % port)
            return False
    else:
        # no port specified, use default port
        port = None
    connection = HTTPConnection(host, port=port)
    connection.request("HEAD", path)
    resp = connection.getresponse()
    return resp.getheader('content-length')


def http_exists(url):
    """
    A quick way to check if a file exists on the web.

    @param url: URL of the document
    @type  url: string
    @rtype: boolean
    @return:  True or False

    Usage:

    >>> http_exists('http://www.python.org/')
    True
    >>> http_exists('http://www.python.org/PenguinOnTheTelly')
    False
    """

    host, path = urlparse.urlsplit(url)[1:3]
    if ':' in host:
        #port specified, try to use it
        host, port = host.split(':', 1)
        try:
            port = int(port)
        except ValueError:
            LOG.error('invalid port number %r' % port)
            return False
    else:
        #no port specified, use default port
        port = None
    connection = HTTPConnection(host, port=port)
    connection.request("HEAD", path)
    resp = connection.getresponse()
    if resp.status == 200:       # normal 'found' status
        found = True
    elif resp.status == 302:     # recurse on temporary redirect
        found = http_exists(urlparse.urljoin(url,
                           resp.getheader('location', '')))
    else:                        # everything else -> not found
        LOG.info("Status %d %s : %s" % (resp.status, resp.reason, url))
        found = False
    return found


def is_content_type(url_or_file, content_type):
    """
    Tells whether the URL or pseudofile from urllib.urlopen is of
    the required content type.

    @param url_or_file: URL or file path
    @type url_or_file: string
    @param content_type: Content type we're looking for
    @type content_type: string

    @rtype: boolean
    @returns: True if it can return the Content type we want

    Usage:

    >>> is_content_type('http://doapspace.org/doap/sf/nlyrics.rdf', \
            'application/rdf+xml')
    True
    >>> is_content_type('http://doapspace.org/', 'application/rdf+xml')
    False
    """
    try:
        if isinstance(url_or_file, str):
            thefile = urllib.urlopen(url_or_file)
        else:
            thefile = url_or_file
        result = thefile.info().gettype() == content_type.lower()
        if thefile is not url_or_file:
            thefile.close()
    except IOError:
        result = False
    return result


def pretty_name(field):
    """
    Convert DOAP element name to pretty printable label

    @param field: Text to be formatted
    @type field: C{string}

    @return: formatted string
    @rtype: string
    """
    if field == 'programming_language':
        field = 'Prog. Lang.'
    if field == 'created':
        field = 'DOAP Created'
    field = field.capitalize()
    field = field.replace('_', ' ')
    field = field.replace('-', ' ')
    return field


def get_n3(xml_text):
    '''
    Return N3 (Notation 3) text

    @param xml_text: XML/RDF
    @type xml_text: string
    @return: Notation 3
    @rtype: string
    '''
    store = ConjunctiveGraph()
    graph = store.parse(StringIO(xml_text), publicID=None, format="xml")
    return graph.serialize(format="n3")


def print_misc_field(label, text):
    '''
    Print colorized and justified single label value pair

    @param label: A label
    @type label: string
    @param text: Text to print
    @type text: string

    @rtype: None
    @return: Nothing
    '''
    label = color['bold'] + label + color['normal']
    print '%s %s' % (label, text)


def fetch_file(url, proxy=None):
    '''
    Download file by URL

    @param url: URL of a file
    @type url: string

    @param proxy: URL of HTTP Proxy
    @type proxy: string

    @return: File
    @rtype: string

    '''
    if not url.startswith('http://') and not url.startswith('ftp://'):
        return open(url, 'r').read()
    LOG.debug('Fetching ' + url)
    if proxy:
        opener = build_opener(ProxyHandler({'http': proxy}))
    else:
        opener = build_opener()
    opener.addheaders = [('Accept', 'application/rdf+xml'),
            ('User-agent',
             'Mozilla/5.0 (compatible; doapfiend ' +
             'http://trac.doapspace.org/doapfiend)')]
    try:
        result = opener.open(url)
    except HTTPError, err_msg:
        if err_msg.code == 404:
            raise NotFoundError('Not found: %s' % url)
        else:
            LOG.error(err_msg)
    return result.read()

class DoapPrinter(object):

    '''Prints DOAP in human readable text'''

    def __init__(self, doap, brief=False):
        '''Initialize attributes'''
        self.brief = brief
        self.doap = doap

    def print_doap(self):
        '''
        Print DOAP in human readable text, optionally colorized

        @rtype: None
        @return: Just prints DOAP
        '''

        self.print_misc()
        if self.brief:
            return
        self.print_people()
        self.print_repos()
        self.print_releases()

    def print_misc(self):
        '''Prints basic DOAP metadata'''
        #Tuples with boolean to indicate single or multiple values
        #and line wrap or not
        #(name, multiple, wrap)
        fields = (('name', False, True), ('shortname', False, True),
                ('homepage', False, False), ('shortdesc', True, True),
                ('description', True, True),
                ('old_homepage', True, False), ('created', False, True),
                ('download_mirror', False, False))

        fields_verbose = (('license', True, True),
                ('programming_language', True, True),
                ('bug_database', False, False),
                ('screenshots', False, False), ('oper_sys', True, True),
                ('wiki', True, False), ('download_page', False, False),
                ('mailing_list', True, False))

        for fld in fields:
            self.print_field(fld)
        if not self.brief:
            for fld in fields_verbose:
                self.print_field(fld)

    def print_repos(self):
        '''Prints DOAP repository metadata'''
        if hasattr(self.doap.cvs_repository, 'module') and \
                self.doap.cvs_repository.module is not None:
            print_misc_field('CVS Module:', self.doap.cvs_repository.module)
            print_misc_field('CVS Anon:', self.doap.cvs_repository.anon_root)
            print_misc_field('CVS Browse:',
                    self.doap.cvs_repository.cvs_browse.resUri)
        if hasattr(self.doap.svn_repository, 'location') and \
                self.doap.svn_repository.location is not None:
            print_misc_field('SVN Location:',
                    self.doap.svn_repository.location.resUri)
            print_misc_field('SVN Browse:',
                    self.doap.svn_repository.svn_browse.resUri)

    def print_releases(self):
        '''Print DOAP package release metadata'''
        if hasattr(self.doap, 'releases'):
            for release in self.doap.releases:
                print color['bold'] + color['cyan'] + release.name + \
                        color['normal']
                print color['cyan'] + '  ' + release.revision + ' ' + \
                        color['normal'] + release.created
                for frel in release.file_releases:
                    print '   %s' % frel.resUri

    def print_people(self):
        '''Print maintainers, documenters, helpers etc.'''
        print_misc_field("Maintainers:",
                ",".join([m[FOAF.name] for m in self.doap.maintainer]))

    def print_field(self, field):
        '''
        Print a DOAP element

        @param field: A misc DOAP element
        @type field: string

        @rtype: None
        @return: Nothing
        '''
        name, multi, wrap = field
        if not hasattr(self.doap, name):
            return
        attr = getattr(self.doap, name)
        if attr == [] or attr is None:
            return
        label = '%s' % color['bold'] + pretty_name(name) + \
                 color['normal'] + ':'
        label = label.ljust(21)
        if multi:
            #Can have multiple values per attribute
            for thing in getattr(self.doap, name):
                if isinstance(thing, rdfSubject):
                    text = thing.resUri
                else:
                    #unicode object
                    text = thing
        else:
            text = getattr(self.doap, name)
            if isinstance(text, rdfSubject):
                text = text.resUri
        if wrap:
            print textwrap.fill('%s %s' % (label, text),
                    initial_indent='',
                    subsequent_indent = '              ')

        else:
            print '%s %s' % (label, text)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

