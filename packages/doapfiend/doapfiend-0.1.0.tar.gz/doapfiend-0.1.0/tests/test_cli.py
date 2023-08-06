
from doapfiend.cli import setup_opt_parser, main

from optparse import OptionParser

    #def test_query_by_homepage(self, url):
    #def test_set_log_level(self):
    #def test_doapfiend_version(self):
    #def test_fetch_file(self, url):
    #def test_get_by_sourceforge(self, project_name):
    #def test_get_by_pypi(self, project_name):
    #def test_display_doap(self, url):
    #def test__display_doap(self, doap_xml):
    #def test_print_doap(self, text, brief=False):
    #def test_print_misc(self):
    #def test_print_repos(self):
    #def test_print_releases(self):
    #def test_print_people(self):
    #def test_print_field(self, field):
    #def test_run(self):

def test_setup_opt_parser():
    assert isinstance(setup_opt_parser(), OptionParser)

#def test_main():
#    #Run main with no options
#    assert main() == 1
