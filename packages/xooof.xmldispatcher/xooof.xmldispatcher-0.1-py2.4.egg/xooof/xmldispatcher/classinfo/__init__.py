
__all__ = [
  "MClass",
  "MClassMethod",
  "MInstanceMethod",
  "MLabel",
  "MState"
]

from xooof.xmlstruct import xmlstruct 

namespaceURI = "http://xmlcatalog/catalog/spectools/class/classinfo" or None

class PackageXMLStructFactory(xmlstruct.IXMLStructFactory):
    """This is a struct factory and an autoloader"""

    def __init__(self,namespaceURI):
        self.__namespaceURI = namespaceURI
        
    def _loadClass(self,moduleName,className):
        module = __import__(moduleName,globals())
        klass = getattr(module,className)
        self.__dict__[className] = klass
        return klass

    def __getattr__(self,name):
        if name.startswith("_"):
            raise AttributeError, name
        if name.endswith("_C"):
            moduleName = name[:-2]
        else:
            moduleName = name
        try:
            return self._loadClass(moduleName,name)
        except:
            raise AttributeError, name

    def create(self,name):
        namespaceURI,localName = name
        if namespaceURI == self.__namespaceURI:
            if localName.endswith("-list"):
                moduleName = localName[:-5]
                className = moduleName + "_C"
            else:
                moduleName = className = localName
            try:
                try:
                    klass = self.__dict__[className]
                except KeyError:
                    klass = self._loadClass(moduleName,className)
                return klass()
            except Exception, e:
                raise xmlstruct.XMLStructFactoryError, e
        else:
            raise xmlstruct.XMLStructFactoryError, \
                  "namespace %s is not recognised by this factory" % \
                  namespaceURI

# this is the structfactory and autoloader
sf = PackageXMLStructFactory(namespaceURI)

# this package behaves as IXMLStructFactory 
create = sf.create
