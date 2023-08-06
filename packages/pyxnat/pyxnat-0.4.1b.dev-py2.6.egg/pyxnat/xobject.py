import os
import sys

module_path = os.path.dirname(os.path.abspath(__file__))

if os.path.join(module_path, 'externals') not in sys.path:
    sys.path.append(os.path.join(module_path, 'externals'))

import subprocess
import tempfile
import shutil
import time
from fnmatch import fnmatch
from configobj import ConfigObj

from lxml import etree
from tracked_memory import TrackedMemory

import xsearch
import xuri
from jsontable import JsonTable

# load externals if necessary
if int(sys.version[:5].replace('.', '')) < 260:
    from deque import Deque as deque
else:
    from collections import deque

try:
    import json
except:
    import simplejson as json

try:
    cfg_dir = \
        os.path.join(os.path.expanduser('~'), '.pyxnat') \
        if not 'win' in sys.platform \
        else os.path.join(os.path.expanduser('~'), 'pyxnat')

    shortcuts_path = os.path.join(cfg_dir, 'xnat_shortcuts.cfg')

    if not os.path.exists(cfg_dir):
        os.makedirs(cfg_dir)

    if not os.path.exists(shortcuts_path):
        shutil.copyfile( os.path.join(module_path, 'xnat_shortcuts.cfg'),
                         shortcuts_path
                       )
except:
    shortcuts_path = os.path.join(module_path, 'xnat_shortcuts.cfg')

xtype_path = os.path.join(module_path, 'xtype.cfg')

configobj_shortcuts = ConfigObj(shortcuts_path)
configobj_xtype = ConfigObj(xtype_path)

class SearchManager(object):
    """ Define constraints to make a complex search on the database.

        A search manager is avalaible as an Interface attribute.
        Its main usage is simply to be called to create a ``Search`` object 
        which will be responsible for specifying the returned data and for
        submitting the actual query.

        Some additional methods are provided to list, retrieve and delete
        saved search.

        Example:
            >>> query = [ ('xnat:subjectData/SUBJECT_ID', 'LIKE', '%'), 
                          ('xnat:projectData/ID', '=', 'my_project'),
                          [ ('xnat:subjectData/AGE', '>', '14'),
                            'AND'
                          ],
                          'OR'
                        ]
            >>> search = interface.search('my_search', query)
            >>>
            >>> # no search is saved because it was not submitted
            >>> interface.search.saved()
            []
            >>> # submit and get results
            >>> search.get_subjects()
            [...]
            >>> # now the search is saved
            >>> interface.search.saved()
            ['my_search']
            >>> 
            >>> same_search = interface.search.get('my_search')
    """
    def __init__(self, interface):
        self._interface = interface

    def __call__(self, name, query):
        """ Setups and returns a ``Search`` object. 

            .. warning::
                The search itself is not submitted here. The search is executed
                when a Search method like get_subjects(), which defines what
                kind of data is to be returned is called.
                
            Parameters
            ----------
            name: string
                Gives a name to the search to be able to retrieve it later.
                A name must be unique for a specific query.
            query: list
                This is the query that will be submitted to the server
                    A query is an unordered list that contains
                        - 1 or more constraints
                        - 0 or more sub-queries (lists as this one)
                        - 1 comparison method between the constraints 
                            ('AND' or 'OR')
                    A constraint is an ordered tuple that contains
                        - 1 valid searchable_type/searchable_field
                        - 1 operator among '=', '<', '>', '<=', '>=', 'LIKE'

            See also
            --------
            Search.get_table(), Search.get_subjects(), Search.get_experiments()
        """
        return Search(name, query, self._interface)

    def types(self, name_filter='*'):
        """ List the searchable types on the XNAT server.
        """
        return [ element_name
                 for element_name in JsonTable(
                     self._interface._engine.get_json('/REST/search/elements')
                                              ).fget_column('ELEMENT_NAME')
                 if fnmatch(element_name, name_filter)
               ]

    def type_fields(self, searchable_type):
        """ List the searchable fields for the given type on the XNAT server.
        """
        return [ field 
                 for field in JsonTable(
                         self._interface._engine.get_json(
                                                 '/REST/search/elements/%s' % \
                                                 searchable_type
                                                         )
                                       ).fget_column('FIELD_ID')
                 if '=' not in field
               ]

    def saved(self, asdict=False):
        """ Returns the list of saved search.

            .. warning ::
                Note that only submitted search are saved.

            Parameters
            ----------
            asdict: True or False
                | If False only the names of the saved searches are returned.
                | If True, a dictionnary with the names as keys and the
                  corresponding queries as values is returned.
                | Defaults to False.
        """
        if asdict:
            return self.__asdct()
        return self.__asdct().keys()

    def get(self, name):
        """ Returns a ``Search`` object for a saved search.

            Parameters
            ----------
            name: string
                Search name.

        """
        return Search(name, self.__asdct().get(name), self._interface)

    def delete(self, name):
        """ Removes a saved search and its results from the cache.

            Parameters
            ----------
            name: string
                Search name.

            Returns
            -------
            True if something was deleted.
            False if no search with that name existed.
        """
        to_delete = [ (args, kwargs)
                      for args, kwargs in \
                      self._interface._engine.submit_search.args_index
                      if args[0] == name
                    ]

        for args, kwargs in to_delete:
            self._interface._engine.submit_search.clear_tracks(*args, **kwargs)

        return to_delete != []

    def update(self, name):
        """ Re-submit all the queries that were made with the set of contraints
            of the given search.

            Parameters
            ----------
            name: string
                Search name.
        """
        search = Search(name, self.__asdct().get(name), self._interface)

        to_update = [ (args, kwargs)
                      for args, kwargs in \
                      self._interface._engine.submit_search.args_index
                      if args[0] == name
                    ]

        self.delete(name)

        for args, kwargs in to_update:
            self._interface._engine.submit_search(*args, **kwargs)

    def __asdct(self):
        return dict([ (args[0], args[-1])
                      for args, kwargs in \
                      self._interface._engine.submit_search.args_index
                   ])


