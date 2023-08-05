############################################################################
# Joshua R. Boverhof, LBNL
# See Copyright for copyright notice!
###########################################################################

import time, urlparse, socket
from ZSI import _seqtypes, EvaluateException, WSActionException
from ZSI.TC import _get_global_element_declaration, _get_type_definition, \
     _has_type_definition, AnyElement, AnyType, TypeCode
from ZSI.TCcompound import ComplexType
from ZSI.wstools.Namespaces import WSA_LIST


class Address(object):
    '''WS-Address
    '''
    def __init__(self, addressTo=None, wsAddressURI=None, action=None):
        self.wsAddressURI = wsAddressURI
        self.anonymousURI = None
        self._addressTo = addressTo
        self._messageID = None
        self._action = action
        self._endPointReference = None
        self._replyTo = None
        self._relatesTo = None
        self.setUp()

    def setUp(self):
        '''Look for WS-Address
        '''
        toplist = filter(lambda wsa: wsa.ADDRESS==self.wsAddressURI, WSA_LIST)
        epr = 'EndpointReferenceType'
        for WSA in toplist+WSA_LIST:
            if (self.wsAddressURI is not None and self.wsAddressURI != WSA.ADDRESS) or \
                _has_type_definition(WSA.ADDRESS, epr) is True:
                break
        else:
            raise EvaluateException,\
                'enabling wsAddressing requires the inclusion of that namespace'

        self.wsAddressURI = WSA.ADDRESS
        self.anonymousURI = WSA.ANONYMOUS
        self._replyTo = WSA.ANONYMOUS

    def _checkAction(self, action, value):
        '''WS-Address Action
        action -- Action value expecting.
        value  -- Action value server returned.
        '''
        if action is None:
            raise WSActionException, 'User did not specify WSAddress Action value to expect'
        if not value:
            raise WSActionException, 'missing WSAddress Action, expecting %s' %action
        if value != action:
            raise WSActionException, 'wrong WSAddress Action(%s), expecting %s'%(value,action)

    def _checkFrom(self, pyobj):
        '''WS-Address From, 
        XXX currently not checking the hostname, not forwarding messages.
        pyobj  -- From server returned.
        '''
        if pyobj is None: return
        value = pyobj._Address
        if value != self._addressTo:
            scheme,netloc,path,query,fragment = urlparse.urlsplit(value)
            hostport = netloc.split(':')
            schemeF,netlocF,pathF,queryF,fragmentF = urlparse.urlsplit(self._addressTo)
            if scheme==schemeF and path==pathF and query==queryF and fragment==fragmentF:
                netloc = netloc.split(':') + ['80']
                netlocF = netlocF.split(':') + ['80']
                if netloc[1]==netlocF[1] and \
                   socket.gethostbyname(netloc[0])==socket.gethostbyname(netlocF[0]):
                    return

            raise WSActionException, 'wrong WS-Address From(%s), expecting %s'%(value,self._addressTo)

    def _checkRelatesTo(self, value):
        '''WS-Address From
        value  -- From server returned.
        '''
        if value != self._messageID:
            raise WSActionException, 'wrong WS-Address RelatesTo(%s), expecting %s'%(value,self._messageID)
        
    def _checkReplyTo(self, value):
        '''WS-Address From
        value  -- From server returned in wsa:To
        '''
        if value != self._replyTo:
            raise WSActionException, 'wrong WS-Address ReplyTo(%s), expecting %s'%(value,self._replyTo)

    def setAction(self, action):
        self._action = action

    def getAction(self):
        return self._action

    def getRelatesTo(self):
        return self._relatesTo

    def getMessageID(self):
        return self._messageID

    def _getWSAddressTypeCodes(self, **kw):
        '''kw -- namespaceURI keys with sequence of element names.
        '''
        typecodes = []
        try:
            for nsuri,elements in kw.items():
                for el in elements:
                    typecode = _get_global_element_declaration(nsuri, el)
                    if typecode is None:
                        raise WSActionException, 'Missing namespace, import "%s"' %nsuri

                    typecodes.append(typecode)
            else:
                pass
        except EvaluateException, ex:
            raise EvaluateException, \
                'To use ws-addressing register typecodes for namespace(%s)' %self.wsAddressURI
        return typecodes

    def checkResponse(self, ps, action):
        ''' 
        ps -- ParsedSoap
        action -- ws-action for response
        '''
        namespaceURI = self.wsAddressURI
        d = {namespaceURI:("MessageID","Action","To","From","RelatesTo")}
        typecodes = self._getWSAddressTypeCodes(**d)
        pyobjs = ps.ParseHeaderElements(typecodes)

        got_action = pyobjs.get((namespaceURI,"Action"))
        self._checkAction(got_action, action)

        From = pyobjs.get((namespaceURI,"From"))
        self._checkFrom(From)

        RelatesTo = pyobjs.get((namespaceURI,"RelatesTo"))
        self._checkRelatesTo(RelatesTo)

        To = pyobjs.get((namespaceURI,"To"))
        if To: self._checkReplyTo(To)

    def setRequest(self, endPointReference, action):
        '''Call For Request
        '''
        self._action = action
        self.header_pyobjs = None
        pyobjs = []
        namespaceURI = self.wsAddressURI
        addressTo = self._addressTo
        messageID = self._messageID = "uuid:%s" %time.time()

        # Set Message Information Headers
        # MessageID
        typecode = _get_global_element_declaration(namespaceURI, "MessageID")
        pyobjs.append(typecode.pyclass(messageID))

        # Action
        typecode = _get_global_element_declaration(namespaceURI, "Action")
        pyobjs.append(typecode.pyclass(action))

        # To
        typecode = _get_global_element_declaration(namespaceURI, "To")
        pyobjs.append(typecode.pyclass(addressTo))

        # From
        typecode = _get_global_element_declaration(namespaceURI, "From")
        mihFrom = typecode.pyclass()
        mihFrom._Address = self.anonymousURI
        pyobjs.append(mihFrom)

        if endPointReference:
            if hasattr(endPointReference, 'typecode') is False:
                raise EvaluateException, 'endPointReference must have a typecode attribute'

            if isinstance(endPointReference.typecode, \
                _get_type_definition(namespaceURI ,'EndpointReferenceType')) is False:
                raise EvaluateException, 'endPointReference must be of type %s' \
                    %_get_type_definition(namespaceURI ,'EndpointReferenceType')

            find = lambda what: isinstance(what,tc)
            ncname = 'ReferencePropertiesType'
            tc = _get_type_definition(namespaceURI, ncname)
            what = filter(find, endPointReference.typecode.ofwhat)
            if len(what) != 1:
                raise EvaluateException,\
                    'EPR must contain one element of type (%s,%s)' %(namespaceURI,ncname)

            what = what[0]
            ReferenceProperties = getattr(endPointReference, what.aname)
             
            #Assuming maxOccurs=1 
            tc = AnyElement
            what = filter(find, what.ofwhat)
            if len(what) != 1:
                raise EvaluateException, 'EPR must contain one <any>'

            what = what[0]
            any = getattr(ReferenceProperties, what.aname)

            if not (what.maxOccurs=='unbounded' and type(any) in _seqtypes):
                raise EvaluateException, 'ReferenceProperties <any> assumed maxOccurs unbounded'

            for v in any:
                if not hasattr(v,'typecode'):
                    raise EvaluateException, '<any> element, instance missing typecode attribute'

                pyobjs.append(v)

            #pyobjs.append(v)

        self.header_pyobjs = tuple(pyobjs)

    def setResponseFromWSAddress(self, address, localURL):
        '''Server-side has to set these fields in response.
        address -- Address instance, representing a WS-Address
        '''
        self.From = localURL
        self.header_pyobjs = None
        pyobjs = []
        namespaceURI = self.wsAddressURI

        for nsuri,name,value in (\
             (namespaceURI, "Action", self._action), 
             (namespaceURI, "MessageID","uuid:%s" %time.time()),
             (namespaceURI, "RelatesTo", address.getMessageID()),
             (namespaceURI, "To", self.anonymousURI),):

            typecode = _get_global_element_declaration(nsuri, name)
            pyobjs.append(typecode.pyclass(value))

        typecode = _get_global_element_declaration(nsuri, "From")
        pyobj = typecode.pyclass()
        pyobj._Address = self.From
        pyobjs.append(pyobj)
        self.header_pyobjs = tuple(pyobjs)


    def serialize(self, sw, **kw):
        '''
        sw -- SoapWriter instance, add WS-Address header.
        '''
        for pyobj in self.header_pyobjs:
            if hasattr(pyobj, 'typecode') is False:
                raise RuntimeError, 'all header pyobjs must have a typecode attribute'

            sw.serialize_header(pyobj, **kw)
        

    def parse(self, ps, **kw):
        '''
        ps -- ParsedSoap instance
        '''
        namespaceURI = self.wsAddressURI
        elements = ("MessageID","Action","To","From","RelatesTo")
        d = {namespaceURI:elements}
        typecodes = self._getWSAddressTypeCodes(**d)
        pyobjs = ps.ParseHeaderElements(typecodes)
        self._messageID = pyobjs[(namespaceURI,elements[0])]
        self._action = pyobjs[(namespaceURI,elements[1])]
        self._addressTo = pyobjs[(namespaceURI,elements[2])]
        self._from = pyobjs[(namespaceURI,elements[3])]
        self._relatesTo = pyobjs[(namespaceURI,elements[4])]

