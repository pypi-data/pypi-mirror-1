#!/usr/bin/env python

# pylint: disable-msg=W0221,R0201

"""

url.py
======

This plugin loads DOAP by its URL or path to a filename.


"""

__docformat__ = 'epytext'


from doapfiend.plugins.base import Plugin
from doapfiend.utils import NotFoundError
from doapfiend.doaplib import fetch_doap


class UrlPlugin(Plugin):

    """Class for formatting DOAP output"""

    #This will be the opt_parser option (--url) in the 'search' group
    name = 'url'
    enabled = False
    enable_opt = 'url'

    def __init__(self):
        '''Setup RDF/XML OutputPlugin class'''
        super(UrlPlugin, self).__init__()
        self.options = None

    def add_options(self, parser, output, search):
        """Add plugin's options to doapfiend's opt parser"""
        search.add_option('-u', '--%s' % self.name,
                action='store', 
                dest=self.enable_opt,
                help='Get DOAP by its URL or by filename.',
                metavar='URL')
        return parser, output, search

    def search(self):
        '''
        Get DOAP by its URL or file path
        This can be any RDF as long as it has the DOAP namespace.

        @rtype: unicode
        @return: DOAP
        '''
        try:
            return fetch_doap(self.options.url, self.options.proxy)
        except NotFoundError:
            print "Not found: %s" % self.options.url

