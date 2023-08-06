
# pylint: disable-msg=C0103
'''

cli.py
======

Command-line tool for querying, serializing and displaying DOAP

Author: Rob Cakebread <rob@doapspace.org>

License : BSD-2

'''

__docformat__ = 'epytext'
__revision__ = '$Revision:  $'[11:-1].strip()


import sys
import logging
import optparse

from doapfiend.plugins import load_plugins
from doapfiend.utils import COLOR
from doapfiend.__init__ import __version__ as VERSION
from doapfiend.doaplib import print_doap, follow_homepages, show_links


class DoapFiend(object):

    '''`DoapFiend` class'''

    def __init__(self):
        '''Initialize attributes, set logger'''
        self.doap = None
        self.options = None
        self.log = logging.getLogger('doapfiend')
        self.log.addHandler(logging.StreamHandler())
        #Cache list of all plugins
        self.plugins = list(load_plugins(others=True))
        self.serializer = None

    def get_plugin(self, method):
        """
        Return plugin object if CLI option is activated and method exists

        @param method: name of plugin's method we're calling
        @type method: string

        @returns: list of plugins with `method`

        """
        all_plugins = []
        for plugin_obj in self.plugins:
            plugin = plugin_obj()
            plugin.configure(self.options, None)
            if plugin.enabled:
                if not hasattr(plugin, method):
                    plugin = None
                else:
                    all_plugins.append(plugin)
        return all_plugins

    def set_log_level(self):
        '''Set log level according to command-line options'''
        if self.options.verbose:
            self.log.setLevel(logging.INFO)
        elif self.options.quiet:
            self.log.setLevel(logging.ERROR)
        elif self.options.debug:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.WARN)

    def print_doap(self, doap_xml):
        '''
        Print doap as n3, rdf/xml, plain text or using serialization plugin

        @param doap_xml: DOAP in RDF/XML serialization
        @type doap_xml: text

        @rtype: None
        @return: Just displays DOAP

        '''
        if self.options.write:
            filename = self.options.write
        else:
            filename = None
        print_doap(doap_xml, serializer=self.serializer, filename=filename,
                color=not self.options.no_color)

    def get_search_plugin(self):
        '''
        Return active search plugin callable
        
        @rtype: callable
        @returns: A callable object that fetches for DOAP
        '''
        plugins = self.get_plugin('search')
        if len(plugins) == 1:
            return plugins[0].search

    def run(self):
        '''
        Run doapfiend command

        Find the active plugin that has a 'search' method and run it,
        then output the DOAP with print_doap, using the active plugin
        with a 'serializer' method.


        @rtype: int 
        @returns: 0 success or 1 failure
        
        '''
        opt_parser = self.setup_opt_parser()
        (self.options, remaining_args) = opt_parser.parse_args()
        self.set_serializer()
        if not self.serializer and remaining_args:
            opt_parser.print_help()
            return 1
        self.set_log_level()

        if self.options.doapfiend_version:
            return doapfiend_version()

        if self.options.no_color:
            for this in COLOR:
                COLOR[this] = '\x1b[0m'
        search_func = self.get_search_plugin()
        if search_func:
            doap_xml = search_func()
            if doap_xml:
                if self.options.follow:
                    #Search for additional DOAP by looking up all doap:homepage
                    #found and then print all found. This may be used if the
                    #DOAP you've found isn't rich enough or with FOAF, where a
                    #person lists multiple projects they are affiliated with
                    #and you want to find DOAP based on the Projec homepages
                    #found in FOAF.
                    self.print_doap(doap_xml)
                    return follow_homepages(doap_xml)
                elif self.options.show_links:
                    return show_links(doap_xml)
                else:
                    return self.print_doap(doap_xml)
        else:
            opt_parser.print_help()
        return 1

    def set_serializer(self):
        '''
        Find all plugins that are enabled on the command-line and have a
        `serialize` method. If none are enabled, default to plain text
        '''
        plugins = self.get_plugin('serialize')
        if len(plugins) == 0:
            self.serializer = None
        else:
            #Choose first serializer in case they try more than one
            self.serializer = plugins[0].serialize

    def setup_opt_parser(self):
        '''
        Setup the optparser

        @rtype: opt_parser.OptionParser
        @return: Option parser

        '''
        usage = 'usage: %prog [options]'
        opt_parser = optparse.OptionParser(usage=usage)
        group_search = optparse.OptionGroup(opt_parser,
                'Search options',
                'Options for searching for DOAP')

        opt_parser.add_option('--version', action='store_true',
                dest='doapfiend_version', default=False,
                help='Show doapfiend version and exit.')

        opt_parser.add_option('-P', '--http-proxy', action='store',
                dest='proxy', default=False,
                help='Specify http proxy URL if you use one.')

        group_output = optparse.OptionGroup(opt_parser,
                'Output options',
                'Choose these options to change default output behavior')

        group_output.add_option('--debug', action='store_true',
                dest= 'debug', default=False,
                help='Show debugging information')

        group_output.add_option('-f', '--follow-links', action='store_true',
                dest='follow', default=False,
                help='Search for and show additional DOAP.',
                              metavar='FILENAME')

        group_output.add_option('-s', '--show-links', action='store_true',
                dest='show_links', default=False,
                help='Search for and show links to additional DOAP.',
                metavar='FILENAME')

        group_output.add_option('-w', '--write', action='store',
                dest='write', default=False,
                help='Write DOAP to a file instead of displaying it.',
                metavar='FILENAME')

        group_output.add_option('-C', '--no-color', action='store_true',
                dest='no_color', default=False,
                help="Don't use color in output")

        group_output.add_option('-q', '--quiet', action='store_true',
                dest='quiet', default=False, help="Show less output")

        group_output.add_option('-v', '--verbose', action='store_true',
                dest='verbose', default=False, help="Show more output")

        # add opts from plugins
        for plugcls in self.plugins:
            plug = plugcls()
            plug.add_options(opt_parser, group_output, group_search)
        opt_parser.add_option_group(group_search)
        opt_parser.add_option_group(group_output)
        return opt_parser


def doapfiend_version():
    '''Print doapfiend version'''
    print VERSION


def main():
    '''Let's do it.'''
    my_doapfiend = DoapFiend()
    return my_doapfiend.run()


if __name__ == '__main__':
    sys.exit(main())

