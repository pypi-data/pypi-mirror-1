"""
Totally incomplete for now.
"""

from uml2orm.umlparser.base import BaseParser

class XmiParser(BaseParser):
    """Handles XMI files."""
    xmi_layer = "XMI.content"
    uml_class = "Class"
    uml_association = "Association"
    
    def __init__(self, xmi_root, nstracker):
        BaseParser.__init__(self, self.uml_class, self.uml_association,
                            xmi_root, nstracker)

        self.find_uml_layer()

    def find_uml_layer(self):
        """Find where UML objects are in XMI file."""
        for child in self.root.getchildren():
            if child.tag != self.xmi_layer:
                #self.uml_layer = child
                continue

            for c in child.getchildren()[0].getchildren()[0].getchildren():
                local = self.nstracker.local_name(c.tag)
                if local == "Model":
                    if len(c.getchildren()) > 1:
                        self.uml_layer = c.getchildren()[0]
                        return

    def build_tables(self):
        """Build tables based on UML."""
        for uml_object in self.uml_layer.getchildren():
            obj_type = self.nstracker.local_name(uml_object.tag)
    
            if obj_type in self.uml_read:
                #getattr(self, self.uml_read[obj_type])(uml_object)
                self.uml_read[obj_type](uml_object)

    def _build_table_from_uml_class(self, uml_obj):
        new_table = Table()
        
        obj_id = uml_obj.attrib['xmi.id']
        new_table.tid = obj_id
        new_table.name = uml_obj.attrib['name']

        for columns in uml_obj.getchildren():
            t_columns = { } 
            for column in columns.getchildren():
                column_name = column.attrib['name']
            """
            if attr.attrib['name'] == 'name':
                new_table.name = self.get_obj_text(attr.getchildren()[0])
                continue

            elif attr.attrib['name'] != 'attributes':
                continue

            t_columns = { } # table columns, 'column name': 'data type'
            for columns in attr.getchildren():
                column_name = None
                for col in columns.getchildren():
                    if col.attrib['name'] == 'name':
                        # column name
                        column_name = self.get_obj_text(col.getchildren()[0])

                    elif col.attrib['name'] == 'type':
                        # column data type
                        data_type = self.get_obj_text(col.getchildren()[0])
                        t_columns[column_name] = data_type
            """

        #new_table.columns.update(t_columns)
        self.tables[obj_id] = new_table

    def _read_uml_association(self, uml_obj): 
        pass