class Search(object):
    def __init__(self, name, query, interface):
        self._query = query
        self._interface = interface

        self.name = name

    def get_tests(self, row_type, test_types, additional_columns=[]):

        return self.get_table( row_type, 
                               [ '%s/%s'%(test_type, field_name)
                                 for test_type in test_types
                                 for field_name in \
                                 self._interface.search.type_fields(test_type)
                               ] + additional_columns
                             )
        
    def get_table(self, row_type, columns=[]):
        """ Submits the defined search and returns a table.

            Parameters
            ----------
            row_type: string
                The returned table will have one line for every matching
                occurence of this type. 

                e.g. xnat:subjectData/SUBJECT_ID

            columns: list of strings
                The returned table will have all the given columns.
                The valid columns names are found through the ``types()``
                and ``type_fields()`` methods of :class:`SearchManager`.

            Returns
            -------
            A JsonTable object containing the results.
        """

        start = time.time()

        full_table = \
            JsonTable(
                self._interface._engine.submit_search( self.name,
                                                       row_type,
                                                       columns,
                                                       self._query
                                                     )
                     )

        subtable_headers = \
            [ column.split('/')[1].lower()
              if full_table.has_header(column.split('/')[1].lower())
              else column.replace(':', '_').replace('/', '_').lower()
              for column in columns
            ]

        print '%s results in %s seconds'%(len(full_table), time.time() - start)

        return full_table.fget_subtable(subtable_headers)

    def get_subjects(self):
        """ Returns a list of :class:`Subject` objects matching the query 
            constraints.
        """
        return [ Subject( ( '/REST/projects/%s'
                            '/subjects/%s' 
                          ) % (ids['project'], ids['subject_id']),
                          self._interface,
                          check_id=False
                        ) 
                 for ids in self.get_table( 'xnat:subjectData', 
                                            [ 'xnat:subjectData/PROJECT', 
                                              'xnat:subjectData/SUBJECT_ID'
                                            ]
                                          )
               ]

    def get_subjects_tests(self, test_types, additional_columns=[]):
        return self.get_tests( 'xnat:subjectData',
                               test_types,
                               [ 'xnat:subjectData/PROJECT', 
                                 'xnat:subjectData/SUBJECT_ID'
                               ] + additional_columns
                             )

    def get_experiments(self, experiment_type='xnat:mrSessionData'):
        """ Returns a list of :class:`Experiment` objects matching the query
            constraints.
        """    
        return [ Experiment( ( '/REST/projects/%s'
                               '/subjects/%s'
                               '/experiments/%s'
                             ) % ( ids['project'], 
                                   ids['subject_id'],
                                   ids['session_id']
                                 ),
                             self._interface,
                             check_id=False
                           )
                 for ids in self.get_table( experiment_type, 
                                            [ experiment_type + '/PROJECT', 
                                              experiment_type + '/SUBJECT_ID', 
                                              experiment_type + '/SESSION_ID'
                                            ]
                                          )
               ]


