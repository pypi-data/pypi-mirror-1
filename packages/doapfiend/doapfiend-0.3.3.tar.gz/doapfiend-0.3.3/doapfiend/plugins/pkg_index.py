
'''

Plugin helper to fetch a single DOAP file from doapspace.org
by Package Index

'''

from doapfiend.utils import fetch_file

PKG_INDEX_URI = 'http://doapspace.org/doap'
OHLOH_URI = 'http://rdfohloh.wikier.org/project/'


def get_by_pkg_index(index, project_name, proxy=None):
    '''
    Get DOAP for a package index project name from doapspace.org

    Builtin indexes:

       - 'sf' SourceForge
       - 'fm' Freshmeat
       - 'py' Python Package Index
       - 'oh' Project listed on Ohlo

    Raises doaplib.utils.NotFound exception on HTTP 404 error

    @param index: Package index two letter abbreviation
    @type index: string

    @param project_name: project name
    @type project_name: string

    @param proxy: Optional HTTP proxy URL
    @type proxy: string

    @rtype: string
    @return: text of file retrieved

    '''
    if index == 'oh':
        url = '%s/%s/rdf' % (OHLOH_URI, project_name)
    else:
        url = '%s/%s/%s' % (PKG_INDEX_URI, index, project_name)
    return fetch_file(url, proxy)

