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
Storm ORM code generator.
"""

from uml2orm.codegen.orm import PYTHON_MAPPING

INDENT = " " * 4
PREFIX = "sl"
STORM_MAPPING = {"integer": "Int", "int": "Int",
                 
                 "text": "Unicode", "varchar": "Unicode", "string": "Unicode", 
                 "str": "Unicode", "char": "Unicode",
                 
                 "date": "DateTime", "datetime": "DateTime", 
                 "timestamp": "DateTime",
                  
                 "bool": "Bool",

                 "enum": "Enum"}
STORM_IMPORT = "import storm.locals as %s" % PREFIX

TMPL_CLASS_BASE = """class %(name)s(%(inheritance)s):
%(attributes)s"""
TMPL_CLASS =  TMPL_CLASS_BASE + """
   
%(indent)sdef __init__(self, %(args)s):
%(attribs_init)s"""

             
class StormConstructor(object):
    """Creates ORM code for Storm."""
    
    def __init__(self, database):
        self.database = database
        self.dtables = self.database.tables
        
    def create_orm(self):
        """Creates all ORM code."""
        # missing code generation for controlling the database, and i am
        # not sure if it is a good thing to generate this kind of code.
        
        return self.create_base_orm()
        
    def create_base_orm(self):
        """Creates ORM code that maps database tables to classes."""
        default_inheritance = '%s.Storm' % PREFIX
        classes = []
        extra_imports = []
        # classes that inherits from others must be written at end
        classes_inheritance = []
        
        for table in self.dtables.values():
            new_class = {'name': self._class_name(table.name), 
                         'inheritance': table.inherits, 'attributes': None, 
                         'indent': INDENT, 'args': None, 'attribs_init': None}

            # setup class inheritance
            inherits = []
            for inherit in new_class['inheritance']:
                inherits.append(self._class_name(self.dtables[inherit].name))
            new_class['inheritance'] = ', '.join(inherits)
            if not new_class['inheritance']:
                new_class['inheritance'] = default_inheritance
                
            # setup class attributes
            columns = []
            references = []
            for column in table.columns:
                column_dtype = column.dtype.split()
                dtype = self._mapping(column_dtype[0])
                if dtype == -1: # mapping not found
                    raise KeyError(("Mapping '%s' specified at UML Class "
                                    "'%s' is invalid" % (column_dtype[0],
                                                         table.name)))
                
                if column.operation:
                    if column.operation[0] == 'pk':
                        dtype += '(primary=True)'
                    elif column.operation[0] == 'fk':
                        dtype += '()'
                        tref = table.references[column.name]
                        references.append((column.name, PREFIX, column.name,
                                self._class_name(self.dtables[tref[0]].name), 
                                tref[1]))
                                
                else:
                    dtype += '()'
                    
                columns.append((column.name, dtype, column.defval,
                                'notnull' in column_dtype))

            # preparing for TMPL_CLASS
            attribs = []
            if table.table:
                attribs.append("%s__storm_table__ = \"%s\"" % (INDENT, 
                                                        table.name.lower()))
            args = []
            args_null = []
            attribs_init = []
            for col in columns:
                attribs.append('%s%s = %s.%s' % (INDENT, col[0], PREFIX, 
                                                 col[1]))

                # check for primary key. Dont add it to attribs_init 
                # (assumining it is auto-increment)
                if col[1][col[1].find('(') + 1:-1] == 'primary=True':
                    continue
                
                if col[2]: # default value set
                    imports, python_code = PYTHON_MAPPING[col[2].lower()]
                    if imports not in extra_imports:
                        extra_imports.append(imports)
                    
                    attribs_init.append("%sif not self.%s:" % (INDENT * 2, 
                                                               col[0]))
                    attribs_init.append("%sself.%s = %s" % (INDENT * 3, col[0],
                                                            python_code))
                    attribs_init.append("%selse:" % (INDENT * 2))
                    attribs_init.append("%sself.%s = %s" % (INDENT * 3, col[0],
                                                            col[0]))
                else:
                    attribs_init.append('%sself.%s = %s' % (INDENT * 2, col[0], 
                                                            col[0]))
                    
                if col[3]:
                    args.append(col[0])
                    
                else:
                    args_null.append("%s=None" % col[0])
            
            for ref in references:
                if ref[0].startswith("fk_"):
                    refname = ref[0][3:]
                else:
                    refname = "fk_%s" % ref[0]
                    
                attribs.append('%s%s = %s.Reference(%s, "%s.%s")' % (INDENT,
                                                       refname, ref[1], ref[2], 
                                                       ref[3], ref[4]))
            
            args.extend(args_null)
            
            new_class['attributes'] = '\n'.join(attribs)
            
            if new_class['inheritance'] != default_inheritance:
                append_to = classes_inheritance
            else:
                append_to = classes
                
            if not args:
                append_to.append(TMPL_CLASS_BASE % new_class)
            else:
                new_class['args'] = ', '.join(args)
                new_class['attribs_init'] = '\n'.join(attribs_init)
                append_to.append(TMPL_CLASS % new_class)

        extra_imports = ['import %s' % eimp for eimp in extra_imports]
        extra_imports = '\n'.join(extra_imports)
        classes.extend(classes_inheritance)
        
        return extra_imports, STORM_IMPORT, '\n\n'.join(classes)
    
    def _mapping(self, tomap):
        """Sanitize tomap and then use it at STORM_MAPPING."""
        parenthesis = tomap.find('(') 
        if parenthesis != -1: # sanitizing "some(thing)"
            tomap = tomap[:parenthesis]
        
        if tomap not in STORM_MAPPING:
            return -1
        
        return STORM_MAPPING[tomap]
    
    def _class_name(self, cname):
        """Returns an appropriate name for a class."""
        return cname.replace('_', ' ').title().replace(' ', '')