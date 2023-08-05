"""
No validation is being done yet.
"""

from uml2orm.umlparser.base import BaseParser

class XmiParser(BaseParser):
    """Handles XMI files."""
    xmi_layer = "XMI.content"
    uml_class = "Class"
    uml_association = "Association"
    uml_inheritance = "Generalization"
    
    def __init__(self, xmi_root, nstracker):
        BaseParser.__init__(self, self.uml_class, self.uml_inheritance, 
                            self.uml_association, xmi_root, nstracker)

        self.tables = { }
        self.datatype = { }
        self.generalizable = { }
        self.generalization = { }
        self.association = { }
        self.dbname = None
        self.find_uml_layer()

    def find_uml_layer(self):
        """Find where UML objects are in XMI file."""
        for child in self.root.getchildren():
            if child.tag != self.xmi_layer:
                continue

            for c in child.getchildren()[0].getchildren()[0].getchildren():
                local = self.nstracker.local_name(c.tag)
                if local == "Model":
                    for _c in c.getchildren():
                        l = self.nstracker.local_name(_c.tag)
                        if l == "Namespace.ownedElement":
                            self.uml_layer = _c
                            return

    def parse_uml(self):
        """Build a database based on UML description."""
        for uml_object in self.uml_layer.getchildren():
            obj_type = self.nstracker.local_name(uml_object.tag)

            if obj_type == 'Package':
                self.parse_datatypes(uml_object)
                continue
    
            if obj_type in self.uml_read:
                ret = self.uml_read[obj_type](uml_object)
                
                if ret:
                    # found database name
                    self.dbname = ret
        
        self.adapt_data()

    def parse_table_from_uml_class(self, uml_obj):
        """Parse table attributes and operations."""
        
        def parse_operation(op_obj):
            op_name = op_obj.attrib['name']
            op_stereotype = op_obj.attrib['stereotype'].lower()
            
            if op_obj.attrib['stereotype'] == 'index':
                op_name = op_name.split(',')
            else:
                op_name = op_name.split()
                
            for oname in op_name:
                if op_obj.getchildren():
                    # BehavioralFeature.parameter -> Parameter (attrib['type'])
                    op_tp = op_obj.getchildren()[0].getchildren()[0].attrib['type']
                else:
                    op_tp = ''
                    
                yield oname.strip(), (op_stereotype, op_tp)
        
        
        name, obj_id = uml_obj.attrib['name'], uml_obj.attrib['xmi.id']
        
        if 'stereotype' in uml_obj.attrib:
            if uml_obj.attrib['stereotype'].lower() == 'database':
                return name
            
            elif uml_obj.attrib['stereotype'].lower() == 'none':
                is_table = False
        else:
            is_table = True
        
        if not uml_obj.getchildren():
            # this doesn't represent a future database table, it
            # actually is a "special" datatype created by user.
            self.datatype[obj_id] = name
            return
        
        new_table = {'columns': {}, 'operations': {}, 'references': {},
                     'inherits': [], 'indexes': [], 'table': is_table, 
                     'name': name}
        
        cindx = 0 # column index, used to keep the order when generating code
        for child in uml_obj.getchildren():
            chtag = self.nstracker.local_name(child.tag)
            if chtag not in ["Classifier.feature", 
                             "GeneralizableElement.generalization"]:
                continue
            
            for c in child.getchildren():
                ctag = self.nstracker.local_name(c.tag).lower()
                
                if ctag == 'attribute': # column
                    if 'initialValue' in c.attrib:
                        initval = c.attrib['initialValue']
                    else:
                        initval = ''
                    new_table['columns'][c.attrib['name']] = (c.attrib['type'],
                                                              initval, cindx)
                    
                    cindx += 1
                    
                elif ctag == 'operation':
                    for name, op_data in parse_operation(c):
                        new_table['operations'].setdefault(name, 
                                                           []).append(op_data)
                    
                elif ctag == 'generalization':
                    self.generalizable.setdefault(obj_id, 
                                            []).append(c.attrib['xmi.idref'])
        
        self.tables[obj_id] = new_table

    def parse_table_association(self, uml_obj):
        ta_id = uml_obj.attrib['xmi.id']
        new_assoc = []
        for end in uml_obj.getchildren()[0].getchildren():
            #new_assoc.append((end.attrib['xmi.id'], end.attrib['name'],
            #                  end.attrib['type']))
            new_assoc.append((end.attrib['name'], end.attrib['type']))
        self.association[ta_id] = new_assoc
    
    def parse_table_inheritance(self, uml_obj):
        self.generalization[uml_obj.attrib['xmi.id']] = (
            uml_obj.attrib['child'], uml_obj.attrib['parent'])
    
    def parse_datatypes(self, uml_obj):
        # uml_obj.getchildren()[0] should be a Namespace.OwnedElement, but
        # i am not sure this always happens.
        for dtype in uml_obj.getchildren()[0].getchildren():
            if dtype.attrib['stereotype'] == 'datatype':
                self.datatype[dtype.attrib['xmi.id']] = dtype.attrib['name']
                
    def adapt_data(self):
        """Adapt collected data to be usable for code generators."""
        
        # adapt tables inheritances
        for tid, data in self.generalizable.iteritems():
            for inherit in data:
                generalization = self.generalization[inherit]
                if tid not in generalization:
                    # RunetimeError is not correct here, but I will leave it
                    # for now (hopefully before a commit).
                    raise RuntimeError("Weird generalization error!")
                
                if generalization[0] == tid:
                    to_inherit = generalization[1]
                else:
                    to_inherit = generalization[0]
                
                self.tables[tid]['inherits'].append(to_inherit)

        for tid, table in self.tables.iteritems():
            # adapt table columns
            for col_name, col_data in table['columns'].iteritems():
                self.tables[tid]['columns'][col_name] = (
                    self.datatype[col_data[0]], col_data[1], col_data[2])
                
            # adapt table operations
            for op_name, op_data, in table['operations'].iteritems():
                for indx, od in enumerate(op_data):
                    if od[1]: # operation type
                        o_type = self.datatype[od[1]]
                    else:
                        o_type = ''
                    
                    self.tables[tid]['operations'][op_name][indx] = (od[0], 
                                                                     o_type)
                    
        # adapt tables associations
        for _, assoc in self.association.iteritems():
            tables, roles, conns = [], [], []
            for table_assoc in assoc:
                roles.append(table_assoc[0])
                conns.append(table_assoc[1])
                tables.append(self.tables[table_assoc[1]])
                
            for oper in tables[0]['operations'][roles[0]]:
                if oper[0] == 'fk':
                    tables[0]['references'][roles[0]] = (conns[1], roles[1])
                    break
            else:
                tables[1]['references'][roles[1]] = (conns[0], roles[0])