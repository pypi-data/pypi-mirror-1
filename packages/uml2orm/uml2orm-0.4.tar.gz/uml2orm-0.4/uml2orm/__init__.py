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

from uml2orm.umlparser import UMLParser
from uml2orm.codegen import create_db_objs

__version__ = "0.4"

def construct_database(uml_file, sql, orm):
    """Constructs SQL code and ORM code based on an UML description."""
    umlparser = UMLParser(uml_file)
    umlparser.parse_uml()
    
    database_obj = create_db_objs(umlparser.dbname, umlparser.tables)
    sql_res = ()
    orm_res = ()

    if sql:
        sql_builder = __import__("uml2orm.codegen.sql.%s" % sql, fromlist=['1'])
        sql = getattr(sql_builder, '%sConstructor' % sql.title())(database_obj)
        sql_res = sql.create_sql()
    
    if orm:
        orm_builder = __import__("uml2orm.codegen.orm.%s" % orm, fromlist=['1'])
        orm = getattr(orm_builder, '%sConstructor' % orm.title())(database_obj)
        orm_res = orm.create_orm()
    
    return database_obj, sql_res, orm_res