class Engine(object):
    """ Class that handles the actual queries on the XNAT server.

        .. note::
            A memory object puts the results of theses queries on a local
            cache. When a new resource is created on the server, all the 
            impacted cached queries are removed from the cache.
    """

    def __init__(self, server, user, password, datastore, interface):
        self.__credentials = (user, password)

        self._server = server
        self._cmd = "java -jar %s -host %s -u %s -p %s -m " % \
                    ( os.path.join( 
                            os.path.dirname(os.path.abspath(__file__)),
                            'tools/xdat-restClient-1.jar'
                                  ),
                      server,
                      user,
                      password
                    )

        self._stdin = deque([], 10)
        self._stdout = deque([], 10)
        self._stderr = deque([], 10)

        self._interface = interface

        # cache initialization
        if datastore == None:
            datastore = os.path.join( tempfile.gettempdir(), 
                                      '%s@%s'%( user, 
                                                server.split('//'
                                                            )[1].split(':')[0]
                                              )
                                    )

        elif not os.path.exists(datastore):
            os.makedirs(datastore)
        
        self._memory = TrackedMemory(datastore, save_npy=False)

        self.get_json = self._memory.cache(self.get_json)
        self.get_xml = self._memory.cache(self.get_xml)
        self.get_file = self._memory.cache(self.get_file)
        self.submit_search = self._memory.cache(self.submit_search)

    def _exec(self, uri, method):
        """ Executes a query on the XNAT server.

            Parameters
            ----------
            uri: string
                This is mainly the identifier of the resource that is being
                queried. More complex queries may also need a query string
                (separated by a '?') and may need some reference to local
                resources.
            method: PUT or POST or GET or DELETE
                The used http method.

            Returns
            -------
            Result as a string.

            Examples::

            +---------+-------------------------------------------------+
            | Method  | URI                                             |
            +=========+=================================================+
            | GET     | /REST/projects?format=csv                       |
            +-----------------------------------------------------------+
            | PUT     | /REST/projects/my_project/files/my_image.jpg    |
            |         |   -local '/tmp/image.jpg'                       |
            +---------+-------------------------------------------------+

        """
        self._stdin.append((uri, method))

        output = subprocess.Popen(
                    "%s %s -remote %s"%(self._cmd, method, uri), 
                    shell=True,
                    stdout=subprocess.PIPE
                                 ).communicate()[0]

        if 'ERROR CODE 13' in output:
            self._stderr.append(output)

            raise Exception('RestException: could not connect to server.')

        if 'You can get technical details' in output:
            self._stderr.append(output)

            raise Exception( 'RestException:'
                             'unsupported query --> %s %s'%(method, uri)
                           )      

        self._stdout.append(output)

        return output

    def get_json(self, uri):
        """ Executes a 'GET' query asking the returned data to be in json.
        """
        return json.dumps(
                    json.loads(self._exec(uri+'?format=json', 'GET')
                              )['ResultSet']['Result']
                         )

    def get_xml(self, uri):
        """ Executes a 'GET' query asking the returned data to be in xml.
        """
        return self._exec(uri+'?format=xml', 'GET')

    def get_file(self, uri):
        """ Executes a 'GET' query on a file resource. The file is saved
            in the local cache.
        """
        file_name = xuri.get_id(uri)
        dest_dir = \
            os.path.join( self._memory.cachedir,
                          *xuri.strip_id(uri).lstrip('/').split('/')
                        )

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        fd = open(os.path.join(dest_dir, file_name), 'wb')
        fd.write(self._exec(uri, 'GET'))
        fd.close()

        return os.path.join(dest_dir, file_name)

    def put_resource(self, uri):
        """ Executes a 'PUT' statement to create a new resource on the server.
            All the cached data that is impacted is removed.

            e.g. If a new subject is created, the list of subjects cached
                 locally is no longer valid so simply destroyed.
        """
        XKlass = globals()[xuri.level(uri).rsplit('s', 1)[0].capitalize()]
        XKlass(uri, self._interface).cache.clear()

        self._exec(uri, 'PUT')

    def put_file(self, uri):
        """ Executes a 'PUT' statement to put a new file on the server.
            All the cached data that is impacted is removed.

            See also
            --------
            Engine.put_resource()
        """
        remote, local = uri.split(' -local ')
        remote = xuri.strip_qr(remote)

        XKlass = globals()[xuri.level(remote).rsplit('s', 1)[0].capitalize()]
        XKlass(remote, self._interface).cache.clear()

        self._exec(uri, 'PUT')

    def del_resource(self, uri):
        """ Executes a 'DELETE' statement to delete a resource on the server.
            All the cached data that is impacted is removed.
        """
        XKlass = globals()[xuri.level(uri).rsplit('s', 1)[0].capitalize()]
        XKlass(uri, self._interface).cache.clear()

        self._exec(uri, 'DELETE')

    def del_file(self, uri):
        """ Executes a 'DELETE' statement to delete a file on the server.
            All the cached data that is impacted is removed.
        """
        local_file = os.path.join( self._memory.cachedir,
                                   *uri.lstrip('/').split('/')
                                 )

        if os.path.exists(local_file):
            os.remove(local_file)

        return self.del_resource(uri)

    def submit_search(self, search_name, row_type, columns, query):
        """ 'POST' an xml containing the description of a complex search.

            A complex search is composed of:
                - a series of constraints
                - a description of the data that is to be returned

            See also
            -------- 
            Search and SearchManager objects.
        """
        search_document = \
            xsearch.build_search_document(row_type, columns, query)

        return json.dumps(
                   json.loads(
                       self._exec( "/REST/search?format=json -local %s" % \
                                                               search_document, 
                                   'POST'
                                 )
                             )['ResultSet']['Result']
                         )


