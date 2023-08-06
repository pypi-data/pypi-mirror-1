from doapfiend.utils import (http_filesize, http_exists, is_content_type)
                
def test_http_filesize(url='http://trac.doapspace.org/test_file.txt'):
    assert http_filesize(url) == '160'

def test_http_exists():
    assert http_exists('http://www.python.org/PenguinOnTheTelly') == False
    assert http_exists('http://www.python.org/') == True

def test_is_content_type():
    assert is_content_type('http://doapspace.org/doap/sf/nlyrics.rdf',
            'application/rdf+xml') == True
    assert is_content_type('http://doapspace.org/',
            'application/rdf+xml') == False

#Move to text.py output plugin
#def test_pretty_name(field=None):
#    assert pretty_name('foo') == 'Foo'
#    assert pretty_name('foo_bar') == 'Foo bar'
#    assert pretty_name('foo-bar') == 'Foo bar'


def test_print_misc_field():
    #label, text
    pass
