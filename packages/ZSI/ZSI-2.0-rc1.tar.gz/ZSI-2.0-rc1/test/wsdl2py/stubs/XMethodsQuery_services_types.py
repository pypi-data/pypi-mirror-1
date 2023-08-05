################################################## 
# XMethodsQuery_services_types.py 
# generated by ZSI.generate.wsdl2python
##################################################


import ZSI
import ZSI.TCcompound
from ZSI.TC import ElementDeclaration,TypeDefinition
from ZSI.generate.pyclass import pyclass_type

##############################
# targetNamespace
# http://www.xmethods.net/interfaces/query.xsd
##############################

class ns0:
    targetNamespace = "http://www.xmethods.net/interfaces/query.xsd"

    class ServiceSummary_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://www.xmethods.net/interfaces/query.xsd"
        type = (schema, "ServiceSummary")
        def __init__(self, pname, **kw):
            ns = ns0.ServiceSummary_Def.schema
            TClist = [ZSI.TC.String(pname="name", aname="_name", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="id", aname="_id", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="shortDescription", aname="_shortDescription", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="wsdlURL", aname="_wsdlURL", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="publisherID", aname="_publisherID", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._name = None
                    self._id = None
                    self._shortDescription = None
                    self._wsdlURL = None
                    self._publisherID = None
                    return
            Holder.__name__ = "ServiceSummary_Holder"
            self.pyclass = Holder

    class ArrayOfServiceSummary_Def(ZSI.TC.Array, TypeDefinition):
        schema = "http://www.xmethods.net/interfaces/query.xsd"
        type = (schema, "ArrayOfServiceSummary")
        def __init__(self, pname, **kw):
            ofwhat = ns0.ServiceSummary_Def(None, typed=False)
            atype = (u'http://www.xmethods.net/interfaces/query.xsd', u'ServiceSummary[]')
            ZSI.TCcompound.Array.__init__(self, atype, ofwhat, pname=pname, childnames='item', **kw)

    class IDNamePair_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://www.xmethods.net/interfaces/query.xsd"
        type = (schema, "IDNamePair")
        def __init__(self, pname, **kw):
            ns = ns0.IDNamePair_Def.schema
            TClist = [ZSI.TC.String(pname="id", aname="_id", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="name", aname="_name", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._id = None
                    self._name = None
                    return
            Holder.__name__ = "IDNamePair_Holder"
            self.pyclass = Holder

    class ArrayOfIDNamePair_Def(ZSI.TC.Array, TypeDefinition):
        schema = "http://www.xmethods.net/interfaces/query.xsd"
        type = (schema, "ArrayOfIDNamePair")
        def __init__(self, pname, **kw):
            ofwhat = ns0.IDNamePair_Def(None, typed=False)
            atype = (u'http://www.xmethods.net/interfaces/query.xsd', u'IDNamePair[]')
            ZSI.TCcompound.Array.__init__(self, atype, ofwhat, pname=pname, childnames='item', **kw)

    class ServiceDetail_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://www.xmethods.net/interfaces/query.xsd"
        type = (schema, "ServiceDetail")
        def __init__(self, pname, **kw):
            ns = ns0.ServiceDetail_Def.schema
            TClist = [ZSI.TC.String(pname="name", aname="_name", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="id", aname="_id", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="shortDescription", aname="_shortDescription", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="description", aname="_description", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="implementationID", aname="_implementationID", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="email", aname="_email", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="wsdlURL", aname="_wsdlURL", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="infoURL", aname="_infoURL", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="discussionURL", aname="_discussionURL", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="notes", aname="_notes", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="tmodelID", aname="_tmodelID", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="publisherID", aname="_publisherID", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded")), ZSI.TC.String(pname="uuid", aname="_uuid", minOccurs=1, maxOccurs=1, nillable=True, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._name = None
                    self._id = None
                    self._shortDescription = None
                    self._description = None
                    self._implementationID = None
                    self._email = None
                    self._wsdlURL = None
                    self._infoURL = None
                    self._discussionURL = None
                    self._notes = None
                    self._tmodelID = None
                    self._publisherID = None
                    self._uuid = None
                    return
            Holder.__name__ = "ServiceDetail_Holder"
            self.pyclass = Holder

# end class ns0 (tns: http://www.xmethods.net/interfaces/query.xsd)
