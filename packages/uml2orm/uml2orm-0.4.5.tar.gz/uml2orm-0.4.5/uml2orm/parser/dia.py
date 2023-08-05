# Copyright (c) 2007, Guilherme Polo.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, 
#      this list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright 
#      notice, this list of conditions and the following disclaimer in the 
#      documentation and/or other materials provided with the distribution.
#
#   3. The name of the author may not be used to endorse or promote products 
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER 
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Maybe all this huge amount of error checking should be placed somewhere else
since all the parsers will need to do this same thing.
"""

import warnings
from uml2orm.consts import DEFAULT_DB_NAME
from uml2orm.parser.base import BaseParser
from uml2orm.parser.base import (BadUML, BadReference, 
                                    IncompleteReference, ReferenceDuplicate,
                                    CyclicReference)
from uml2orm.parser.base import NoColumnType, DisconnectedObject

class DiaParser(BaseParser):
    """Handles DIA files."""
    dia_layer = "layer"
    uml_class = "UML - Class"
    uml_inheritance = "UML - Generalization"
    uml_association = "UML - Association"

    def __init__(self, dia_root, nstracker):
        BaseParser.__init__(self, self.uml_class, self.uml_inheritance,
                            self.uml_association, dia_root, nstracker)

        self.tables = { }
        self.dbname = None
        self.find_uml_layer()


    def get_obj_text(self, dia_str_object):
        """Removes '#' from string object and return the new string."""
        return dia_str_object.text[1:-1]  
    
    
    def find_uml_layer(self):
        """Find where UML objects are in DIA file."""
        for child in self.root.getchildren():
            local = self.nstracker.local_name(child.tag)

            if local == self.dia_layer:
                self.uml_layer = child
                break      


    def parse_document(self):
        """Build a database based on UML description."""
        inheritance_obj = []
        reference_obj = []

        # First we will parse the tables and store other objects we
        # will need later
        for uml_object in self.uml_layer.getchildren():
            obj_type = uml_object.attrib['type']
    
            if obj_type in self.uml_read:
                if obj_type == self.uml_class:
                    # UML Class (Tables in database)
                    ret = self.uml_read[obj_type](uml_object)

                    if ret:
                        # found database name
                        self.dbname = ret

                elif obj_type == self.uml_inheritance:
                    # UML Generalization (Inheritance)
                    inheritance_obj.append(uml_object)

                else:
                    # UML Association (Table reference)
                    reference_obj.append(uml_object)
        
        # Parse inheritances now
        for inherit in inheritance_obj:
            self.uml_read[self.uml_inheritance](inherit)

        # And finally, parse references
        for ref in reference_obj:
            self.uml_read[self.uml_association](ref)

        # Check for database name
        if self.dbname is None:
            # no UML Class defined as Database, so lets set the default
            # name to it.
            self.dbname = DEFAULT_DB_NAME
            

    def parse_table_from_uml_class(self, uml_obj):
        """Parse table attributes and operations."""

        def parse_table_attributes(table_attrs):
            """Parse UML Class attributes doing proper error checking."""
            errors = [ ]
            # table columns, 'column name': ('data type', 'default value')
            t_columns = { }
            for indx, columns in enumerate(table_attrs):
                t_col = { }

                for col in columns.getchildren():
                    col_n = col.attrib['name']

                    if col_n in ['name', 'type', 'value']:
                        t_col[col_n] = self.get_obj_text(col.getchildren()[0])

                if not t_col['name']: # obrigatory field not filled
                    return None, 1

                elif t_col['name'] in t_columns:  # column duplicated
                    return t_col['name'], 2

                elif not t_col['type']: 
                    # no type especified, a warning will be raised
                    errors.append(t_col['name'])
                    
                t_columns[t_col['name']] = (t_col['type'], t_col['value'], indx)

            return t_columns, errors

        def parse_table_operations(table_operations):
            """Parse UML Class operations doing proper error checking."""
            t_operations = { }

            for ops in table_operations:
                t_op = { }

                for op in ops.getchildren():
                    op_attr = op.attrib['name']
           
                    if op_attr in ['name', 'type', 'stereotype']:
                        t_op[op_attr] = self.get_obj_text(op.getchildren()[0])

                if not t_op['name'] or not t_op['stereotype']:
                    # both fields are obrigatory
                    return None, 1
              
                if t_op['stereotype'] == 'index':
                    t_op['name'] = t_op['name'].split(',')
                else:
                    t_op['name'] = t_op['name'].split()
                 
                for op_name in t_op['name']:
                    op_name = op_name.strip()
                    
                    if op_name in t_operations:
                        for oper in t_operations[op_name]:
                            if oper[0] == t_op['stereotype'].lower():
                                # found a duplicated operation
                                #return (t_op['stereotype'], t_op['name']), 2
                                return (t_op['stereotype'], op_name), 2
                    
                    t_operations.setdefault(op_name, []).append(
                            (t_op['stereotype'].lower(), t_op['type'].lower()))
           
            return t_operations, 0

        # table skeleton
        new_table = {'columns': None, 'operations': None, 'references': {},
                     'inherits': [], 'indexes': [], 'table': True, 
                     'name': None}
        obj_id = uml_obj.attrib['id']
    
        for attr in uml_obj.getchildren():
            attr_name = attr.attrib['name']

            if attr_name == 'name':
                # Found name for this UML class
                new_table['name'] = self.get_obj_text(attr.getchildren()[0])
           
            # Check if we are dealing with a real database Table
            elif attr_name == 'stereotype':
                stereotype = self.get_obj_text(attr.getchildren()[0]).lower()

                if stereotype == 'database':
                    # This is an UML class that defines a database, not
                    # a table actually.
                    return new_table['name'] # database name

                elif stereotype == 'none':
                    # This UML class will not generate SQL code, it is
                    # just being subclassed by some other table. This is
                    # used only to construct ORM code.
                    new_table['table'] = False

            elif attr_name == 'attributes':
                t_columns, ret = parse_table_attributes(attr.getchildren())
                if ret == 1:
                    raise BadUML(("No name defined for a column at UML Class "
                                  "'%s'." % new_table['name']))
                elif ret == 2:
                    raise BadUML(("Found a duplicated column ('%s') at UML "
                                  "Class "
                                  "'%s'." % (t_columns, new_table['name'])))
                elif ret:
                    for err_col in ret:
                        warnings.warn(("Column '%s' at UML Class '%s' has no "
                                       "type defined, assuming "
                                       "TEXT." % (err_col, new_table['name'])),
                                       NoColumnType)

            elif attr_name == 'operations':
                t_operations, ret = parse_table_operations(attr.getchildren())
                if ret == 1:
                    raise BadUML(("An operation at UML Class '%s' is missing "
                                  "both or one of the following data: "
                                  "name, stereotype." % new_table['name']))
                elif ret == 2:
                    raise BadUML(("Found a duplicated operation %s at UML "
                                  "Class "
                                  "'%s'." % (t_operations, new_table['name'])))

        new_table['columns'] = t_columns
        new_table['operations'] = t_operations 
        self.tables[obj_id] = new_table
    

    def parse_table_inheritance(self, uml_obj):
        """Find and set tables subclasses."""
        for attr in uml_obj.getchildren():
            if self.nstracker.local_name(attr.tag) == "connections":
                inherit_from, inheriter = None, None

                for inherit in attr.getchildren():
                    if inherit.attrib['handle'] == '0':
                        inherit_from = inherit.attrib['to']
                    else:
                        inheriter = inherit.attrib['to']

                conn = None
                if inherit_from is None and inheriter is None:
                    warnings.warn(("Both end points of an UML Generalization "
                                   "are disconnected, discarding it."),
                                  DisconnectedObject)
                    return
                elif inherit_from is None:
                    conn = self.tables[inheriter]['name']
                elif inheriter is None:
                    conn = self.tables[inherit_from]['name']

                if conn:
                    raise BadUML(("An UML Generalization object is connected "
                                  "to '%s' but the other end point is "
                                  "disconnected." % conn))
                    
                self.tables[inheriter]['inherits'].append(inherit_from)


    def parse_table_association(self, uml_obj):
        """Find and set table association based on uml_obj."""
        for attr in uml_obj.getchildren():
            # connections
            if self.nstracker.local_name(attr.tag) == "connections":
                conns = [c.attrib['to'] for c in attr.getchildren()]
                continue

            if attr.attrib['name'] != 'ends':
                continue

            # ends
            roles = [self.get_obj_text(end.getchildren()[0]) 
                     for ends in attr.getchildren() 
                        for end in ends.getchildren() 
                            if end.attrib['name'] == 'role']

        # Check for badly connected references.
        if not len(conns):
            warnings.warn(("Both end points of an UML Reference with roles: "
                           "'%s' are disconnected, discarding "
                           "it. " % ' and '.join(roles)), 
                           DisconnectedObject)
            return

        elif len(conns) == 1:
            raise IncompleteReference(self.tables[conns[0]]['name'])
        
        tables = (self.tables[conns[0]], self.tables[conns[1]])

        # Check for inexistent references
        if not roles[0] in tables[0]['operations']:
            raise BadReference(tables[0]['name'], roles[0])

        if not roles[1] in tables[1]['operations']:
            raise BadReference(tables[1]['name'], roles[1])
        
        # Check for duplicated references
        if roles[0] in tables[0]['references']:
            raise ReferenceDuplicate(tables[0]['name'], roles[0])
        if roles[1] in tables[1]['references']:
            raise ReferenceDuplicate(tables[1]['name'], roles[1])

        # Check for cyclic reference
        if conns[0] == conns[1]:
            raise CyclicReference(tables[0]['name'], roles[0])
      
        # Passed all the tests, it is ok to store the reference now
        # The following for loop and if condition are used to "detect"
        # what UML Class is being referenced and which one is referencing
        for oper in tables[0]['operations'][roles[0]]:
            if oper[0] == 'fk':
                tables[0]['references'][roles[0]] = (conns[1], roles[1])
                return

        # If no 'fk' operation was found at tables[0] it means tables[1]
        # is the one referencing and table[0] is referenced.
        tables[1]['references'][roles[1]] = (conns[0], roles[0])
