#! /usr/bin/env python
# $Header: /cvsroot/pywebsvcs/zsi/ZSI/writer.py,v 1.19 2006/01/03 23:45:29 boverhof Exp $
'''SOAP message serialization.
'''

from ZSI import _copyright, ZSI_SCHEMA_URI
from ZSI import _backtrace, _stringtypes, _seqtypes
from ZSI.TC import AnyElement, TypeCode
from ZSI.wstools.Utility import MessageInterface, ElementProxy
from ZSI.wstools.Namespaces import XMLNS, SOAP, SCHEMA
from ZSI.wstools.c14n import Canonicalize
import types

_standard_ns = [ ('xml', XMLNS.XML), ('xmlns', XMLNS.BASE) ]

_reserved_ns = {
        'SOAP-ENV': SOAP.ENV,
        'SOAP-ENC': SOAP.ENC,
        'ZSI': ZSI_SCHEMA_URI,
        'xsd': SCHEMA.BASE,
        'xsi': SCHEMA.BASE + '-instance',
}

class SoapWriter:
    '''SOAP output formatter.
       Instance Data:
           memo -- memory for id/href 
           envelope -- add Envelope?
           encoding -- 
           header -- add SOAP Header?
           outputclass -- ElementProxy class.
    '''

    def __init__(self, envelope=True, encoding=None, header=True, 
    nsdict={}, outputclass=None, **kw):
        '''Initialize.
        '''
        if outputclass is None:
            outputclass=ElementProxy
        if not issubclass(outputclass, MessageInterface):
            raise TypeError, 'outputclass must subclass MessageInterface'

        self.dom, self.memo, self.nsdict= \
            outputclass(self), [], nsdict
        self.envelope = envelope
        self.encodingStyle = encoding
        self.header = header
        self.body = None
        self.callbacks = []
        self.closed = False

    def __str__(self):
        self.close()
        return str(self.dom)

    def getSOAPHeader(self):
        if self.header is True or self.header is False:
            return None
        return self.header

    def serialize_header(self, hpyobjs, htypecode, **kw):
        '''Serialize a Python object in SOAP-ENV:Header, make
        sure everything in Header unique (no #href).
        '''
        kw['unique'] = True
        soap_env = _reserved_ns['SOAP-ENV']
        header = self.dom.getElement(soap_env, 'Header')
        if type(hpyobjs) not in _seqtypes:
           hpyobjs = (hpyobjs,)
        for hpyobj in hpyobjs:
            helt = htypecode.serialize(header, self, hpyobj, **kw)

    def serialize(self, pyobj, typecode=None, root=None, header_pyobjs={}, 
                   header_typecodes=(), **kw):
        '''Serialize a Python object to the output stream.
           pyobj -- python instance to serialize in body.
           typecode -- typecode describing body 
           root -- SOAP-ENC:root
           header_pyobjs -- dictionary of header instances
           header_typecodes -- list of header typecodes
        '''
        self.body = None
        if self.envelope: 
            soap_env = _reserved_ns['SOAP-ENV']
            self.dom.createDocument(soap_env, 'Envelope')
            for prefix, nsuri in _reserved_ns.items():
                self.dom.setNamespaceAttribute(prefix, nsuri)
            self.writeNSdict(self.nsdict)
            if self.encodingStyle:
                self.dom.setAttributeNS(soap_env, 'encodingStyle', 
                                        self.encodingStyle)
            if self.header:
                header = self.dom.createAppendElement(soap_env, 'Header')
                for htypecode in header_typecodes:
                    nspname,pname = htypecode.nspname,htypecode.pname
                    hpyobjs = header_pyobjs.get((nspname,pname))
                    if hpyobjs is not None:
                        self.serialize_header(hpyobjs, htypecode, **kw)

            self.body = self.dom.createAppendElement(soap_env, 'Body')
        else:
            self.dom.createDocument(None,None)

        if typecode is None: typecode = pyobj.__class__.typecode
        if TypeCode.typechecks and type(pyobj) == types.InstanceType and \
        not hasattr(typecode, 'pyclass'):
            pass
            # XXX XML ...
            #raise TypeError('Serializing Python object with other than Struct.')
        kw = kw.copy()
        
        # TODO: FIX THIS...
        #if root in [ 0, 1 ]:
        #    kw['attrtext'] = ' SOAP-ENC:root="%d"' % root
            
        if self.body is None:
            typecode.serialize(self.dom, self, pyobj, **kw)
        else:
            typecode.serialize(self.body, self, pyobj, **kw)
        return self

    def writeNSdict(self, nsdict):
        '''Write a namespace dictionary, taking care to not clobber the
        standard (or reserved by us) prefixes.
        '''
        for k,v in nsdict.items():
            if (k,v) in _standard_ns: continue
            rv = _reserved_ns.get(k)
            if rv:
                if rv != v:
                    raise KeyError("Reserved namespace " + str((k,v)) + " used")
                continue
            if k:
                self.dom.setNamespaceAttribute(k, v)
            else:
                self.dom.setNamespaceAttribute('xmlns', v)


    def ReservedNS(self, prefix, uri):
        '''Is this namespace (prefix,uri) reserved by us?
        '''
        return _reserved_ns.get(prefix, uri) != uri

    def AddCallback(self, func, *arglist):
        '''Add a callback function and argument list to be invoked before
        closing off the SOAP Body.
        '''
        self.callbacks.append((func, arglist))

    def Known(self, obj):
        '''Seen this object (known by its id()?  Return 1 if so,
        otherwise add it to our memory and return 0.
        '''
        obj = id(obj)
        if obj in self.memo: return 1
        self.memo.append(obj)
        return 0

    def Forget(self, obj):
        '''Forget we've seen this object.
        '''
        obj = id(obj)
        try:
            self.memo.remove(obj)
        except ValueError:
            pass

    def Backtrace(self, elt):
        '''Return a human-readable "backtrace" from the document root to
        the specified element.
        '''
        return _backtrace(elt._getNode(), self.dom._getNode())

    def close(self):
        '''Invoke all the callbacks, and close off the SOAP message.
        '''
        if self.closed: return
        for func,arglist in self.callbacks:
            apply(func, arglist)
        self.closed = True

    def __del__(self):
        if not self.closed: self.close()
        

if __name__ == '__main__': print _copyright
