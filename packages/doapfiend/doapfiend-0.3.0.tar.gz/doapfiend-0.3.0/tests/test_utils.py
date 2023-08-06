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

#Move to n3.py output plugin
#def test_get_n3():
#    xml_text = '''<?xml version="1.0"?>
#<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
#         xmlns:dc="http://purl.org/dc/elements/1.1/"
#         xmlns:ex="http://example.org/stuff/1.0/">
#  <rdf:Description rdf:about="http://www.w3.org/TR/rdf-syntax-grammar"
#		   dc:title="RDF/XML Syntax Specification (Revised)">
#    <ex:editor>
#      <rdf:Description ex:fullName="Dave Beckett">
#	<ex:homePage rdf:resource="http://purl.org/net/dajobe/" />
#      </rdf:Description>
#    </ex:editor>
#  </rdf:Description>
#</rdf:RDF>'''
#    #Okay, this doesn't really prove much except that the serializer
#    #returned text without raising an exception
#    assert isinstance(get_n3(xml_text), str)

def test_print_misc_field():
    #label, text
    pass
