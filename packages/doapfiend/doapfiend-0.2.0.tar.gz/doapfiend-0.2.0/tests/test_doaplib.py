
from nose.tools import assert_raises
from rdflib import Namespace

from doapfiend.doaplib import load_graph
from doapfiend.model import Project

DOAP = Namespace("http://usefulinc.com/ns/doap#")
SAMPLE_DOAP = open('tests/data/doapfiend.rdf', 'r').read()


def get_rdf():
    '''Return some sample DOAP RDF/XML'''
    return load_graph(SAMPLE_DOAP)

def test_load_graph():
    doap = open('tests/data/doapfiend.rdf', 'r').read()
    assert isinstance(load_graph(doap), Project)

def test_attributes():
    proj = get_rdf()
    assert proj.name == 'doapfiend'
    assert isinstance(proj.name, unicode)
    assert isinstance(proj.shortname, unicode)
    assert proj.shortname == 'doapfiend'
    assert isinstance(proj.shortdesc[0], unicode)
    assert isinstance(proj.description[0], unicode)
    assert str(proj.homepage.resUri) == 'http://trac.doapspace.org/doapfiend'
    proj.name = 'foo'
    assert proj.name == 'foo'


def type_single(attribute):
    proj = get_rdf()
    proj[attribute] = ['a list, not a string, oops']

def type_multiple(attribute):
    proj = get_rdf()
    setattr(proj, attribute, 'a string not a list')

def test_single_types():
    assert_raises(AttributeError, type_single, 'homepage')
    assert_raises(AttributeError, type_single, 'name')
    assert_raises(AttributeError, type_single, 'shortname')

def test_multiple_types():
    assert_raises(AttributeError, type_multiple, 'shortdesc')
    assert_raises(AttributeError, type_multiple, 'description')
    assert_raises(AttributeError, type_multiple, 'old_homepage')

def test_get_by():
    proj = get_rdf()
    p = Project.get_by(name = 'doapfiend')
    assert p.name == 'doapfiend'
    del p.name
    assert p.name != 'doapfiend'
    

