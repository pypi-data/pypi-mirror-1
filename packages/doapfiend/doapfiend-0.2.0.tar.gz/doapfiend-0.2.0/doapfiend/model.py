
'''

Model of a DOAP profile using RDFAlchemy

'''

from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple
from rdfalchemy.orm import mapper
from rdflib import Namespace

DOAP = Namespace("http://usefulinc.com/ns/doap#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")


class Project(rdfSubject):

    """
    DOAP Project Class
    """

    rdf_type = DOAP.Project

    category = rdfMultiple(DOAP.category)
    created = rdfSingle(DOAP.created)
    shortname = rdfSingle(DOAP.shortname)
    description = rdfMultiple(DOAP.description)
    bug_database = rdfSingle(DOAP['bug-database'])
    developer = rdfMultiple(DOAP.developer, range_type=FOAF.Person)
    documenter = rdfMultiple(DOAP.documenter, range_type=FOAF.Person)
    download_mirror = rdfMultiple(DOAP['downoad-mirror'])
    download_page = rdfSingle(DOAP['download-page'])
    helper = rdfMultiple(DOAP.helper, range_type=FOAF.Person)
    homepage = rdfSingle(DOAP.homepage)
    license = rdfMultiple(DOAP['license'])
    maintainer = rdfMultiple(DOAP.maintainer, range_type=FOAF.Person)
    developer = rdfMultiple(DOAP.developer, range_type=FOAF.Person)
    translator = rdfMultiple(DOAP.translator, range_type=FOAF.Person)
    helper = rdfMultiple(DOAP.helper, range_type=FOAF.Person)
    tester = rdfMultiple(DOAP.tester, range_type=FOAF.Person)
    documenter = rdfMultiple(DOAP.documenter, range_type=FOAF.Person)
    module = rdfSingle(DOAP.module)
    name = rdfSingle(DOAP.name)
    old_homepage = rdfMultiple(DOAP['old-homepage'])
    programming_language = rdfMultiple(DOAP['programming-language'])
    releases = rdfMultiple(DOAP.release, range_type=DOAP.Version)
    svn_repository = rdfSingle(DOAP.repository, 'svn_repository',
            range_type=DOAP.SVNRepository)
    cvs_repository = rdfSingle(DOAP.repository, 'cvs_repository',
            range_type=DOAP.CVSRepository)
    oper_sys = rdfMultiple(DOAP['os'])
    screenshots = rdfMultiple(DOAP.screenshots)
    shortdesc = rdfMultiple(DOAP.shortdesc)
    tester = rdfMultiple(DOAP.tester, range_type=FOAF.Person)
    translator = rdfMultiple(DOAP.translator, range_type=FOAF.Person)
    wiki = rdfMultiple(DOAP.wiki)

class Release(rdfSubject):
    """A release class"""
    rdf_type = DOAP.Version
    revision = rdfSingle(DOAP.revision)
    name = rdfSingle(DOAP.name)
    created = rdfSingle(DOAP.created)
    file_releases = rdfMultiple(DOAP['file-release'])

class SVNRepository(rdfSubject):
    """Subversion repository classs"""
    rdf_type = DOAP.SVNRepository
    location = rdfSingle(DOAP.location)
    svn_browse = rdfSingle(DOAP.browse)

class CVSRepository(rdfSubject):
    """CVS repository class"""
    rdf_type = DOAP.CVSRepository
    anon_root = rdfSingle(DOAP['anon-root'])
    cvs_browse = rdfSingle(DOAP.browse)
    module = rdfSingle(DOAP.module)


mapper(Project, Release, CVSRepository, SVNRepository)

