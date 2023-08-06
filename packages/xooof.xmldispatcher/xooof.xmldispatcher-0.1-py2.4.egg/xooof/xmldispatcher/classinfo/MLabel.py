
from xooof.xmlstruct.xmlstruct import XMLStructBase, XMLStructBase_C
from xooof.xmlstruct.metafield import *
from xooof.xmlstruct.typeinfo import *



class MLabel(XMLStructBase):
    #__slots__ = ["lang", "descr", ]
    _metaStruct = None

    def _getMetaStruct(cls):
        if cls._metaStruct is None:
            cls._metaStruct = MLabel_M()
        return cls._metaStruct

    _getMetaStruct = classmethod(_getMetaStruct)


class MLabel_C(XMLStructBase_C):
    _itemKlass = MLabel

class MLabel_M:

    _xsNamespaceURI = "http://xmlcatalog/catalog/spectools/class/classinfo" or None

    def __init__(self):

        self._lfields = []
        self._dfields = {}

        fname = "lang"
        fmeta = MetaVField(MLabel_M._xsNamespaceURI, TypeInfo_string(2, 2, None), 0, MetaVField.SERIALIZE_element)
        self._lfields.append((fname,fmeta))

        self._dfields[fname] = fmeta

        fname = "descr"
        fmeta = MetaVField(MLabel_M._xsNamespaceURI, TypeInfo_string(1, None, None), 1, MetaVField.SERIALIZE_element)
        self._lfields.append((fname,fmeta))

        self._dfields[fname] = fmeta
