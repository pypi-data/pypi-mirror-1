"""
A script that uses uml2orm for performing code generation.
"""

import sys
import uml2orm
from optparse import OptionParser

def exit_err(msg, parser):
    sys.stderr.write("%s\n" % msg)
    parser.print_help()
    sys.exit(1)

def separator(output=sys.stdout):
    output.write("%s\n" % ('*' * 40))

def write_output(content, psep=True, output=sys.stdout):
    """Write content to output."""
    for out in content:
        if not out:
            continue

        output.write("%s\n" % out)

    if psep:
        separator(output)

def gen_code(finput, sql, orm, wstdout, sql_output, orm_output):
    """Generate code and save output based on parameters."""
    db_obj, sqlgen, ormgen = uml2orm.construct_database(finput, sql, orm)
    defname = db_obj.name

    # decide file names for saving output
    if sql_output == -1 and orm_output == -1: # use default files for output
        rightdot = defname.rfind('.')
        if rightdot != -1:
            defname = defname[:rightdot]

        if sql:
            sql_out = "%s_%s.sql" % (defname, sql)
            sql_dout = "%s_%s-drops.sql" % (defname, sql)
            
        if orm:
            orm_out = "%s_%s.py" % (defname, orm)
            
    else:
        if sql_output:
            sql_out = "%s.sql" % sql_output
            sql_dout = "%s-drops.sql" % sql_output
        orm_out = orm_output
        
    # stdout output
    if wstdout:
        write_output(["Database '%s'" % db_obj.name])
  
    if sql:
        # sql return (indexes):
        #   0 = tables code, 1 = triggers code, 2 = indexes code, 
        #   3 = tables drop code, 4 = triggers drop code, 5 = indexes drop code
        if wstdout:
            write_output(sqlgen)
            
        if sql_output:
            sout = open(sql_out, 'w')
            write_output(sqlgen[:3], False, sout)
            sout.close()
            write_output(["Created file '%s'" % sql_out], False)
            sout = open(sql_dout, 'w')
            write_output(sqlgen[3:], False, sout)
            sout.close()
            write_output(["Created file '%s'" % sql_dout], False)    

    if orm:
        # orm return (indexes):
        #   0 = extra imports needed bases on orm code, 1 = orm import,
        #   2 = orm code
        if wstdout:
            write_output(ormgen, False)
            
        if orm_output:
            oout = open(orm_out, 'w')
            write_output(ormgen, False, oout)
            oout.close()
            write_output(["Created file '%s'" % orm_out], False)        

def main(args):
    usage = ("Usage: %prog [OPTIONS] INPUT\n"
             "Generates code according to OPTIONS and INPUT")
    epilog = "Report bugs to <ggpolo@gmail.com>."
    
    parser = OptionParser(usage=usage, epilog=epilog)
    parser.add_option('-m', '--orm', dest='orm', metavar='ORM',
                      help="Generate code for ORM. "
                           "Available ORM: storm")
    parser.add_option('-s', '--sql', dest='sql', metavar='SQL',
                      help="Generate code for SQL. "
                           "Available SQL: sqlite")
    parser.add_option('--orm-output', dest='orm_out', metavar='FILE',
                      help="Save ORM output to FILE.")
    parser.add_option('--sql-output', dest='sql_out', metavar='BASENAME',
                      help="Define BASENAME for saving SQL output. "
                           "It will be saved to files BASENAME.sql and "
                           "BASENAME-drops.sql")
    parser.add_option('-o', '--default-file-output', dest='default_out',
                      action="store_true",
                      help="Save SQL output and ORM output to default files. "
                           "Default file is databasename_SQL.sql and "
                           "databasename_SQL-drops.sql for SQL and "
                           "databasename_ORM.py for ORM.")
    parser.add_option('--stdout', dest='std_out', action="store_true",
                      default=False, 
                      help="Outputs generated code to stdout. This will be "
                           "the output in case no option for saving the "
                           "output is passed.")

    options, finput = parser.parse_args(args[1:])
    
    if not finput:
        exit_err("%s: Missing INPUT" % args[0], parser)

    if not options.sql and not options.orm:
        exit_err("%s: No code generation selected" % args[0], parser)

    if not options.std_out and (not options.orm_out and \
        not options.sql_out and not options.default_out):
        # no option for saving the output, show it at stdout
        options.std_out = True

    if (options.orm_out or options.sql_out) and (options.default_out):
        exit_err("%s: Conflicting options for saving output" % args[0], parser)
        
    elif options.default_out:
        options.sql_out = -1
        options.orm_out = -1
        
    gen_code(finput[0], options.sql, options.orm, options.std_out,
             options.sql_out, options.orm_out)


if __name__ == "__main__":
    main(sys.argv)
