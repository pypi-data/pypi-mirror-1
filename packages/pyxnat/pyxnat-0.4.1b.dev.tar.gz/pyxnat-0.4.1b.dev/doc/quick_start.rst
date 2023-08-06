==============================
Quick start
==============================

.. currentmodule:: pyxnat.xobject

This is a short tutorial going through the main features of this API. 
Depending on the policy of the XNAT server you are using, and your user level, 
you can have read and write access to a specific set of resources. During this
tutorial, we will use a `fake` standard user account on the XNAT Central 
repository, where you will have limited access to a number of projects and
full access to the projects you own.

.. note::
    XNAT Central is a public XNAT repository managed by the XNAT team and 
    updated regularly with the latest improvements of the development branch.
    
_____

.. [#]  http://central.xnat.org
    

Connect to the server
------------------------

Connecting to a XNAT server requires valid credentials so you might want to
start by requesting those on the Web interface of your server. 

>>> from pyxnat import Interface
>>> interface = Interface(server='http://central.xnat.org:8080',
                          user='my_login',
                          password='my_pass',
                          datastore=os.path.join( os.path.expanduser('~'),
                                                  'XnatStore'
                                                )
                         )

The datastore argument specifies where the local disk-cache will be stored.
Every query and every downloaded file will be stored here so choose a location
with sufficient free space. If the datastore argument if not given, a temporary
location is picked automatically but it may be flushed at every reboot of the 
machine. Here the datastore argument is set to a `XnatSore` directory in the
user's home directory in a cross platform manner.

.. warning::
    Depending on the server configuration, you may have to include the port 
    in the server url, as well as the name of the XNAT tomcat application. 
    So you might end up with somthing like:
    http://server_ip:port/xnat


Browse the resources
--------------------

Now that we have an `Interface` object, we can start browsing the server::

    >>> interface.projects()
    [..., u'CENTRAL_OASIS_CS', u'CENTRAL_OASIS_LONG', ...]
    >>> # with an optional filter argument
    >>> interface.projects('*OASIS_CS*')
    [u'CENTRAL_OASIS_CS']
    >>> oasis_cs = interface.project('OASIS_CS')
    >>> oasis_cs.exists()
    True
    >>> oasis_cs.subjects()
    [..., u'OAS1_0307', u'OAS1_0308', u'OAS1_0309', u'OAS1_0310', ...]
    >>> oasis_cs.subject('OAS1_0307').experiments()
    [u'OAS1_0307_CLIN_1', u'OAS1_0307_MR1']

Resources operations
--------------------

Several operations are accessible for every resource level. The most importants
are responsible for creating new resources, deleting existing one and testing
whether a given resource exists or not::

    >>> my_project = interface.project('my_project')
    >>> my_project.exists()
    False
    >>> my_project.create()
    >>> my_project.exists()
    True
    >>> subject_1 = my_project.subject('first_subject')
    >>> subject_1.create()
    >>> subject_1.delete()
    >>> subject_1.exists()
    False

For some levels, it is possible to give a xnat_type argument to the create
method, so that the resource is created accordingly::

    >>> subject1.create()
    >>> subject1.experiment('pet_session').create('xnat:petSessionData')

Other common operations are available such as::

    >>> experiment = oasis_cs.subject('OAS1_0307').experiment('OAS1_0307_MR1')
    >>> experiment.type()
    'xnat:mrSessionData'
    >>> experiment.level()
    'experiment'
    >>> experiment.id()
    'OAS1_0307_MR1'
    >>> experiment.label()
    'OAS1_0307_MR1'

See the ``ResourceObject`` class reference documentation for further details.

File support
------------

It is possible to upload and then download files at every resource level. 
When grouping files makes sense, it is possible to use a level 
called ``resources``::

    >>> my_project.files()
    []
    >>> my_project.file('image.nii').put('/tmp/image.nii')
    >>> # you can add any of the following arguments to give additional information
          on the file you are uploading
    >>> my_project.file('image.nii').put( '/tmp/image.nii', 
                                          content='T1', 
                                          format='NIFTI'
                                          tags='image test'
                                        )
    >>> my_project.file('image.nii').size()
    98098
    >>> my_project.file('image.nii').content()
    'T1'
    >>> my_project.file('image.nii').format()
    'NIFTI'
    >>> my_project.file('image.nii').tags()
    'image test'
    >>> my_project.file('image.nii').get()
    '~/XnatStore/REST/projects/my_project/resources/123150742/files/image.nii'
    >>> # grouping files
    >>> my_project.resource('ANALYZE').file('image.hdr').put('/tmp/image.hdr')
    >>> my_project.resource('ANALYZE').file('image.img').put('/tmp/image.img')
    >>> my_project.resources()
    ['123150742', 'ANALYZE']
    >>> my_project.resource('ANALYZE').files()
    ['image.hdr', 'image.img']
    >>> my_project.resource('ANALYZE').file('image.hdr').get()
    '~/XnatStore/REST/projects/my_project/resources/ANALYZE/files/image.hdr'
    >>> my_project.resource('ANALYZE').file('image.img').get()
    '~/XnatStore/REST/projects/my_project/resources/ANALYZE/files/image.img'

.. note::
    For the `image.nii`, the ``resources`` level is implicit and an ID
    for that level is generated automatically.

Metadata support
----------------

Each resource level also has a set of metadata fields that can be informed. This
set of fields depends on the resource level and on its type in the XNAT schema::

    >>> my_project.attrib.keys()
    ['note','alias','secondary_ID','name','pi_lastname',
     'label','keywords','pi_firstname','ID','description']
    >>> my_project.attrib.set('note', 'a note')
    >>> my_project.attrib.get('note')
    'a note'
    >>> my_project.attrib.update({'pi_lastname':'doe', 'pi_firstname':'john'})
    >>> # when using a method that does not commit automatically to the server
    >>> my_project.attrib['description'] = 'a description here'
    >>> # use the manual commit method
    >>> my_project.attrib.commit()
    
See the ``Attrib`` class reference documentation for further details.

.. note::
    The list of fields is actually generated from a config file so one can
    set a convenient shortcut on the XNAT schema.
    
    e.g. Choose your shortcut by editing the configuration file:
        - description = xnat:projectData/description
        - desc = xnat:projectData/description

    The configuration file is called ``xnat_shortcuts.cfg`` and is located
    in `$HOME/.pyxnat` under Unix and in `$HOME/pyxnat` under Windows.

.. warning::
    The list of fields is not generated knowing the type of the resource in
    the XNAT schema. 
    
    It means that an experiment will have both:
        - tracer_isotope = xnat:petSessionData/tracer/isotope/half-life
        - coil = xnat:mrSessionData/coil

    But if the experiment it a mrSessionData, it will not be able to set 
    `tracer_isotope` and `tracer_isotope` value will always be ``None``.

_____

.. [#] http://nrg.wikispaces.com/XNAT+REST+XML+Path+Shortcuts

Make complex searches
---------------------

The XNAT search engine can be queried via the REST model. The following query
finds all the subjects that are within `my_project` or that have an age superior
to 14::

    >>> search = interface.search( 'my_search',
                                   [ ('xnat:subjectData/SUBJECT_ID','LIKE','%'),
                                     ('xnat:subjectData/PROJECT', '=', 'my_project'),
                                     'OR',
                                     [ ('xnat:subjectData/AGE','>','14'),
                                       'AND'
                                     ]
                                   ]
                                 )
    >>> search.get_subjects()

See the ``Search`` and ``SeachManager`` classes reference documentation for
further details.

