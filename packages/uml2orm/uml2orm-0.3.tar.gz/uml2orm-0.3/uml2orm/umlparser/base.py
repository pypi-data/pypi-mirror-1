class BadUML(Exception):
    """Raised in case UML design is incorrect."""

class BadReference(BadUML):
    """
    Raised in case UML object Reference references non-existant operation 
    in other UML Class.
    """
    def __init__(self, tname, oper):
        self.tname = tname
        self.oper = oper

    def __str__(self):
        return ("UML Class '%s' has no operation '%s' to use as reference. " 
                "You must define valid roles for both end "
                "points." % (self.tname, self.oper))

class BadOperation(BadUML):
    """Raised when a operation is placed at a wrong place."""

class IncompleteReference(BadUML):
    """
    Raised in case UML object Reference is not connected to both end points.
    """
    def __init__(self, connected):
        self.connected = connected

    def __str__(self):
        return ("One end point of an UML Reference is disconnected, "
                "and the other end is connected to the UML Class "
                "'%s'." % self.connected)

class ReferenceDuplicate(BadUML):
    """Raised when finding the same reference between same UML Class."""
    def __init__(self, dtable, dcolumn):
        self.dtable = dtable
        self.dcolumn = dcolumn

    def __str__(self):
        return ("Found a reference duplicate at UML Class '%s' involving "
                "attribute '%s'." % (self.dtable, self.dcolumn))

class CyclicReference(BadUML):
    """Raise when finding a cyclic reference in an UML Class."""
    def __init__(self, ctable, ccolumn):
        self.ctable = ctable
        self.ccolumn = ccolumn

    def __str__(self):
        return ("Found a cyclic reference at UML Class '%s' involving "
                "attribute '%s'." % (self.ctable, self.ccolumn))

class NoColumnType(Warning):
    """Raise when a attribute has no type defined."""

class DisconnectedObject(Warning):
    """Raised when both end points of an UML object are disconnected."""

class BaseParser(object):
    """
    UML parsers should inherit from this class and override methods 
    not implemented.
    """

    def __init__(self, uml_class, uml_inheritance, uml_association, 
                 uml_root, nstracker):
        self.dbname = None
        self.uml_layer = None

        self.root = uml_root
        self.nstracker = nstracker
        self.uml_read = {uml_class: self.parse_table_from_uml_class,
                         uml_inheritance: self.parse_table_inheritance,
                         uml_association: self.parse_table_association}

    def parse_uml(self, *args, **kwargs):
        raise NotImplementedError
    
    def parse_table_from_uml_class(self, *args, **kwargs):
        raise NotImplementedError

    def parse_table_inheritance(self, *args, **kwargs):
        raise NotImplementedError

    def parse_table_association(self, *args, **kwargs):
        raise NotImplementedError
