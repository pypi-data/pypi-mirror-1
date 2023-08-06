import os
import sys
from fnmatch import fnmatch


module_path = os.path.dirname(os.path.abspath(__file__))

if os.path.join(module_path, 'externals') not in sys.path:
    sys.path.append(os.path.join(module_path, 'externals'))

try:
    import json
except:
    import simplejson as json


class JsonTable(list):
    def __init__(self, jstr):
        if jstr == None:
            list.__init__(self, [])
        else:
            list.__init__(self, json.loads(jstr))

    def dump(self, file_location, leading=[], trailing=[], sep=','):
        sep_rpl = '.' if sep != '.' else ','

        fd = open(file_location, 'wb')

        if self != []:
            csv = '\n'.join( [ sep.join([ str(val).replace(sep, sep_rpl) 
                                          for val in row
                                        ])
                               for row in self.as_list(leading, trailing)
                             ]
                           )

        fd.write(csv)
        fd.close()

    def as_list(self, leading=[], trailing=[]):
        between = [ header
                    for header in self.get_headers() 
                    if header not in leading and header not in trailing
                  ]

        ordered_headers = leading + between + trailing

        return [ ordered_headers ] + \
               [ [ row[header] 
                   for header in ordered_headers 
                   if self.has_header(header)
                 ]
                 for row in self
               ]

    def has_header(self, name):
        if self != []:
            return name in self.get_headers()
        return False

    def get_headers(self):
        if self != []:
            return self[0].keys()    

    def get_column(self, col_name, col_filter='*'):
        return [ entry[col_name] 
                 for entry in \
                 self.get_subtable([col_name]).kwfilter({col_name:col_filter})
               ]

    def fget_column(self, col_name):
        return [ entry[col_name] 
                 for entry in self.fget_subtable([col_name])
               ]

    def get_subtable(self, col_names=[]):
        sub_table = []

        for entry in self:
            row = ()

            for col_name in col_names:
                for key in entry.keys():
                    if fnmatch(key, col_name):
                        row += (entry[key], )
                        break

            sub_table.append(row)

        return self.__class__( json.dumps([ dict(zip(col_names, row))
                                            for row in sub_table
                                         ])
                             )

    def fget_subtable(self, col_names=[]):
        sub_table = [ [ (col_name, entry[col_name])
                        for col_name in col_names
                      ]
                      for entry in self
                    ]

        return self.__class__(json.dumps([dict(entry) for entry in sub_table]))

    def kwfilter(self, kwargs):
        sub_table = \
            [ self[i]
              for i, filter_entry in enumerate(self.get_subtable(kwargs.keys()))
              if all([ fnmatch(str(filter_entry[key]), kwargs[key])
                       for key in filter_entry.keys()
                    ])
            ]
       
        return self.__class__(json.dumps(sub_table))

    def vfilter(self, fvals):
        return self.__class__(
                        json.dumps([ entry
                                     for entry in self
                                     if all([ fval in entry.values()
                                              for fval in fvals
                                           ])
                                  ])
                             )

