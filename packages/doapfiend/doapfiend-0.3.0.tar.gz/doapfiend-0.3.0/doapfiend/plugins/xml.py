#!/usr/bin/env python

# pylint: disable-msg=W0221,R0201

"""

Serialize DOAP as XML/RDF
=========================

This plugin outputs DOAP in RDF/XML
It basically does nothing because all DOAP today is in RDF/XML.
In the future this may take N3, Turtle, RDFa etc. and convert it to RDF/XML.

"""

__docformat__ = 'epytext'


from doapfiend.plugins.base import Plugin


class OutputPlugin(Plugin):

    """Class for formatting DOAP output"""

    #This will be the opt_parser option (--xml) in the output group
    name = "xml"
    enabled = False
    enable_opt = None

    def __init__(self):
        '''Setup RDF/XML OutputPlugin class'''
        super(OutputPlugin, self).__init__()
        self.options = None

    def add_options(self, parser, output, search):
        """Add plugin's options to doapfiend's opt parser"""
        output.add_option('-x', '--%s' % self.name,
                action='store_true', 
                dest=self.enable_opt,
                help='Output DOAP as RDF/XML')
        return parser, output, search

    def serialize(self, doap_xml, color=False):
        '''
        Serialize RDF/XML DOAP as N3 syntax

        @param doap_xml: DOAP in RDF/XML serialization
        @type doap_xml: string

        @rtype: unicode
        @returns: DOAP
        '''

        if hasattr(self.options, 'no_color'):
            color = not self.options.no_color
        if color:
            #pygments plugin fools pylint
            # pylint: disable-msg=E0611
            try:
                from pygments import highlight
                from pygments.lexers import XmlLexer
                from pygments.formatters import TerminalFormatter
            except ImportError:
                return doap_xml
            return highlight(doap_xml,
                    XmlLexer(),
                    TerminalFormatter(full=False))
        else:
            return doap_xml

