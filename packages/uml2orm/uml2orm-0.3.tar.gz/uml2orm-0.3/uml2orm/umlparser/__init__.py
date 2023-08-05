import gzip
from xml.etree.ElementTree import ElementTree, XMLTreeBuilder
from uml2orm.umlparser.dia import DiaParser
from uml2orm.umlparser.xmi import XmiParser

class NamespaceTracker(XMLTreeBuilder):
    def __init__(self):
        XMLTreeBuilder.__init__(self)

        self._parser.StartNamespaceDeclHandler = self._start_ns
        self.namespaces = { }

    def local_name(self, name):
        return self.analyze_name(name)[1]

    def analyze_name(self, name):
        if name[0] == '{':
            ns, local = name[1:].split("}")
        else:
            return None, None, None

        prefix = self.namespaces[ns]
        if prefix is None:
            prefix = u"!Unknown"

        return prefix, local, ns

    def _start_ns(self, prefix, ns):
        self.namespaces[ns] = prefix
        

class UMLParser(object):
    """Opens and parses:
        DIA file (compressed and uncompressed);
        XMI file."""

    def __init__(self, uml_file):
        self.root = None
        self.nstracker = NamespaceTracker()
        
        self.parse(uml_file)
        self.set_appropriate_parser()
        
    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return object.__getattribute__(self.parser, attr)

    def parse(self, ufile):
        """Opens uml file and parse it, then store its root."""
        uml_file = gzip.open(ufile)
        etree = ElementTree()

        try:
            self.root = etree.parse(uml_file, self.nstracker)

        except IOError:
            # This probably was caused because we opened the file in binary
            # mode to read a compressed DIA file but the file is not in this
            # format, so it failed. Open it as a normal file now and try to
            # parse it again.
            uml_file = open(ufile)
            self.root = etree.parse(uml_file, self.nstracker)

        finally:
            uml_file.close()

    def set_appropriate_parser(self):
        """Set a parser based on namespace found during ElementTree parsing."""
        uml_ns = self.nstracker.namespaces.values()[0].lower()
        if uml_ns == "dia":
            self.parser = DiaParser
        elif uml_ns == "uml":
            self.parser = XmiParser

    def _get_parser(self):
        """Get parser being used."""
        return self.__parser

    def _set_parser(self, parser):
        """Instanciate an UML parser."""     
        self.__parser = parser(self.root, self.nstracker)


    # Properties
    parser = property(_get_parser, _set_parser)