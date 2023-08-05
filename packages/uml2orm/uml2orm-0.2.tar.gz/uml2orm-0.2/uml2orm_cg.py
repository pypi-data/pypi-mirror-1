"""
A script that uses uml2orm for performing code generation.
"""

import sys
import uml2orm

def separator():
    print '*' * 40

if __name__ == "__main__":
    file_input = None
    if len(sys.argv) < 2:
        file_input = raw_input("Especify a filename please: ")
    else:
        file_input = sys.argv[1]

    db_obj, sql, orm = uml2orm.construct_database(file_input)

    print "Database '%s'" % db_obj.name
    separator()
  
    # sql return (indexes):
    #   0 = tables code, 1 = triggers code, 2 = indexes code, 
    #   3 = tables drop code, 4 = triggers drop code, 5 = indexes drop code
    for sql_output in sql:
        if not sql_output:
            continue
        
        print sql_output
    separator()

    # orm return (indexes):
    #   0 = extra imports needed bases on orm code, 1 = orm import,
    #   2 = orm code
    for i, orm_output in enumerate(orm):
        if not orm_output:
            continue

        if i == 2:
            print
        print orm_output
