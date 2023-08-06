#!/usr/bin/env python

# pylint: disable-msg=W0221,R0201

"""

homepage
========

Fetches DOAP by searching doapspace.org by a project's homepage.

"""

__docformat__ = 'epytext'

import logging

from doapfiend.plugins.base import Plugin
from doapfiend.doaplib import fetch_doap, query_by_homepage


class OutputPlugin(Plugin):

    """Class for formatting DOAP output"""

    #This will be the opt_parser option (--xml) in the output group
    name = "homepage"
    enabled = False
    enable_opt = name

    def __init__(self):
        '''Setup RDF/XML OutputPlugin class'''
        super(OutputPlugin, self).__init__()
        self.log = logging.getLogger("doapfiend")
        self.options = None

    def add_options(self, parser, output, search):
        """Add plugin's options to doapfiend's opt parser"""
        search.add_option('-o', '--%s' % self.name,
                action='store', 
                dest=self.enable_opt,
                help="Search for DOAP by a project's homepage",
                metavar='HOMEPAGE_URL')
        return parser, output, search

    def search(self):
        '''
        Get DOAP given a project's homepage

        @rtype: unicode
        @return: DOAP
        '''
        resp = query_by_homepage(self.options.homepage)
        self.log.debug(resp)
        if len(resp) == 0:
            self.log.error("Not found: %s" % self.options.homepage)
            return
        elif len(resp) == 1:
            url = resp[0][1]
        else:
            #Multiple, send warning and use first 'external' if any
            self.log.error("Warning: Multiple DOAP found.")
            url = None
            for this in resp:
                self.log.error(this)
                if not url:
                    #Keep first one if there is no external DOAP
                    url = this[1]
                if this[0] == 'ex':
                    url = this[1]
            self.log.error("Using %s" % url)
        return fetch_doap(url, self.options.proxy)
