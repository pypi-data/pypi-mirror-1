#!/usr/bin/env python

# pylint: disable-msg=W0221,R0201

"""

sourceforge
===========

Currently this plugin uses http://doapspace.org/ to fetch DOAP for SourceForge


"""

__docformat__ = 'epytext'


from doapfiend.utils import NotFoundError
from doapfiend.plugins.base import Plugin
from doapfiend.plugins.pkg_index import get_by_pkg_index


class SourceForgePlugin(Plugin):

    """Get DOAP from SourceForge package index"""

    #This will be the opt_parser option (--sf) in the output group
    name = "sf"
    enabled = False
    enable_opt = name

    def __init__(self):
        '''Setup RDF/XML OutputPlugin class'''
        super(SourceForgePlugin, self).__init__()
        self.options = None
        self.query = None

    def add_options(self, parser, output, search):
        """Add plugin's options to doapfiend's opt parser"""
        search.add_option('--%s' % self.name,
                action='store', 
                dest=self.enable_opt,
                help='Get DOAP by its SourceForge project name.',
                metavar='PROJECT_NAME')
        return parser, output, search

    def search(self, proxy=None):
        '''
        Get SourceForge DOAP

        @param proxy: Option HTTP proxy URL
        @type proxy: string

        @rtype: unicode
        @returns: Single DOAP

        '''
        if hasattr(self.options, self.name): 
            self.query = getattr(self.options, self.name)
        #Else self.query was set directly, someone not using the CLI
        try:
            return get_by_pkg_index(self.name, self.query, proxy)
        except NotFoundError:
            print "Not found: %s" % self.query

