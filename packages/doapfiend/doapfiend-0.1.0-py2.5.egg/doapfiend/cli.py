
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

from doapfiend.utils import color, NotFoundError
from doapfiend.__init__ import __version__ as VERSION
from doapfiend.doaplib import (get_by_pkg_index, query_by_homepage,
        display_doap, fetch_doap)


class DoapFiend(object):

    '''`DoapFiend` class'''

    def __init__(self):
        '''Initialize attributes, set logger'''
        self.doap = None
        self.options = None
        self.log = logging.getLogger('doapfiend')
        self.log.addHandler(logging.StreamHandler())

    def by_homepage(self, url):
        '''
        Print DOAP given a project's homepage

        @param url: URL of homepage of a project
        @type url: string

        @rtype: None
        @return: Print a DOAP profile

        '''
        resp = query_by_homepage(url)
        self.log.debug(resp)
        if len(resp) == 0:
            self.log.error("Not found: %s" % url)
            return 1
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
        doap_text = fetch_doap(url, self.options.proxy)
        self.log.debug(doap_text)
        if doap_text:
            self.print_doap(doap_text)

    def set_log_level(self):
        '''Set log level according to command-line options'''
        if self.options.debug:
            self.log.setLevel(logging.DEBUG)

    def doapfiend_version(self):
        '''Print doapfiend version'''
        #pylint: disable-msg=R0201
        print VERSION

    def by_pkg_index(self, index, project_name):
        '''
        Display DOAP for a package index project name
        index examples: sf - SourceForge, fm - Freshmeat

        @param index: Package index two letter abbreviation
        @type index: string

        @param project_name: project name
        @type project_name: string

        @rtype: None
        @return: Nothing, just prints DOAP

        '''
        try:
            doap = get_by_pkg_index(index, project_name, self.options.proxy)
        except NotFoundError:
            self.log.error("Not found: %s" % project_name)
            return 1
        self.print_doap(doap)

    def show_doap(self, url):
        '''
        Display DOAP given its URL

        @param url: URL of DOAP profile in RDF/XML serialization
        @type url: string

        @rtype: None
        @return: Just displays DOAP
        '''
        try:
            doap_xml = fetch_doap(url, self.options.proxy)
        except NotFoundError:
            self.log.error("Not found: %s" % url)
            return 1
        self.print_doap(doap_xml)

    def print_doap(self, doap_xml):
        '''
        Print doap in one of two serializations or plain text

        @param doap_xml: DOAP in RDF/XML serialization
        @type doap_xml: text

        @rtype: None
        @return: Just displays DOAP

        '''
        if self.options.xml:
            serialize = 'xml'
        elif self.options.n3:
            serialize = 'n3'
        else:
            serialize = 'text'
        display_doap(doap_xml, serialize, self.options.brief)

    def run(self):
        '''Run doapfiend command'''
        # Too many return statements:
        # pylint: disable-msg=R0911

        opt_parser = setup_opt_parser()
        (self.options, remaining_args) = opt_parser.parse_args()
        if remaining_args:
            opt_parser.print_help()
        self.set_log_level()

        if self.options.no_color:
            #Set it to normal code instead of '' for justification
            for this in color:
                color[this] = '\x1b[0m'

        if self.options.by_homepage:
            return self.by_homepage(url=self.options.by_homepage)
        elif self.options.display_doap:
            return self.show_doap(url=self.options.display_doap)
        elif self.options.doapfiend_version:
            return self.doapfiend_version()
        elif self.options.sourceforge:
            return self.by_pkg_index(index="sf",
                    project_name=self.options.sourceforge)
        elif self.options.freshmeat:
            return self.by_pkg_index(index="fm",
                    project_name=self.options.freshmeat)
        elif self.options.pypi:
            return self.by_pkg_index(index="py",
                    project_name=self.options.pypi)
        else:
            opt_parser.print_help()
            return 1


def setup_opt_parser():
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

    opt_parser.add_option('--version', action='store_true', dest=
                          'doapfiend_version', default=False, help=
                          'Show doapfiend version and exit.')

    opt_parser.add_option('-P', '--http-proxy', action='store', dest=
                          'proxy', default=False, help=
                          'Specify http proxy URL if you use one.')

    group_search.add_option('-d', '--display-doap', action='store', dest=
                          'display_doap', default=False, help=
                          'Display DOAP you know the URL of or filename.',
                          metavar='URL')

    group_search.add_option('-o', '--homepage', action='store', dest=
                          'by_homepage', default=False, help=
                          "Get DOAP by the project's homepage URL.",
                          metavar='HOMEPAGE_URL')

    group_search.add_option('-f', '--freshmeat', action='store', dest=
                          'freshmeat', default=False, help=
                          'Display DOAP by its Freshmeat project name.',
                          metavar='PROJECT_NAME')

    group_search.add_option('-s', '--sourceforge', action='store', dest=
                          'sourceforge', default=False, help=
                          'Display DOAP by its SourceForge project name.',
                          metavar='PROJECT_NAME')

    group_search.add_option('-p', '--pypi', action='store', dest=
                          'pypi', default=False, help=
                          'Display DOAP by its Python Package Index pkg name.',
                          metavar='PROJECT_NAME')

    group_display = optparse.OptionGroup(opt_parser,
            'Display options',
            'Choose these options to change default display behavior')

    group_display.add_option('--debug', action='store_true', dest=
                          'debug', default=False, help=
                          'Show debugging information')

    group_display.add_option('-b', '--brief', action='store_true', dest=
                          'brief', default=False, help=
                          'Show less output.')

    group_display.add_option('-C', '--no-color', action='store_true', dest=
                          'no_color', default=False, help=
                          "Don't use color in output")

    group_display.add_option('-n', '--n3', action='store_true',
                          dest='n3', default=False, help=
                          'Display DOAP in Notation Three syntax')

    group_display.add_option('-x', '--xml', action='store_true', dest=
                          'xml', default=False, help=
                          'Display DOAP as RDF/XML')

    opt_parser.add_option_group(group_search)
    opt_parser.add_option_group(group_display)
    return opt_parser


def main():
    '''Let's do it.'''
    my_doapfiend = DoapFiend()
    return my_doapfiend.run()


if __name__ == '__main__':
    sys.exit(main())

