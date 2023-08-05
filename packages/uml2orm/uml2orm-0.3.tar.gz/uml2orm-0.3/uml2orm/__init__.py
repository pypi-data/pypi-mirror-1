from uml2orm.umlparser import UMLParser
from uml2orm.codegen import create_db_objs

# only sqlite sql construction is supported for now
from uml2orm.codegen.sql.sqlite import SqliteConstructor
# only storm orm construction is supported for now
from uml2orm.codegen.orm.storm import StormConstructor

__version__ = "0.3"

def construct_database(uml_file):
    """Constructs SQL code and ORM code based on an UML description."""
    umlparser = UMLParser(uml_file)
    umlparser.parse_uml()
    
    database_obj = create_db_objs(umlparser.dbname, umlparser.tables)

    sql = SqliteConstructor(database_obj)
    sql = sql.create_sql()
    
    orm = StormConstructor(database_obj)
    orm = orm.create_orm()
    
    return database_obj, sql, orm
