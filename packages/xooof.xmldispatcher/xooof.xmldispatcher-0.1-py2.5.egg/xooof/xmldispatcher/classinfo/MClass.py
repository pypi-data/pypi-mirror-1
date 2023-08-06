
from xooof.xmlstruct.xmlstruct import XMLStructBase, XMLStructBase_C
from xooof.xmlstruct.metafield import *
from xooof.xmlstruct.typeinfo import *



class MClass(XMLStructBase):
    #__slots__ = ["name", "descr", "classmethods", "instancemethods", "states", ]
    _metaStruct = None

    def _getMetaStruct(cls):
        if cls._metaStruct is None:
            cls._metaStruct = MClass_M()
        return cls._metaStruct

    _getMetaStruct = classmethod(_getMetaStruct)


class MClass_C(XMLStructBase_C):
    _itemKlass = MClass

class MClass_M:

    _xsNamespaceURI = "http://xmlcatalog/catalog/spectools/class/classinfo" or None

    def __init__(self):

        # import gfield and glfield classes
        import MLabel
        import MClassMethod
        import MInstanceMethod
        import MState
        self._lfields = []
        self._dfields = {}

        fname = "name"
        fmeta = MetaVField(MClass_M._xsNamespaceURI, TypeInfo_string(1, None, None), 1, MetaVField.SERIALIZE_element)
        self._lfields.append((fname,fmeta))

        self._dfields[fname] = fmeta

        fname = "descr"
        fmeta = MetaGLField(MClass_M._xsNamespaceURI, MLabel.MLabel_C, 1, None)
        self._lfields.append((fname,fmeta))
        self._dfields[fname] = fmeta

        fname = "classmethods"
        fmeta = MetaGLField(MClass_M._xsNamespaceURI, MClassMethod.MClassMethod_C, 0, None)
        self._lfields.append((fname,fmeta))
        self._dfields[fname] = fmeta

        fname = "instancemethods"
        fmeta = MetaGLField(MClass_M._xsNamespaceURI, MInstanceMethod.MInstanceMethod_C, 0, None)
        self._lfields.append((fname,fmeta))
        self._dfields[fname] = fmeta

        fname = "states"
        fmeta = MetaGLField(MClass_M._xsNamespaceURI, MState.MState_C, 0, None)
        self._lfields.append((fname,fmeta))
        self._dfields[fname] = fmeta
