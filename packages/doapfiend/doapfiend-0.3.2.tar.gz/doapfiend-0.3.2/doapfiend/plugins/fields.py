#!/usr/bin/env python

# pylint: disable-msg=W0221,R0201
"""

Plain text serializer
=====================

This plugin outputs DOAP in human-readable plain text

"""

__docformat__ = 'epytext'

import logging

from rdflib import Namespace
from rdfalchemy import rdfSubject

from doapfiend.plugins.base import Plugin
from doapfiend.utils import COLOR 
from doapfiend.doaplib import load_graph


FOAF = Namespace("http://xmlns.com/foaf/0.1/")

LOG = logging.getLogger('doapfiend')


class OutputPlugin(Plugin):

    """Class for formatting DOAP output"""

    #This will be the opt_parser option (--fields)
    name = "fields"
    enabled = False
    enable_opt = name

    def __init__(self):
        '''Setup Plain Text OutputPlugin class'''
        super(OutputPlugin, self).__init__()
        self.options = None

    def add_options(self, parser, output, search):
        """Add plugin's options to doapfiend's opt parser"""
        output.add_option('--%s' % self.name,
                action='store', 
                dest=self.enable_opt,
                help='Output specific DOAP fields as plain text')
        return parser, output, search

    def serialize(self, doap_xml, color=False):
        '''
        Serialize RDF/XML DOAP as N3 syntax

        @param doap_xml: DOAP in RDF/XML serialization
        @type doap_xml: string
        
        @rtype: unicode
        @return: DOAP in plain text
        '''
        if hasattr(self.options, 'no_color'):
            color = not self.options.no_color
        if not color:
            #This has already been done if we're called from cli.py
            #Fix me: Need to think on this.
            for this in COLOR:
                COLOR[this] = '\x1b[0m'

        if hasattr(self.options, 'quiet'):
            brief = self.options.quiet
        else:
            brief = False

        doap = load_graph(doap_xml)
        fields = self.options.fields.split(',')
        #print fields
        out = ''
        for field in fields:
            if '-' in field:
                field = field.replace('-', '_')
            field = field.strip()
            if '.' in field:
                repo, field = field.split('.')
                text = print_repos(doap, repo, field)
            elif field == 'releases':
                text = get_releases(doap, brief)
            if field in ['maintainer', 'developer', 'documenter', 'helper',
                    'tester', 'translator']:
                text = get_people(doap, field)
            else:
                try: 
                    text = getattr(doap, field)
                except AttributeError:
                    LOG.warn("No such attribute: %s" % field)
                    text = None
                if not text:
                    continue
                if isinstance(text, list):
                    text = print_list(doap, field)
                else:
                    text = print_field(doap, field)
            out += text + '\n'
        return out.rstrip()

def print_list(doap, field):
    '''
    Print list of DOAP attributes

    @param doap: DOAP in RDF/XML
    @type doap: text

    @param field: DOAP attribute to be printed
    @type field: text

    @rtype: text
    @returns: Field to be printed
    '''
    #Can have multiple values per attribute
    text = ""
    for thing in getattr(doap, field):
        if isinstance(thing, rdfSubject):
            text += thing.resUri
        else:
            #unicode object
            thing = thing.strip()
            text += thing 
    return text

def print_field(doap, field):
    '''
    Print single field

    @param doap: DOAP in RDF/XML
    @type doap: text

    @param field: DOAP attribute to be printed
    @type field: text

    @rtype: text
    @returns: Field to be printed
    '''
    text = getattr(doap, field)
    if isinstance(text, rdfSubject):
        return text.resUri.strip()
    else:
        return text.strip()

def print_repos(doap, repo, field):
    '''Prints DOAP repository metadata'''
    if repo == 'cvs':
        if hasattr(doap.cvs_repository, field):
            return getattr(doap.cvs_repository, field)

    if repo == 'svn':
        if field == 'browse':
            field = 'svn_browse'
        if hasattr(doap.svn_repository, field):
            text = getattr(doap.svn_repository, field)
            if text:
                if isinstance(text, rdfSubject):
                    return text.resUri
                else:
                    return text.strip()
    return ''

def get_people(doap, job):
    '''Print people for a particular job '''
    out = ''
    if hasattr(doap, job):
        attribs = getattr(doap, job)
        if len(attribs) > 0:
            peeps = []
            for attr in attribs:
                if attr[FOAF.mbox] is None:
                    person = "%s" % attr[FOAF.name]
                else:
                    mbox = attr[FOAF.mbox].resUri
                    if mbox.startswith('mailto:'):
                        mbox = mbox[7:]
                        person = "%s <%s>" % (attr[FOAF.name], mbox)
                    else:
                        LOG.debug("mbox is invalid: %s" % mbox)
                        person = "%s" % attr[FOAF.name]
                peeps.append(person)
            out += ", ".join([p for p in peeps])
    return out


def get_releases(doap, brief=False):
    '''Print DOAP package release metadata'''
    out = ''
    if hasattr(doap, 'releases') and len(doap.releases) != 0:
        if not brief:
            out += COLOR['bold'] + "Releases:" + COLOR['normal'] + '\n'
        for release in doap.releases:
            if release.name:
                out += COLOR['bold'] + COLOR['cyan'] + release.name + \
                    COLOR['normal'] + '\n'
            if hasattr(release, 'created') and release.created is not None:
                created = release.created
            else:
                created = ''
            out += COLOR['cyan'] + '  ' + release.revision + ' ' + \
                    COLOR['normal'] + created + '\n'
            if not brief:
                if hasattr(release, 'changelog'):
                    if release.changelog:
                        out += COLOR['yellow'] + release.changelog + \
                                COLOR['normal'] + '\n'

            for frel in release.file_releases:
                out += '   %s' % frel.resUri + '\n'
    return out