class CacheManager(object):
    """ Manual manager for the cached data.

        The cache management is mainly transparent but it is useful sometimes
        to do theses actions manually.

        A cache manager is linked to a ResourceObject and only works upon 
        the cached data related to this object.
        
        e.g. If the ResourceObject is a subject, related data may be:
                 - its files
                 - its experiments
                 - the list of subjects from its project

        The cache manager should be accessed through the `cache` attribute
        of its corresponding resource.

        >>> subject.cache.checkout(attrib=True, files=True, recursive=True)
        >>> subject.cache.update()
        >>> subject.cache.clear()
    """
    def __init__(self, robj):
        """
            Parameters
            ----------
            robj: ResourceObject
                The :class:`ResourceObject` the cache manager is linked to.
        """
        self._robj = robj
        self._interface = robj._interface
        self._engine = self._interface._engine

    def __repr__(self):
        jsons, xmls, files = self.status()

        _repr_ = "======================================================\n"

        if self._robj._uri == '/REST':
            _repr_ += "Cache entries for Interface\n"
        
        else:
            _repr_ += "Cache entries for %s %s\n" % ( self._robj.level(),
                                                     self._robj.id()
                                                   )
 
        _repr_ += "======================================================\n"
        _repr_ += "+ json cached\n"

        for uri in jsons:
             _repr_ += '  - ' + uri + '\n'

        _repr_ += "------------------------------------------------------\n"
        _repr_ += "+ xml cached\n"

        for uri in xmls:
             _repr_ += '  - ' + uri + '\n'

        _repr_ += "------------------------------------------------------\n"
        _repr_ += "+ files cached\n"

        for uri in files:
             _repr_ += '  - ' + uri + '\n'

        _repr_ += "------------------------------------------------------\n"

        return _repr_

    def __str__(self):
        return self.__repr__()

    def status(self):
        """ Returns the URIs of the cached data related to the ResourceObject.
        """
        if self._robj._uri == '/REST':
            return \
                [args[0] for args, kwargs in self._engine.get_json.args_index],\
                [args[0] for args, kwargs in self._engine.get_xml.args_index],\
                [args[0] for args, kwargs in self._engine.get_file.args_index]
        else:
            return \
                [ args[0]
                  for args, kwargs in \
                      self._engine.get_json.args_index
                  if xuri.is_related(self._robj._uri, args[0])
                ], \
                [ args[0]   
                  for args, kwargs in \
                      self._engine.get_xml.args_index
                  if xuri.is_related(self._robj._uri, args[0])
                ], \
                [ args[0]
                  for args, kwargs in \
                      self._engine.get_file.args_index
                  if xuri.is_related(self._robj._uri, args[0])
                ]

    def checkout(self, attrib=False, files=False, recursive=True):
        """ Put all the resources related to this object in the local datastore.

            Parameters
            ----------
            attrib: True or False
                Caches the objects attributes.
            files: True or False
                Downloads attached files if any.
            recursive: True or False
                Iterates through the object descendants and caches them as
                well with the same 'attrib' and 'files' parameters.
        """
        if self._robj._uri == '/REST':
            for proj_id in self._robj.projects():
                self._robj.project(proj_id).cache.checkout( attrib, 
                                                            files, 
                                                            recursive
                                                          )

        else:
            print self._robj.level(), self._robj.id()

            if attrib and self._robj.level() not in ['resource', 'file']:
                self._robj.attrib.as_dict()

            if files and self._robj.level() == 'file':
                self._robj.get()

            for child_resource in \
                configobj_xtype[self._robj.level()]['children']:

                for child_id in getattr(self._robj, child_resource + 's')():
                    if recursive:
                        getattr(self._robj, child_resource
                               )(child_id).cache.checkout( attrib, 
                                                           files, 
                                                           recursive
                                                         )

    def update(self):
        """ Go through all the cached data and checks whether or not it matches
            the data on the server. 
            Non-matching data is updated.
        """
        jsons, xmls, files = self.status()

        for uri in jsons:
            if self._engine.get_json(uri) != self._engine.get_json.call(uri):
                print '[U]',
            else:
                print '[N]',
            print uri

        for uri in xmls:
            if self._engine.get_xml(uri) != self._engine.get_xml.call(uri):
                print '[U]',
            else:
                print '[N]',
            print uri

        for uri in files:
            if int(File(uri, self._interface).size()) != \
               int(str(os.path.getsize(File(uri, self._interface).get()))):
                self._engine.get_file.call(uri)
                print '[U]',
            else:
                print '[N]',
            print uri

    def clear(self):
        """ Clears the cached data for this object.
        """
        if self._robj._uri == '/REST':
            self._robj._engine._memory.clear()
        else:
            # remove local files
            uri = self._robj.full_uri() \
                if self._robj.level() == 'file' and \
                self._robj.full_uri() != None else \
                self._robj._uri

            local_path = \
                os.path.join( self._engine._memory.cachedir,
                              *uri.lstrip('/').split('/')
                            )

            if os.path.exists(local_path):
                if os.path.isdir(local_path):
                    shutil.rmtree(local_path)
                elif os.path.isfile(local_path):
                    os.remove(local_path)
                else:
                    print ( 'CacheWarning: local path %s exists'
                            'but is neither a file nor a directory.'
                            'It will have to be deleted manually.'
                          ) % (local_path)

            # remove remote entries
            jsons, xmls, files = self.status()

            [self._engine.get_json.clear_tracks(uri) for uri in jsons]
            [self._engine.get_xml.clear_tracks(uri) for uri in xmls]
            [self._engine.get_file.clear_tracks(uri) for uri in files]

