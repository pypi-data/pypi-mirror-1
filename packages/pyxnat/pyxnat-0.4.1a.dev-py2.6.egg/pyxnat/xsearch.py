import os
import hashlib
import tempfile

from lxml import etree

search_nsmap = { 'xdat':'http://nrg.wustl.edu/security',
                 'xsi':'http://www.w3.org/2001/XMLSchema-instance' }

def build_search_document(root_element_name, columns, criteria_set):
    root_node = \
        etree.Element( etree.QName(search_nsmap['xdat'], 'search'),
                       nsmap=search_nsmap
                     )

    root_node.set('ID', "")
    root_node.set('allow-diff-columns', "0")
    root_node.set('secure', "false")

    root_element_name_node = \
        etree.Element( etree.QName(search_nsmap['xdat'], 'root_element_name'),
                       nsmap=search_nsmap
                     )

    root_element_name_node.text = root_element_name

    root_node.append(root_element_name_node)

    for i, column in enumerate(columns):
        element_name, field_ID = column.split('/')

        search_field_node = \
            etree.Element( etree.QName(search_nsmap['xdat'], 'search_field'), 
                           nsmap=search_nsmap
                         )

        element_name_node = \
            etree.Element( etree.QName(search_nsmap['xdat'], 'element_name'), 
                           nsmap=search_nsmap
                         )

        element_name_node.text = element_name

        field_ID_node = \
            etree.Element( etree.QName(search_nsmap['xdat'], 'field_ID'), 
                           nsmap=search_nsmap
                         )

        field_ID_node.text = field_ID

        sequence_node = \
            etree.Element( etree.QName(search_nsmap['xdat'], 'sequence'), 
                           nsmap=search_nsmap
                         )

        sequence_node.text = str(i)

        type_node = \
            etree.Element( etree.QName(search_nsmap['xdat'], 'type'), 
                           nsmap=search_nsmap
                         )

        type_node.text = 'string'

        header_node = \
            etree.Element( etree.QName(search_nsmap['xdat'], 'header'), 
                           nsmap=search_nsmap
                         )

        header_node.text = column

        search_field_node.extend([ element_name_node,
                                   field_ID_node,
                                   sequence_node,
                                   type_node, header_node
                                ])

        root_node.append(search_field_node)

    search_where_node = \
        etree.Element( etree.QName(search_nsmap['xdat'], 'search_where'), 
                       nsmap=search_nsmap
                     )

    root_node.append(build_criteria_set(search_where_node, criteria_set))

    xml_path = \
        os.path.join( tempfile.gettempdir(),
                      hashlib.md5(etree.tostring(root_node)).hexdigest() + \
                                                                        '.xml'
                    )

    root_node.getroottree().write(xml_path)

    return xml_path

def build_criteria_set(container_node, criteria_set):

    for criteria in criteria_set:
        if isinstance(criteria, (str, unicode)):
            container_node.set('method', criteria)

        if isinstance(criteria, (list)):
            sub_container_node = \
                etree.Element( etree.QName(search_nsmap['xdat'], 'child_set'),
                               nsmap=search_nsmap
                             )

            container_node.append(
                build_criteria_set(sub_container_node, criteria))

        if isinstance(criteria, (tuple)):
            constraint_node = \
                etree.Element( etree.QName(search_nsmap['xdat'], 'criteria'), 
                               nsmap=search_nsmap
                             )

            constraint_node.set('override_value_formatting', '0')

            schema_field_node = \
                etree.Element( etree.QName( search_nsmap['xdat'],
                                             'schema_field'
                                          ), 
                               nsmap=search_nsmap
                             )

            schema_field_node.text = criteria[0]

            comparison_type_node = \
                etree.Element( etree.QName( search_nsmap['xdat'],
                                            'comparison_type'
                                          ), 
                               nsmap=search_nsmap
                             )

            comparison_type_node.text = criteria[1]

            value_node = \
                etree.Element( etree.QName(search_nsmap['xdat'], 'value'),
                               nsmap=search_nsmap
                             )

            value_node.text = criteria[2]

            constraint_node.extend([
                        schema_field_node, comparison_type_node, value_node])

            container_node.append(constraint_node)

    return container_node