# TODO: Remove MessageContainer.  Hopefully the new <any> functionality
#       makes this irrelevant.  But could create an Interop problem.
"""
class MessageContainer:
    '''Automatically wraps all primitive types so attributes 
    can be specified.
    '''
    class IntHolder(int): pass
    class StrHolder(str): pass
    class UnicodeHolder(unicode): pass
    class LongHolder(long): pass
    class FloatHolder(float): pass
    class BoolHolder(int): pass
    #class TupleHolder(tuple): pass
    #class ListHolder(list): pass
    typecode = None
    pyclass_list = [IntHolder,StrHolder,UnicodeHolder,LongHolder,
        FloatHolder,BoolHolder,]

    def __setattr__(self, key, value):
        '''wrap all primitives with Holders if present.
        '''
        if type(value) in _seqtypes:
            value = list(value)
            for indx in range(len(value)):
                try:
                    item = self._wrap(value[indx])
                except TypeError, ex:
                    pass
                else:
                    value[indx] = item
        elif type(value) is bool:
            value = BoolHolder(value)
        else:
            try:
                value = self._wrap(value)
            except TypeError, ex:
                pass
        self.__dict__[key] = value

    def _wrap(self, value):
        '''wrap primitive, return None
        '''
        if value is None: 
            return value
        for pyclass in self.pyclass_list:
            if issubclass(value.__class__, pyclass): break
        else:
            raise TypeError, 'MessageContainer does not know about type %s' %(type(value))
        return pyclass(value)

    def setUp(self, typecode=None, pyclass=None):
        '''set up all attribute names (aname) in this python instance.
        If what is a ComplexType or a simpleType w/attributes instantiate 
        a new MessageContainer, else set attribute aname to None.
        '''
        if typecode is None: 
            typecode = self.typecode
        else:
            self.typecode = typecode

        if not isinstance(typecode, TypeCode):
            raise TypeError, 'typecode must be a TypeCode class instance'

        if isinstance(typecode, ComplexType):
            if typecode.has_attributes() is True:
                setattr(self, typecode.attrs_aname, {})
            if typecode.mixed is True:
                setattr(self, typecode.mixed_aname, None)
            for what in typecode.ofwhat:
                setattr(self, what.aname, None)
                if isinstance(what, ComplexType):
                    setattr(self, what.aname, MessageContainer())
                    getattr(self, what.aname).setUp(typecode=what)
        else:
            raise TypeError, 'Primitive type'
"""


if __name__ == '__main__': print _copyright