# --------------------------------------------------------------------------- #

def list_resource_children(child_resource):
    """ Used in the XType metaclass to generate a method that returns a list
        of children resource identifiers.
    """
    def sub_func(self, id_filter='*'):
        """
            Parameters
            ----------
            id_filter: string
                Filters the identifiers list according to the given pattern.
        """
        id_header = configobj_xtype[child_resource]['id']
        results = self._interface._engine.get_json( '%s/%ss' % \
                                                     (self._uri, child_resource)
                                                  )

        return JsonTable(results).get_column(id_header, id_filter)
    return sub_func

def get_resource_object(child_resource):
    """ Used in the XType metaclass to generate a method that returns 
        the :class:`ResourceObject` for the specified resource.
    """
    def sub_func(self, ID):
        """
            Parameters
            ----------
            ID: string
                Identifier of the resource.
        """
        return globals()[child_resource.capitalize()]( self._uri+'/%ss/%s' % \
                                                         (child_resource, ID),
                                                       self._interface
                                                     )
    return sub_func


class XType(type):
    """ The ResourceObjects share a common interface for management 
        (e.g. create). They need a specialized one for listing their children
        resources since it is resource level dependent.

        This metaclass provides a way to create dynamically an accessor
        interface for the resource children on basing itself on a description
        of the resources in a configuration file ('xtype.cfg').

        Two methods are created for each resource child:
            child_resource(child_ID):
                returns the ResourceObject for that resource.

            child_resource_names():
                return a list of identifiers for that kind of resource.

        .. note::
            A Subject object will have the following generated methods:
                - experiment & experiments
                - resource & resources
                - file & files
    """
    def __new__(cls, name, bases, dct):
        for child_rsc in \
            configobj_xtype[name.lower()]['children']:

            dct[child_rsc+'s'] = list_resource_children(child_rsc)
            dct[child_rsc] = get_resource_object(child_rsc)

        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(XType, cls).__init__(name, bases, dct)
        

