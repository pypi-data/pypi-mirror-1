from uml2orm.umlparser.base import BadOperation

class Database(object):
    """Representation of a database."""
    
    def __init__(self, name, tables=None):#, indexes=None):
        self.name = name
        self.tables = tables


class Table(object):
    """Representation of a Database table."""
    
    def __init__(self, tid, name, table, columns=None, references=None, 
                 inherits=None, indexes=None, *args, **kwargs):
        self.table = table # this is false when an UML class is inherited only
        self.tid = tid # table id
        self.name = name # table name
        self.columns = columns # a list of Column instances
        self.references = references # column references (foreign keys)
        self.inherits = inherits # table inheritance
        self.indexes = indexes # columns indexes


class Column(object):
    """Representation of a Table column."""

    def __init__(self, name, dtype, defval, operation=None):
        self.name = name
        self.dtype = dtype # data type
        self.defval = defval # default value
        self.operation = operation


class Index(object):
    """Representation of an Index in a table column."""
    
    def __init__(self, name, table, column):
        self.name = name
        self.table = table
        self.column = column


def create_db_objs(dbname, tables_dict):
    """
    Create Database objects based on the tables dict that were built at an
    UML Reader. No error checking is done here, it is supposed that the
    uml parser that generated tables_dict did all the necessary checkings
    already.
    """
    tables = { }

    for tid, table in tables_dict.items():
        new_table = table
        new_table.update({'tid': tid})
        tcolumns = new_table.pop('columns')
        operations = new_table.pop('operations')
        new_table['columns'] = [0] * len(tcolumns)

        # create Columns and Index objects for current table
        for column, data in tcolumns.items():
            dtype, defval, index = data
            
            if column not in operations:
                new_table['columns'][index] = Column(column, dtype, 
                                                     defval, None)
                continue
            
            opers = operations.pop(column)
            if len(opers) == 1 and opers[0][0] == 'index':
                new_table['indexes'].append(column)
                new_table['columns'][index] = Column(column, dtype, 
                                                     defval, None)
                continue
                
            for op_name, op_type in opers:
                if op_name == "index":
                    new_table['indexes'].append(column)
                    continue
                
                new_table['columns'][index] = Column(column, dtype, defval,
                                                     (op_name, op_type))

        if operations:
            # some invalid operation was created, since it didn't match any
            # attribute in current uml class
            raise BadOperation(("The following operations: '%s' couldn't be "
                                "found at UML Class '%s'"
                                "." % ("', '".join(operations.keys()),
                                       new_table['name'])))

        tables[tid] = Table(**new_table)
    
    return Database(dbname, tables)