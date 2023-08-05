"""
Sample database representation.
"""

dbname = "testing"

tables = {
    'unique_id': 
        {'name': 'tableA',
         'columns': {'id': ('int', '', 0), 'date': ('timestamp', 'now', 1)},
         'operations': {'id': [('pk', '')]},
         'references': {},
         'inherits': [],
         'indexes': [],
         'table': True
        },

    'unique_id2':
        {'name': 'tableB',
         'columns': {'id': ('int', '', 0), 'id_A': ('int notnull', '', 1)},
         'operations': {'id_A': [('fk', '')], 'id': [('pk', '')]},
         'references': {'id_A': ('unique_id', 'id')},
         'inherits': [],
         'indexes': [],
         'table': True
        }
    }