class ResourceObject(object):
    """ All REST resources objects are derived from ResourceObject which 
        contains the common mechanisms to read and write on the server.
    """
    def __init__(self, uri, interface, check_id=True):
        """
            Parameters
            ----------
            uri: string
                Uniform Resource Identifier
            interface: :class:`Interface`
                It contains the necessary information and mechanisms to query
                the database.
            check_id: True or False
                The resource `id` may be a custom label or the actual unique id.
                The uri of a :class:`ResourceObject` must always contain the
                real id. 
                Setting this parameter to True ensures this by making a query 
                on the server. 
                Setting it to False skips this step.
        """
        self._uri = xuri.strip_qr(uri)
        self._interface = interface

        if check_id and xuri.get_id(uri) == self.label():
            self._uri = xuri.join(xuri.strip_id(uri), self.id())

        self.cache = CacheManager(self)

    def __repr__(self):
        return '<%s %s>'%(self.__class__.__name__, xuri.get_id(self._uri))

    def __getcell__(self, col_name):
        if self.exists():
            used_id = xuri.get_id(self._uri)
            parent_uri = xuri.strip_id(self._uri)

            jtable = JsonTable(self._interface._engine.get_json(parent_uri))

            if '*' in col_name:
                return jtable.vfilter([used_id]).get_column(col_name)[0]
            else:
                return jtable.vfilter([used_id]).fget_column(col_name)[0]

    def level(self):
        """ Returns the level of the resource corresponding to this object.
            e.g. 'project', 'subject' etc...            
        """
        return self.__class__.__name__.lower()

    def id(self):
        """ It depends on the resource, but some resources may be accessed
            through their id or through their label. The method returns the
            actual id of the resource.
        """
        id_header = \
            configobj_xtype[self.level()]['id']

        return self.__getcell__(id_header)

    def label(self):
        """ It depends on the resource, but some resources may be accessed
            through their id or through their label. The method returns the
            actual label of the resource if available. If not, it will return
            a valid id.
        """
        label_header = \
            configobj_xtype[self.level()]['label']

        return self.__getcell__(label_header)

    def type(self):
        """ Returns the ``xnat_type`` which is defined in the XNAT schema
            of this ``ResourceObject``.

            .. note:

            +----------------+-----------------------+
            | ResourceObject | possible xnat types   |
            +================+=======================+
            | Project        | xnat:projectData      |
            +----------------+-----------------------+
            | Subject        | xnat:subjectData      |
            +----------------+-----------------------+
            | Experiment     | xnat:mrSessionData    | 
            |                | xnat:petSessionData   | 
            +----------------+-----------------------+
        """
        return self.__getcell__('element_name')

    def exists(self):
        """ Test whether this object actually exists.

            Returns
            -------
            True or False
        """
        parent_uri = xuri.strip_id(self._uri)
        used_id = xuri.get_id(self._uri)

        return JsonTable(self._interface._engine.get_json(parent_uri)
                        ).vfilter([used_id]) != []

    def create(self, xnat_type=None):
        """ Creates the corresponding element on the XNAT server.

            .. note::
                The xnat_type is defined in the XNAT XML Schema. It allows
                a generic type such as ``xnat:experimentData`` to be derived in
                ``xnat:mrSessionData`` and ``xnat:petSessionData`` to be given
                some specific attributes.

            Parameters
            ----------
            xnat_type: string or None
                If not None, it will affect the given schema type to the created
                element. If None, a default schema type is given, depending on
                the object type.

            See also
            --------
            ResourceObject.type()
        """
        create_uri = \
            self._uri if xnat_type is None \
                      else self._uri + '?xsiType=%s' % xnat_type

        self._interface._engine.put_resource(create_uri)

        return self

    def delete(self, delete_files=True):
        """ Deletes the corresponding resource on the XNAT server.

            Parameters
            ----------
            delete_files: True or False
                Files attached to the resource may be kept or not on the server
                when the object is deleted. Defaults to True.
        """
        delete_uri = \
            self._uri if not delete_files else self._uri + '?removeFiles=true'

        return self._interface._engine.del_resource(delete_uri)


class Interface(object):
    """ Class that holds the properties to access a XNAT server.

        >>> interface = Interface( server='http://central.xnat.org:8080',
                                   user='login',
                                   password='pwd',
                                   datastore='/tmp'
                                 )
    """
    __metaclass__ = XType

    def __init__(self, server, user, password, datastore=None):
        """
            Parameters
            ----------
            server: string
                The full server URL, including the port if necessary.
            user: string   
                A valid login registered through the XNAT web interface.
            password: string
                The user's password.
            datastore: string or None
                The path of the base directory to use as a data store. If
                None is given a temporary directory will be created and used
                but the cache will not be persistent.
        """                            
        self._uri = '/REST'
        self._interface = self

        self._user = user
        self._server = server
        self._engine = Engine(server, user, password, datastore, self)

        self.cache = CacheManager(self)
        self.search = SearchManager(self)

