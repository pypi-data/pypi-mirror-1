
from xml.parsers.expat import ExpatError

from nose.tools import assert_raises

from doapfiend.plugins.xml import OutputPlugin


XML_TEXT = '''<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:ex="http://example.org/stuff/1.0/">
  <rdf:Description rdf:about="http://www.w3.org/TR/rdf-syntax-grammar"
		   dc:title="RDF/XML Syntax Specification (Revised)">
    <ex:editor>
      <rdf:Description ex:fullName="Dave Beckett">
	<ex:homePage rdf:resource="http://purl.org/net/dajobe/" />
      </rdf:Description>
    </ex:editor>
  </rdf:Description>
</rdf:RDF>'''

BOGUS_XML = 'This is no XML'

def my_output_plugin(data):
    plugin = OutputPlugin()
    xml = plugin.serialize(data, False)

def test_output_plugin():
    plugin = OutputPlugin()
    assert isinstance(plugin.serialize(XML_TEXT), str)
    assert isinstance(plugin.serialize(XML_TEXT, True), unicode)
    assert isinstance(plugin.serialize(XML_TEXT, False), str)

def test_output_plugin_bad_data():
    assert_raises(ExpatError, my_output_plugin, BOGUS_XML)

