
resources_types = [ 'projects', 'subjects', 'experiments', 
                   'scans', 'reconstructions', 'assessors',
                   'resources', 'files'
                 ]

def get_id(uri):
    if not uri.split('/')[-1] in resources_types:
        return uri.split('/')[-1].strip('"')
    
def strip_id(uri):
    if not uri.split('/')[-1] in resources_types:
        return '/'.join(uri.split('/')[:-1]).strip('"')
    return uri

def join(uri, *parts):
    return '/'.join( uri.rstrip('/').split('/') + \
                     [ part.lstrip('/') 
                       for part in parts
                     ]
                   )

def strip_qr(uri):
    return uri.split('?')[0].strip('"')

def parent(uri):
    return '/'.join(strip_id(uri).split('/')[:-1])
    
def level(uri):
    return strip_id(strip_qr(uri)).split('/')[-1]

def is_resource(uri):
    return uri != strip_id(strip_qr(uri))

def is_query(uri):
    return uri == strip_id(strip_qr(uri))

def as_items(uri):
    if is_query(uri):
        uri += '/'
    return zip(uri.split('/')[2::2], uri.split('/')[3::2])

def as_dict(uri):
    return dict(as_items(uri))

def is_related(uri, other_uri):
    uri1 = strip_qr(uri)
    uri2 = strip_qr(other_uri)

    items_uri1 = as_items(uri1)
    items_uri2 = as_items(uri2)

    if uri1 in uri2:
        return True

    if level(uri1) == 'files':
        el1_items = [ item 
                      for item in items_uri1
                      if item[0] not in ['resources', 'files']
                    ]

        el2_items = [ item 
                      for item in items_uri2
                      if item[0] not in ['resources', 'files']
                    ]

        return el1_items == el2_items

    if level(uri1) == level(uri2):
        return parent(uri1) == parent(uri2) 

