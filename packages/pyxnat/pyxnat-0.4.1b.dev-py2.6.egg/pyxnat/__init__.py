""" Pyxnat is a simple python library that relies on the REST API provided
by the XNAT platform since its 1.4 version. XNAT is an extensible database for neuroimaging data. The main objective is to ease communications with an XNAT
server to plug-in external tools or python scripts to process the data. It
features:

    #. resources browsing capabilities
    #. read and write access to resources
    #. complex searches
    #. disk-caching of requested files and resources

.. [#] http://www.xnat.org/
.. [#] http://packages.python.org/pyxnat/

____

    **A short overview**    

    *Setup the connection*
        >>> from pyxnat import Interface
        >>> interface = Interface(server='http://central.xnat.org:8080',
                                  user='login',
                                  password='pass',
                                  datastore=os.path.join( os.path.expanduser('~'),
                                                          'XnatStore'
                                                        )
                                 )

    *Browse the resources*
        >>> interface.projects()
        [u'CENTRAL_OASIS_CS', u'CENTRAL_OASIS_LONG', ...]

    *Create new resources*
        >>> interface.project('my_project').create()
        >>> interface.project('my_project').file('image.nii').put('/tmp/image.nii')

    *Metadata support*
        >>> proj = interface.project('my_project')
        >>> proj.attrib.keys()
        ['note','alias','secondary_ID','name','pi_lastname',
         'label','keywords','pi_firstname','ID','description']
        >>> proj.attrib.set('note', 'a note')
        >>> proj.attrib.get('note')
        'a note'

    *Make complex searches*
        >>> search = interface.search( 'my_search',
                                       [ ('xnat:subjectData/SUBJECT_ID','LIKE','%'),
                                         ('xnat:subjectData/PROJECT', '=', 'my_project'),
                                         'AND'
                                       ]
                                     )
        >>> search.get_subjects()
"""

__version__ = '0.4.1b'

import os
import sys

module_path = os.path.dirname(os.path.abspath(__file__))

if os.path.join(module_path, 'externals') not in sys.path:
    sys.path.append(os.path.join(module_path, 'externals'))

from .xobject import Interface, SearchManager, Search, CacheManager, \
                     ResourceObject, Project, Subject, Experiment, Scan, \
                     Resource, File, Attrib

from .xobject import module_path as xnatrest_path
from .xobject import shortcuts_path as xnatrest_shortcuts

