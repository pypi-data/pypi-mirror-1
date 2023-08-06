
#pylint: disable-msg=C0103
"""
doapfiend
=========

U{http://trac.doapspace.org/doapfiend}

Description
-----------
doapfiend is a command-line client and library for querying, creating and
displaying DOAP (Description of a Project) RDF profiles.

doapfiend uses RDFAlchemy and rdflib to parse and serialize DOAP.

Plugins
-------
Plugins can be written for editing DOAP, scraping websites and creating DOAP,
searching for DOAP in SPARQL endpoints, displaying DOAP in various formats such
as HTML etc.


"""


#Hack to get around warning in RDFAlchemy, bug filed upstream
import logging
log = logging.getLogger()
log.setLevel(logging.ERROR)

__docformat__ = 'epytext'
__version__ = '0.3.2'
__author__ = 'Rob Cakebread <rob@doapspace.org>'
__copyright__ = '(C) 2007-2008 Rob Cakebread'
__license__ = 'BSD-2'