class Project(ResourceObject):
    """ Specialized ResourceObject class for projects.
    """
    __metaclass__ = XType

    def __init__(self, uri, interface, check_id=True):
        ResourceObject.__init__(self, uri, interface, check_id)
        self.attrib = Attrib(self)

    def type(self):
        return 'xnat:projectData'


class Subject(ResourceObject):
    """ Specialized ResourceObject class for subjects.
    """
    __metaclass__ = XType

    def __init__(self, uri, interface, check_id=True):
        ResourceObject.__init__(self, uri, interface, check_id)
        self.attrib = Attrib(self)

    def type(self):
        return 'xnat:subjectData'


class Experiment(ResourceObject):
    """ Specialized ResourceObject class for experiments.
    """
    __metaclass__ = XType

    def __init__(self, uri, interface, check_id=True):
        ResourceObject.__init__(self, uri, interface, check_id)
        self.attrib = Attrib(self)

    def create(self, xnat_type='xnat:mrSessionData'):
        return super(Experiment, self).create(xnat_type)


class Scan(ResourceObject):
    """ Specialized ResourceObject class for scans.
    """
    __metaclass__ = XType

    def __init__(self, uri, interface, check_id=True):
        ResourceObject.__init__(self, uri, interface, check_id)
        self.attrib = Attrib(self)

    def create(self, xnat_type='xnat:mrScanData'):
        return super(Scan, self).create(xnat_type)


class Resource(ResourceObject):
    """ Specialized ResourceObject class for resources.
    """
    __metaclass__ = XType

    def __init__(self, uri, interface, check_id=True):
        ResourceObject.__init__(self, uri, interface, check_id)


class File(ResourceObject):
    """ Specialized ResourceObject class for files.
    """
    __metaclass__ = XType

    def __init__(self, uri, interface):
        ResourceObject.__init__(self, uri, interface, check_id=False)

    def size(self):
        """ 
            Returns
            -------
            The size of the file in bytes as a string.
        """
        return self.__getcell__('Size')

    def tags(self):
        """ 
            Returns
            -------
            The specified tags for this file.
        """
        return self.__getcell__('file_tags').strip('\'')

    def format(self):
        """ 
            Returns
            -------
            The specified format for this file.

            e.g. NIFTI, DICOM, jpeg
        """
        return self.__getcell__('file_format').strip('\'')

    def content(self):
        """ 
            Returns
            -------
            The specified content for this file.

            e.g. T1, DTI, sequence preview
        """
        return self.__getcell__('file_content').strip('\'')

    def full_uri(self):
        return self.__getcell__('URI')

    def resource(self):
        return Resource(xuri.parent(self.__getcell__('URI')), self._interface)

    def get(self):
        """ Downloads the file if it is not in the local cache.

            .. note::
                It is not possible to define a custom path for the download
                because files are kept in the datastore and managed with the
                cache manager.            

            Returns
            -------
            The file path as a string.
        """
        if xuri.level(xuri.parent(self._uri)) != 'resources':
            return self.resource().file(xuri.get_id(self._uri)).get()
        else:
            return self._interface._engine.get_file(self._uri)

    def put(self, local_file, format='undefined', \
                  content='unknown', tags='none'):
        """ Uploads a local file on the server.

            Returns
            -------
            True if successful, False otherwise.
        """
        format = "'%s'"%format if ' ' in format else format
        content = "'%s'"%content if ' ' in content else content
        tags = "'%s'"%tags if ' ' in tags else tags

        put_uri = \
            "\"%s?%s\" -local %s" % ( self._uri,
                                      '&'.join([ 'format=%s'%format, 
                                                 'content=%s'%content, 
                                                 'tags=%s'%tags
                                               ]),
                                      local_file
                                    )

        return self._interface._engine.put_file(put_uri)

    def delete(self):
        """ Removes the file from the server and from the cache if necessary.
        """
        return self._interface._engine.del_file(self.__getcell__('URI'))


