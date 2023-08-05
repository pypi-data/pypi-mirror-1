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
Generates sqlite SQL code based on database objects passed in.
"""

SQL_MAPPING = {'varchar': 'TEXT', 'str': 'TEXT', 'string': 'TEXT',
               'int': 'INTEGER',
               'date': 'TIMESTAMP', 'datetime': 'TIMESTAMP',
               'notnull': 'NOT NULL',
               'pk': 'INTEGER%(null)s PRIMARY KEY',
               'fk': ("INTEGER%(null)s CONSTRAINT %(fk_column)s\n"
               "              REFERENCES %(table)s(%(column)s) %(cascade)s"),
               'cascade': "ON DELETE CASCADE"}

# DELETE trigger templates
TMPL_DEL_TRIGGER_TITLE = "%(refdtable)s_%(kind)s_delete"
TMPL_DEL_TRIGGER_BASE = """CREATE TRIGGER %(title)s
    BEFORE DELETE ON %(reftable)s
    FOR EACH ROW BEGIN
        %(del_oper)s
    END;"""
TMPL_DEL_TRIGGER = """SELECT RAISE(ROLLBACK, "Bad DELETE on table '%(reftable)s', it still holds references.")
        WHERE (SELECT %(column)s FROM %(table)s 
               WHERE %(column)s = OLD.%(refcolumn)s) IS NOT NULL;"""
TMPL_DEL_TRIGGER_CASCADE = """DELETE FROM %(table)s WHERE %(table)s.%(column)s = OLD.%(refcolumn)s;"""

# INSERT/UPDATE trigger templates
TMPL_IU_TRIGGER_TITLE = "%(table)s_%(lower_op)s_bad_%(column)s"
TMPL_IU_TRIGGER = """CREATE TRIGGER %(title)s
    BEFORE %(operation)s ON %(table)s
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad %(operation)s on table '%(table)s', invalid %(column)s especified.")
        WHERE%(null)s (SELECT %(refcolumn)s FROM %(reftable)s 
                       WHERE %(refcolumn)s = NEW.%(column)s) IS NULL;
    END;"""
TMPL_IU_TRIGGER_NULL = "NEW.%s IS NOT NULL AND"

# INDEX template 
TMPL_INDEX = "CREATE%(unique)s INDEX %(index_name)s ON %(table)s(%(column)s);"

# table base structure
BASETABLE = "CREATE TABLE %(name)s (\n%(columns)s\n);"

class SqliteConstructor(object):
    """Construct complete sqlite code based on the database content."""

    def __init__(self, database):
        self.database = database
        self.dtables = self.database.tables
        self.trigger_names = [ ]
        self.trigger_prefix = { } # used to ensure uniqueness in trigger names
        self.index_names = { } # used to ensure uniqueness in index names

    def create_sql(self):
        """
        Construct complete sqlite code based on the self.database 
        content. Returns (in the following order): Tables SQL, 
        Triggers SQL, Indexes SQL, Drop tables SQL, Drop triggers SQL, 
        Drop indexes SQL.
        """
        tables = { } # table_name: {column1, column2, .., columnN}
        sql_triggers = [ ] # triggers code
        sql_indexes = [ ] # indexes code

        for table in self.dtables.values():
            if not table.table:
                # Table only inherited by others (probably), no SQL code 
                # gets produced for this.
                continue
            
            tname = table.name.lower()
            tables[tname], indexes, triggers = self._build_table(table)
            sql_indexes.extend(indexes)
            sql_triggers.extend(triggers)

        # format sql code nicely =)
        sql_tables = [ ]
        for tname, columns in tables.items():
            cols = ["%12s  %s," % (col[0], col[1]) for col in columns]
            table_dict = {"name": tname,
                          # remove last comma from table columns
                          "columns": '\n'.join(cols)[:-1]}

            sql_tables.append(BASETABLE % table_dict)
 
        sql_tables = '\n\n'.join(sql_tables)
        sql_triggers = '\n\n'.join(sql_triggers)
        sql_indexes = '\n'.join(sql_indexes)
        sql_del_tables = '\n'.join("DROP TABLE %s;" % t for t in tables.keys())
        sql_del_triggers = '\n'.join("DROP TRIGGER %s;" % t 
                                        for t in self.trigger_names)
        sql_del_indexes = '\n'.join("DROP INDEX %s;" % i 
                                        for i in self.index_names)

        return (sql_tables, sql_triggers, sql_indexes, sql_del_tables, 
                sql_del_triggers, sql_del_indexes)

    def _build_table(self, wtable, calling_from=None):
        """
        Build all the columns for wtable (working table, or current table).
        Lookups for inheritances and construct columns for them first.
        It will also construct triggers needed for this table aswell.
        """
        new_columns, new_triggers, new_indexes = [ ], [ ], [ ]
        wtable_name = wtable.name.lower() # using lowercase for table name

        # construct code from inherited tables first
        for inherit in wtable.inherits:
            columns, indexes, triggers = self._build_table(
                                            self.dtables[inherit], wtable_name)
            new_columns.extend(columns)
            new_indexes.extend(indexes)
            new_triggers.extend(triggers)

        # indexes code
        if wtable.indexes:
            index_name = self._good_name("%s_indx" % '_'.join(wtable.indexes), 
                                         self.index_names)
            new_indexes.append(TMPL_INDEX % {
                'index_name': index_name,
                'table': calling_from if not wtable.table else wtable_name,
                'column': ', '.join(wtable.indexes), 'unique': ''})#'UNIQUE' if indx.unique else ''})

        # columns code
        for column in wtable.columns:
            column_dtype = column.dtype.split()

            if column.operation and column.operation[0] in SQL_MAPPING:
                column_subs = {'null': '', 'fk_column': None, 'table': None,
                               'column': None, 'cascade': ''}
                if 'notnull' in column_dtype:
                    column_subs['null'] = ' %s' % SQL_MAPPING['notnull']

                if column.name in wtable.references:
                    # need to create triggers aswell
                    ret = self._build_triggers(wtable_name, column.name, 
                                               wtable.references[column.name],
                                               column_dtype, 
                                               column.operation[1])
                    new_triggers.extend(ret)
                
                    ref = wtable.references[column.name]
                    column_subs['fk_column'] = column.name
                    column_subs['table'] = self.dtables[ref[0]].name
                    column_subs['column'] = ref[1]
                    if column.operation[1] == 'cascade':
                        column_subs['cascade'] = SQL_MAPPING['cascade']

                newc = SQL_MAPPING[column.operation[0]] % column_subs
        
            else:
                if not column_dtype:
                    # set TEXT as a fallback
                    column_dtype.append(SQL_MAPPING['str'])

                newc = ' '.join(SQL_MAPPING[dtype] if dtype in SQL_MAPPING 
                                  else dtype.upper() for dtype in column_dtype)

            new_columns.append((column.name, newc))

        return new_columns, new_indexes, new_triggers


    def _build_triggers(self, wtname, wtcolumn, wcolumnref, column_type, 
                        extra):
        """
        Creates a DELETE trigger for the table being referenced and
        creates triggers for INSERT and UPDATE statements for the table 
        referencing, so data integrity is enforced in sqlite.
        """
        ref = wcolumnref
        tref = self.dtables[ref[0]].name # referenced table name
        tcolumn = ref[1] # referenced table column name

        ddata = {'table': wtname, 'column': wtcolumn,
                 'refcolumn': tcolumn, 'reftable': tref,
                 'refdtable': self._good_name(tref, self.trigger_prefix),
                 'operation': None, 'lower_op': None, 'null': '',
                 'kind': 'bad'}

        sql_triggers = [ ]

        # create triggers for INSERT and UPDATE
        operations = ("INSERT", "UPDATE") 
        if "notnull" not in column_type:
            ddata['null'] = ' %s' % (TMPL_IU_TRIGGER_NULL % wtcolumn)

        for oper in operations:
            ddata['operation'] = oper
            ddata['lower_op'] = ddata['operation'].lower()
            ddata['title'] = TMPL_IU_TRIGGER_TITLE % ddata

            self.trigger_names.append(ddata['title'])
            sql_triggers.append(TMPL_IU_TRIGGER % ddata)
   
        # create trigger for DELETE
        if extra == 'cascade':
            del_oper = TMPL_DEL_TRIGGER_CASCADE % ddata
            ddata['kind'] = 'cascade'
        else:
            del_oper = TMPL_DEL_TRIGGER % ddata

        ddata['del_oper'] = del_oper
        ddata['title'] = TMPL_DEL_TRIGGER_TITLE % ddata
        self.trigger_names.append(ddata['title'])
        sql_triggers.append(TMPL_DEL_TRIGGER_BASE % ddata)

        return sql_triggers


    def _good_name(self, index_name, look_at):
        """Return a unique name based on index_name and keys at look_at."""
        index_name = index_name.lower()
        
        if index_name in look_at:
            look_at[index_name] += 1
            index_name = index_name + str(look_at[index_name])
        else:
            look_at[index_name] = 0

        return index_name
