
from xooof.xmlstruct.xmlstruct import XMLStructBase, XMLStructBase_C
from xooof.xmlstruct.metafield import *
from xooof.xmlstruct.typeinfo import *



class MInstanceMethod(XMLStructBase):
    #__slots__ = ["name", "descr", "interfaceName", "special", "states", ]
    _metaStruct = None

    def _getMetaStruct(cls):
        if cls._metaStruct is None:
            cls._metaStruct = MInstanceMethod_M()
        return cls._metaStruct

    _getMetaStruct = classmethod(_getMetaStruct)


class MInstanceMethod_C(XMLStructBase_C):
    _itemKlass = MInstanceMethod

class MInstanceMethod_M:

    _xsNamespaceURI = "http://xmlcatalog/catalog/spectools/class/classinfo" or None

    def __init__(self):

        # import gfield and glfield classes
        import MLabel
        self._lfields = []
        self._dfields = {}

        fname = "name"
        fmeta = MetaVField(MInstanceMethod_M._xsNamespaceURI, TypeInfo_string(1, None, None), 1, MetaVField.SERIALIZE_element)
        self._lfields.append((fname,fmeta))

        self._dfields[fname] = fmeta

        fname = "descr"
        fmeta = MetaGLField(MInstanceMethod_M._xsNamespaceURI, MLabel.MLabel_C, 1, None)
        self._lfields.append((fname,fmeta))
        self._dfields[fname] = fmeta

        fname = "interfaceName"
        fmeta = MetaVField(MInstanceMethod_M._xsNamespaceURI, TypeInfo_string(1, None, None), 0, MetaVField.SERIALIZE_element)
        self._lfields.append((fname,fmeta))

        self._dfields[fname] = fmeta

        fname = "special"
        fmeta = MetaVField(MInstanceMethod_M._xsNamespaceURI, TypeInfo_string(1, None, None), 0, MetaVField.SERIALIZE_element)
        self._lfields.append((fname,fmeta))
        fmeta.addChoiceXML("constructor")
        fmeta.addChoiceXML("destructor")

        self._dfields[fname] = fmeta

        fname = "states"
        fmeta = MetaVLField(MInstanceMethod_M._xsNamespaceURI, TypeInfo_string(1, None, None), 0, None)
        self._lfields.append((fname,fmeta))

        self._dfields[fname] = fmeta