class Attrib(object):
    """ Class that provides access to a resource metadata.

        It behaves mainly as a dictionnary that synchronizes itself with
        the server.
    """
    def __init__(self, robj):
        """
            Parameters
            ----------
            robj: ResourceObject
                The ResourceObject it is linked to.        
        """
        self._robj = robj
        self._interface = robj._interface
        self._map = configobj_shortcuts[robj.level()]

    def __repr__(self):
        return 'Attrib(%s)' % repr(self.as_dict())

    def __getitem__(self, name):
        """ Returns the value of the specified attribute.
            Raises an exception if the attribute does not exists.

            e.g. subject.attrib['label']

            .. note::
                There is no XNAT REST method to directly get the value of a
                specific attribute so an xml file with all the data attached
                to the resource is downloaded and then parsed.
        """
        name_in_schema = self._map[name].split('/')[-1]

        xml_root = \
            etree.fromstring(
                    self._interface._engine.get_xml(self._robj._uri)
                            )

        token_xpath = ['/*']
        for token in self._map[name].split('/'):

            if ':' not in token and '[' not in token:
                token_xpath.append("*[local-name()='%s']"%token)
            elif '[' in token:
                node_name, xsi_type = token.rstrip(']').split('[')

                xsi_type = xsi_type if xsi_type[0] == '@' else '@' + xsi_type
                xsi_type = xsi_type.replace('=', '=\'') + '\''

                token_xpath.append( "*[local-name()='%s'][%s]" % \
                                    (node_name, xsi_type)
                                  )
            else:
                pass

        element = \
            xml_root.xpath( '/'.join(token_xpath),
                            namespaces=xml_root.nsmap
                          )

        attribute = \
            xml_root.xpath( '/'.join(token_xpath[:-1]) + '[@%s]' % \
                            name_in_schema,
                            namespaces=xml_root.nsmap
                          )

        # I hope xnat rest api works this way for every 'field' in 'fields'
        if token_xpath[-1] == "*[local-name()='field']":
            val = xml_root.xpath( '/'.join(token_xpath[:-1]),
                                   namespaces=xml_root.nsmap
                                )[0].getchildren()[0].tail.strip('\'')

        elif element != [] and attribute != []:
            raise Exception( ( "AttribException: path "
                               "for attribute '%s'"
                               "is ambigious, two "
                               "possible values (%s and %s)"
                             ) % ( name, 
                                   element[0].text,
                                   attribute[0].get(name_in_schema)
                                 )
                           )
        elif element != []:
            val = element[0].text.strip('\'')
        elif attribute != []:
            val = attribute[0].get(name_in_schema).strip('\'')            
        else:
            return

        # if the set value is '', it is stored with its ascii character on xnat
        if val != '39#':
            return val
        return 

    def __setitem__(self, name, val):
        """ Sets the value of the specified attribute.

            See also
            --------
            Attrib.update()
        """
        self.update({name:val})

    def as_dict(self):
        """
            Returns
            -------
            The attributes names and values as a standard python dict.
        """
        return dict(self.items())

    def get(self, name):
        """ Returns the value of the specified attribute.
            Returns None if the attribute does not exists.
        """
        if self.has_key(name):
            return self[name]

    def has_key(self, name):
        """ Test whether this resource has the specified attribute.
        """
        return name in self.keys()

    def items(self):
        """
            Returns
            -------
            The attributes names and values as a list of 2-tuples.
        """
        return zip(self.keys(), self.values())

    def keys(self):
        """ List of all the available attributes names for this resource. 
        """
        return self._map.keys()

    def set(self, name, val):
        """ Sets the value of the specified attribute.

            See also
            --------
            Attrib.update()
        """
        if self.has_key(name):
            self.update({name:val})
            return True
        return False

    def update(self, dct):
        """ Takes a dictionnay and update the attributes with its values.
            
            It is recommanded to use this method when more than one value
            has to be set because this way, they are all uploaded in a single
            shot.

            Parameters
            ----------
            dct: dict
                The dictionnary.
        """
        if dct != {}:
            for key in dct.keys():
                dct[key] = "39#" if str(dct[key]) == '' or dct[key] == None \
                                 else dct[key]

            set_values = \
                ['%s=%s'%(self._map[key], dct[key]) for key in dct.keys()]

            self._interface._engine.put_resource(
                            '"%s?xsiType=%s&%s"' % ( self._robj._uri,
                                                     self._robj.type(),
                                                     '&'.join(set_values)
                                                   )
                                                )

            dct.clear()
            return True
        return False

    def values(self):
        """ Returns all the values of the attributes as a list.
        """
        return [self.get(key) for key in self.keys()]


