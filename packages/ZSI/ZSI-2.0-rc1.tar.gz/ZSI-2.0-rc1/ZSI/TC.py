#! /usr/bin/env python
# $Header: /cvsroot/pywebsvcs/zsi/ZSI/TC.py,v 1.41 2006/01/03 23:45:29 boverhof Exp $
'''General typecodes.
'''

from ZSI import _copyright, _children, _child_elements, \
    _floattypes, _stringtypes, _seqtypes, _find_attr, _find_attrNS, \
    _find_arraytype, _find_default_namespace, _find_href, _find_encstyle, \
    _resolve_prefix, _find_xsi_attr, _find_type, \
    _find_xmlns_prefix, _get_element_nsuri_name, _Node, EvaluateException, \
    _valid_encoding, ParseException

from ZSI.wstools.Namespaces import SCHEMA, SOAP
from ZSI.wstools.Utility import Base, SplitQName
from ZSI.wstools.c14n import Canonicalize

import re, types, time, copy

from base64 import decodestring as b64decode, encodestring as b64encode
from urllib import unquote as urldecode, quote as urlencode
from binascii import unhexlify as hexdecode, hexlify as hexencode

UNBOUNDED = 'unbounded'

_is_xsd_or_soap_ns = lambda ns: ns in [
                        SCHEMA.XSD3, SOAP.ENC, SCHEMA.XSD1, SCHEMA.XSD2, ]
_find_nil = lambda E: _find_xsi_attr(E, "null") or _find_xsi_attr(E, "nil")

def _get_xsitype(pyclass):
    if hasattr(pyclass,'type') and type(pyclass.type) in _seqtypes:
        return pyclass.type
    elif hasattr(pyclass,'type') and hasattr(pyclass, 'schema'):
        return (pyclass.schema, pyclass.type)

    return (None,None)

def _get_object_id(pyobj):
    '''Python 2.3.x will generate a FutureWarning for negative IDs, so
    we use a different prefix character to ensure uniqueness, and
    call abs() to avoid the warning.'''
    x = id(pyobj)
    if x < 0:
        return 'x%x' % abs(x)
    
    return 'o%x' % x

def _get_type_definition(namespaceURI, name):
    return SchemaInstanceType.getTypeDefinition(namespaceURI, name)

def _get_global_element_declaration(namespaceURI, name):
    return SchemaInstanceType.getElementDeclaration(namespaceURI, name)

def _get_substitute_element(elt, what):
    raise NotImplementedError, 'Not implemented'

def _has_type_definition(namespaceURI, name):
    return SchemaInstanceType.getTypeDefinition(namespaceURI, name) is not None


class SchemaInstanceType(type):
    '''Register all types/elements, when hit already defined 
    class dont create a new one just give back reference.  Thus 
    import order determines which class is loaded.
    '''
    types = {}
    elements = {}

    def __new__(cls,classname,bases,classdict):
        '''If classdict has literal and schema register it as a
        element declaration, else if has type and schema register
        it as a type definition.
        '''
        if classname in ['ElementDeclaration', 'TypeDefinition']:
            return type.__new__(cls,classname,bases,classdict)

        if ElementDeclaration in bases:
            if classdict.has_key('schema') is False  or classdict.has_key('literal') is False: 
                raise AttributeError, 'ElementDeclaration must define schema and literal attributes'

            key = (classdict['schema'],classdict['literal'])
            if SchemaInstanceType.elements.has_key(key) is False:
                SchemaInstanceType.elements[key] = type.__new__(cls,classname,bases,classdict)
            return SchemaInstanceType.elements[key]

        if TypeDefinition in bases:
            if classdict.has_key('type') is None:
                raise AttributeError, 'TypeDefinition must define type attribute'

            key = classdict['type']
            if SchemaInstanceType.types.has_key(key) is False:
                SchemaInstanceType.types[key] = type.__new__(cls,classname,bases,classdict)
            return SchemaInstanceType.types[key]

        raise TypeError, 'SchemaInstanceType must be an ElementDeclaration or TypeDefinition '

    def getTypeDefinition(cls, namespaceURI, name):
        '''Grab a type definition
        namespaceURI -- 
        name -- 
        '''
        return cls.types.get((namespaceURI, name), None)
    getTypeDefinition = classmethod(getTypeDefinition)

    def getElementDeclaration(cls, namespaceURI, name):
        '''Grab an element declaration
        namespaceURI -- 
        name -- 
        '''
        return cls.elements.get((namespaceURI, name), None)
    getElementDeclaration = classmethod(getElementDeclaration)


class ElementDeclaration:
    '''Typecodes subclass to represent a Global Element Declaration by
    setting class variables schema and literal.

    schema = namespaceURI
    literal = NCName
    '''
    __metaclass__ = SchemaInstanceType


class TypeDefinition:
    '''Typecodes subclass to represent a Global Type Definition by
    setting class variable type.

    type = (namespaceURI, NCName)
    '''
    __metaclass__ = SchemaInstanceType


class TypeCode(Base):
    '''The parent class for all parseable SOAP types.
    Class data:
        typechecks -- do init-time type checking if non-zero
    Class data subclasses may define:
        tag -- global element declaration
        type -- global type definition
        parselist -- list of valid SOAP types for this class, as
            (uri,name) tuples, where a uri of None means "all the XML
            Schema namespaces"
        errorlist -- parselist in a human-readable form; will be
            generated if/when needed
        seriallist -- list of Python types or user-defined classes
            that this typecode can serialize.
    '''
    tag = None
    type = (None,None)
    typechecks = True
    attribute_typecode_dict = None

    def __init__(self, pname=None, aname=None, minOccurs=1,
    maxOccurs=1, nillable=False, typed=True, unique=True, 
    pyclass=None, attrs_aname='_attrs',
    **kw):
        '''Baseclass initialization.
        Instance data (and usually keyword arg)
            pname -- the parameter name (localname).
            nspname -- the namespace for the parameter;
                None to ignore the namespace
            typed -- output xsi:type attribute
            unique -- data item is not aliased (no href/id needed)
            minOccurs -- min occurances
            maxOccurs -- max occurances
            nillable -- is item nillable?
            attrs_aname -- This is variable name to dictionary of attributes
            encoded -- encoded namespaceURI (specify if use is encoded)
        '''
        Base.__init__(self)
        if type(pname) in _seqtypes:
            self.nspname, self.pname = pname
        else:
            self.nspname, self.pname = None, pname

        if self.pname:
            self.pname = str(self.pname).split(':')[-1]

        self.aname = aname or self.pname
        self.minOccurs = minOccurs
        self.maxOccurs = maxOccurs
        self.nillable = nillable
        self.typed = typed
        self.unique = unique
        self.attrs_aname = attrs_aname
        self.pyclass = pyclass
        #if kw.has_key('default'): self.default = kw['default']

        # Need this stuff for rpc/encoded.
        encoded = kw.get('encoded')
        if encoded is not None:
            self.nspname = kw['encoded']

    def parse(self, elt, ps):
        '''elt -- the DOM element being parsed
        ps -- the ParsedSoap object.
        '''
        raise EvaluateException("Unimplemented evaluation", ps.Backtrace(elt))

    def serialize(self, elt, sw, pyobj, name=None, orig=None, **kw):
        '''elt -- the current DOMWrapper element 
           sw -- soapWriter object
           pyobj -- python object to serialize

        '''
        raise EvaluateException("Unimplemented evaluation", sw.Backtrace(elt))

    def text_to_data(self, text):
        '''convert text into typecode specific data.
        '''
        raise EvaluateException("Unimplemented evaluation", sw.Backtrace(elt))

    def serialize_as_nil(self, elt):
        '''elt -- the current DOMWrapper element 
        '''
        elt.setAttributeNS(SCHEMA.XSI3, 'nil', '1')

    def SimpleHREF(self, elt, ps, tag):
        '''Simple HREF for non-string and non-struct and non-array.
        '''
        if len(_children(elt)): return elt
        href = _find_href(elt)
        if not href:
            if self.minOccurs is 0: return None
            raise EvaluateException('Non-optional ' + tag + ' missing',
                    ps.Backtrace(elt))
        return ps.FindLocalHREF(href, elt, 0)

    def get_parse_and_errorlist(self):
        """Get the parselist and human-readable version, errorlist is returned,
        because it is used in error messages.
        """
        d = self.__class__.__dict__
        parselist = d.get('parselist')
        errorlist = d.get('errorlist')
        if parselist and not errorlist:
            errorlist = []
            for t in parselist:
                if t[1] not in errorlist: errorlist.append(t[1])
            errorlist = ' or '.join(errorlist)
            d['errorlist'] = errorlist
        return (parselist, errorlist)

    def checkname(self, elt, ps):
        '''See if the name and type of the "elt" element is what we're
        looking for.   Return the element's type.
        '''

        parselist,errorlist = self.get_parse_and_errorlist()
        ns, name = _get_element_nsuri_name(elt)
        if ns == SOAP.ENC:
            # Element is in SOAP namespace, so the name is a type.
            if parselist and \
            (None, name) not in parselist and (ns, name) not in parselist:
                raise EvaluateException(
                'Element mismatch (got %s wanted %s) (SOAP encoding namespace)' % \
                        (name, errorlist), ps.Backtrace(elt))
            return (ns, name)

        # Not a type, check name matches.
        if self.nspname and ns != self.nspname:
            raise EvaluateException('Element NS mismatch (got %s wanted %s)' % \
                (ns, self.nspname), ps.Backtrace(elt))

        if self.pname and name != self.pname:
            raise EvaluateException('Element Name mismatch (got %s wanted %s)' % \
                (name, self.pname), ps.Backtrace(elt))
        return self.checktype(elt, ps)

    def checktype(self, elt, ps):
        '''See if the type of the "elt" element is what we're looking for.
        Return the element's type.
        '''
        typeName = _find_type(elt)
        if typeName is None or typeName == "":
            return (None,None)

        # Parse the QNAME.
        prefix,typeName = SplitQName(typeName)
        uri = ps.GetElementNSdict(elt).get(prefix)
        if uri is None:
            raise EvaluateException('Malformed type attribute (bad NS)',
                    ps.Backtrace(elt))

        #typeName = list[1]
        parselist,errorlist = self.get_parse_and_errorlist()
        if not parselist or \
        (uri,typeName) in parselist or \
        (_is_xsd_or_soap_ns(uri) and (None,typeName) in parselist):
            return (uri,typeName)
        raise EvaluateException(
                'Type mismatch (%s namespace) (got %s wanted %s)' % \
                (uri, typeName, errorlist), ps.Backtrace(elt))

    def name_match(self, elt):
        '''Simple boolean test to see if we match the element name.
        '''
        return self.pname == elt.localName and \
                    self.nspname in [None, elt.namespaceURI]

    def nilled(self, elt, ps):
        '''Is the element NIL, and is that okay?
        '''
        if _find_nil(elt) not in [ "true",  "1"]: return False
        if self.nillable is False:
            raise EvaluateException('Non-nillable element is NIL',
                    ps.Backtrace(elt))
        return True

    def simple_value(self, elt, ps):
        '''Get the value of the simple content of this element.
        '''
        if not _valid_encoding(elt):
            raise EvaluateException('Invalid encoding', ps.Backtrace(elt))
        c = _children(elt)
        if len(c) == 0:
            raise EvaluateException('Value missing', ps.Backtrace(elt))
        for c_elt in c:
            if c_elt.nodeType == _Node.ELEMENT_NODE:
                raise EvaluateException('Sub-elements in value',
                    ps.Backtrace(c_elt))

        # It *seems* to be consensus that ignoring comments and
        # concatenating the text nodes is the right thing to do.
        return ''.join([E.nodeValue for E in c
                if E.nodeType 
                in [ _Node.TEXT_NODE, _Node.CDATA_SECTION_NODE ]])

    def parse_attributes(self, elt):
        '''find all attributes specified in the attribute_typecode_dict in
        current element tag, if an attribute is found set it in the 
        self.attributes dictionary.  Default to putting in String.
        '''
        attributes = {}
        if self.attribute_typecode_dict is None: return
        for attr,what in self.attribute_typecode_dict.items():
            if type(attr) in _seqtypes: 
                namespaceURI,localName = attr
                value = _find_attrNS(elt, namespaceURI, localName)
                self.logger.debug("Parsed Attribute (%s,%s) -- %s", namespaceURI, localName, value)
            else:
                value = _find_attr(elt, attr)
                self.logger.debug("Parsed Attribute (%s) -- %s", attr, value)
            # For Now just set it w/o any type interpretation.
            if value is None: continue
            attributes[attr] = value
        return attributes

    def set_attributes(self, el, pyobj):
        '''Instance data attributes contains a dictionary 
        of keys (namespaceURI,localName) and attribute values.
        These values can be self-describing (typecode), or use
        attribute_typecode_dict to determine serialization.
            el -- MessageInterface instance representing the element
                declaration.
        '''
        if not hasattr(pyobj, self.attrs_aname):
            return

        if not isinstance(getattr(pyobj, self.attrs_aname), dict):
            raise TypeError,\
                'pyobj.%s must be a dictionary of names and values'\
                % self.attrs_aname

        for attr, value in getattr(pyobj, self.attrs_aname).items():
            namespaceURI,localName = None, attr
            if type(attr) in _seqtypes:
                namespaceURI, localName = attr

            what = None
            if getattr(self, 'attribute_typecode_dict', None) is not None:
                what = self.attribute_typecode_dict.get(attr)
                if what is None and namespaceURI is None:
                    what = self.attribute_typecode_dict.get(localName)

            if hasattr(value, 'typecode'):
                if what is not None and not isinstance(value.typecode, what):
                    raise EvaluateException, \
                        'self-describing attribute must subclass %s'\
                        %what.__class__

                what = value.typecode
                
            self.logger.debug("attribute create -- %s", value)
            if isinstance(what, QName):
                what.set_prefix(el, value)
            
            #format the data
            if what is None:
                value = str(value)
            else:
                value = what.get_formatted_content(value)

            el.setAttributeNS(namespaceURI, localName, value)

    def set_attribute_xsi_type(self, el, **kw):
        '''if typed, set the xsi:type attribute 
        '''
        if kw.get('typed', self.typed):
            namespaceURI,typeName = kw.get('type', _get_xsitype(self))
            if namespaceURI and typeName:
                self.logger.debug("attribute: (%s, %s)", namespaceURI, typeName)
                el.setAttributeType(namespaceURI, typeName)

    def set_attribute_href(self, el, objid):
        '''set href attribute
        '''
        el.setAttributeNS(None, 'href', "#%s" %objid)

    def set_attribute_id(self, el, objid):
        '''set id attribute
        '''
        if self.unique is False:
            el.setAttributeNS(None, 'id', "%s" %objid)

    def get_name(self, name, objid):
        n = name or self.pname or ('E' + objid)
        return n

    def has_attributes(self):
        '''Return True if Attributes are declared outside
        the scope of SOAP ('root', 'id', 'href'), and some
        attributes automatically handled (xmlns, xsi:type).
        '''
        if self.attribute_typecode_dict is None: return False
        return len(self.attribute_typecode_dict) > 0


class SimpleType(TypeCode):
    '''SimpleType -- consist exclusively of a tag, attributes, and a value
    '''

    def get_formatted_content(self, pyobj):
        raise NotImplementedError, 'method get_formatted_content is not implemented'

    def serialize_text_node(self, elt, sw, pyobj):
        '''Serialize without an element node.
        '''
        if pyobj is not None:
            text = self.get_formatted_content(pyobj)
            if type(text) not in _stringtypes:
                raise TypeError, 'pyobj must be a formatted string'

            textNode = elt.createAppendTextNode(text)

        return textNode

    def serialize(self, elt, sw, pyobj, name=None, orig=None, **kw):
        '''Handles the start and end tags, and attributes.  callout
        to get_formatted_content to get the textNode value.
            sw --
            pyobj -- processed content.
        '''
        objid = _get_object_id(pyobj)
        n = name or self.pname or ('E' + objid)

        # nillable
        el = elt.createAppendElement(self.nspname, n)
        if self.nillable is True and pyobj is None:
            self.serialize_as_nil(el)
            return None

        # other attributes
        self.set_attributes(el, pyobj)

        # soap href attribute
        unique = self.unique or kw.get('unique', False)
        if unique is False and sw.Known(orig or pyobj):
            self.set_attribute_href(el, objid)
            return None

        # xsi:type attribute 
        if kw.get('typed', self.typed) is True:
            self.set_attribute_xsi_type(el, **kw)

        # soap id attribute
        if self.unique is False:
            self.set_attribute_id(el, objid)

        #Content, <empty tag/>c
        if pyobj is not None:
            textNode = self.get_formatted_content(pyobj)
            if type(textNode) not in _stringtypes:
                raise TypeError, 'pyobj must be a formatted string'

            el.createAppendTextNode(textNode)

        return el


#XXX NOT FIXED YET
class Any(TypeCode):
    '''When the type isn't defined in the schema, but must be specified
    in the incoming operation.
        parsemap -- a type to class mapping (updated by descendants), for
                parsing
        serialmap -- same, for (outgoing) serialization
    '''
    parsemap, serialmap = {}, {}

    def __init__(self, pname=None, aslist=0, **kw):
        TypeCode.__init__(self, pname, **kw)
        self.aslist = aslist
        # If not derived, and optional isn't set, make us optional
        # so that None can be parsed.
        if self.__class__ == Any and not kw.has_key('optional'):
            self.optional = 1
        self.asarray = True
        self.unique = False

    # input arg v should be a list of tuples (name, value).
    def listify(self, v):
        if self.aslist: return [ k for j,k in v ]
        else: return dict(v)
        return v

    def parse_into_dict_or_list(self, elt, ps):
        c = _child_elements(elt)
        count = len(c)
        v = []
        if count == 0:
            href = _find_href(elt)
            if not href: return v
            elt = ps.FindLocalHREF(href, elt)
            self.checktype(elt, ps)
            c = _child_elements(elt)
            count = len(c)
            if count == 0: return self.listify(v)
        if self.nilled(elt, ps): return None

        for c_elt in c:
            # append (name,value) tuple to list
            v.append( (str(c_elt.nodeName), self.parse(c_elt, ps) ) )
        return self.listify(v)

    def parse(self, elt, ps):
        (ns,type) = self.checkname(elt, ps)
        if not type and self.nilled(elt, ps): return None
        if len(_children(elt)) == 0:
            href = _find_href(elt)
            if not href:
                if self.optional: return None
                raise EvaluateException('Non-optional Any missing',
                        ps.Backtrace(elt))
            elt = ps.FindLocalHREF(href, elt)
            (ns,type) = self.checktype(elt, ps)
        if not type and elt.namespaceURI == SOAP.ENC:
            ns,type = SOAP.ENC, elt.localName
        if not type or (ns,type) == (SOAP.ENC,'Array'):
            if self.aslist or _find_arraytype(elt):
                return [ self.__class__(aslist=self.aslist).parse(e, ps)
                            for e in _child_elements(elt) ]
            if len(_child_elements(elt)) == 0:
                raise EvaluateException("Any cannot parse untyped element",
                        ps.Backtrace(elt))
            return self.parse_into_dict_or_list(elt, ps)
        parser = Any.parsemap.get((ns,type))
        if not parser and _is_xsd_or_soap_ns(ns):
            parser = Any.parsemap.get((None,type))
        if not parser:
            raise EvaluateException('''Any can't parse element''',
                    ps.Backtrace(elt))
        return parser.parse(elt, ps)

    def get_formatted_content(self, pyobj):
        tc = type(pyobj)
        if tc == types.InstanceType:
            tc = pyobj.__class__
            if hasattr(pyobj, 'typecode'):
                serializer = pyobj.typecode.serialmap.get(tc)
            else:
                serializer = Any.serialmap.get(tc)
            if not serializer:
                tc = (types.ClassType, pyobj.__class__.__name__)
                serializer = Any.serialmap.get(tc)
        else:
            serializer = Any.serialmap.get(tc)
            if not serializer and isinstance(pyobj, time.struct_time):
                from ZSI.TCtimes import gDateTime
                serializer = gDateTime()
        if serializer:
            return serializer.get_formatted_content(pyobj)
        raise EvaluateException, 'Failed to find serializer for pyobj %s' %pyobj

    def serialize(self, elt, sw, pyobj, name=None, **kw):
        if hasattr(pyobj, 'typecode') and pyobj.typecode is not self:
            pyobj.typecode.serialize(elt, sw, pyobj, **kw)
            return

        objid = _get_object_id(pyobj)
        n = self.get_name(name, objid)

        kw['name'] = n
        tc = type(pyobj)
        self.logger.debug('Any serialize -- %s', tc)

        if tc in _seqtypes:
            if self.asarray:
                arrElt = elt.createAppendElement(self.nspname, n )
                arrElt.setAttributeNS(self.nspname, 'SOAP-ENC:arrayType', "xsd:anyType[" + str(len(pyobj)) + "]" )
                a = self.__class__() # instead of = Any()
                                     # since this is also used by AnyLax()
                for e in pyobj:
                    a.serialize(arrElt, sw, e, name='element')
            else:
                for o in pyobj:
                    serializer = self.__class__() # instead of =Any()
                    serializer.serialize(elt, sw, o, **kw)
            return
        elif tc == types.DictType:
            el = elt.createAppendElement(self.nspname, n)
            parentNspname = self.nspname # temporarily clear nspname for dict elements
            self.nspname = None
            for o,m in pyobj.items():
                subkw = dict(kw)
                if type(o) != types.StringType and type(o) != types.UnicodeType:
                    raise Exception, 'Dictionary implementation requires keys to be of type string (or unicode).' %pyobj
                subkw['name'] = o
                subkw.setdefault('typed', True)
                self.serialize(el, sw, m, **subkw)
            # restore nspname
            self.nspname = parentNspname
            return
                
        elif tc == types.InstanceType:
            tc = pyobj.__class__
            if hasattr(pyobj, 'typecode'):
                serializer = pyobj.typecode.serialmap.get(tc)
            else:
                serializer = Any.serialmap.get(tc)
            if not serializer:
                tc = (types.ClassType, pyobj.__class__.__name__)
                serializer = Any.serialmap.get(tc)
        else:
            serializer = Any.serialmap.get(tc)
            if not serializer and isinstance(pyobj, time.struct_time):
                from ZSI.TCtimes import gDateTime
                serializer = gDateTime()
        if not serializer:
            # Last-chance; serialize instances as dictionary
            if type(pyobj) != types.InstanceType:
                raise EvaluateException('''Any can't serialize ''' + \
                        repr(pyobj))
            self.serialize(elt, sw, pyobj.__dict__, **kw)
        else:
            # Try to make the element name self-describing
            tag = getattr(serializer, 'tag', None)
            if self.pname is not None:
                serializer.nspname = self.nspname
                serializer.pname = self.pname
                if "typed" not in kw:
                    kw['typed'] = False
            elif tag:
                if tag.find(':') == -1: tag = 'SOAP-ENC:' + tag
                kw['name'] = tag
                kw['typed'] = False
            serializer.unique = self.unique
            serializer.serialize(elt, sw, pyobj, **kw)
            # Reset TypeCode
            serializer.nspname = None
            serializer.pname = None


def RegisterType(C, clobber=0, *args, **keywords):
    instance = apply(C, args, keywords)
    for t in C.__dict__.get('parselist', []):
        prev = Any.parsemap.get(t)
        if prev:
            if prev.__class__ == C: continue
            if not clobber:
                raise TypeError(
                    str(C) + ' duplicating parse registration for ' + str(t))
        Any.parsemap[t] = instance
    for t in C.__dict__.get('seriallist', []):
        ti = type(t)
        if ti in [ types.TypeType, types.ClassType]:
            key = t
        elif ti in _stringtypes:
            key = (types.ClassType, t)
        else:
            raise TypeError(str(t) + ' is not a class name')
        prev = Any.serialmap.get(key)
        if prev:
            if prev.__class__ == C: continue
            if not clobber:
                raise TypeError(
                    str(C) + ' duplicating serial registration for ' + str(t))
        Any.serialmap[key] = instance

def _DynamicImport(moduleName, className):
    '''
    Utility function for RegisterTypeWithSchemaAndClass
    '''
    mod = __import__(moduleName)
    components = moduleName.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return getattr(mod, className)

def _RegisterTypeWithSchemaAndClass(importedSchemaTypes, schemaTypeName, classModuleName, className, generatedClassSuffix="_"):
    '''
    Used by RegisterGeneratedTypesWithMapping.
    Helps register classes so they can be serialized and parsed as "any".
    Register a type by providing its schema and class.  This allows
       Any and AnyType to reconstruct objects made up of your own classes.
       Note: The class module should be able to be imported (by being in your
       pythonpath).  Your classes __init__ functions shoud have default arguments
       for all extra parameters.
    Example of use:
        import SchemaToPyTypeMap # Mapping written by you.  Also used with wsdl2py -m
             # mapping = {"SomeDescription" : ("Descriptions", "SomeDescription"),
             #          #  schemaTypeName       :  moduleName    ,  className 
        # The module on the next line is generated by wsdl2py
        from EchoServer_services_types import urn_ZSI_examples as ExampleTypes

        for key,value in SchemaToPyTypeMap.mapping.items():
        ZSI.TC.RegisterTypeWithSchemaAndClass(importedSchemaTypes = ExampleTypes, schemaTypeName=key, classModuleName=value[0], className=value[1])


    '''
    # Doing this: (schemaTypeName="ExampleTypes", classModuleName="Description",
    #               className="SomeDescription")
    # sd_instance = ExampleTypes.SomeDescription_(pname="SomeDescription")
    # Any.serialmap[Descriptions.SomeDescription] = sd_instance
    # Any.parsemap[(None,'SomeDescription')] = sd_instance
    classDef = _DynamicImport(classModuleName, className)
    interfaceDef = getattr(importedSchemaTypes, schemaTypeName + generatedClassSuffix)

    instance = interfaceDef(pname=className)
    Any.serialmap[classDef] = instance
    Any.parsemap[(None,schemaTypeName)] = instance

def RegisterGeneratedTypesWithMapping(generatedTypes, mapping, generatedClassSuffix="_"):
    """
    Helps register your classes so they can be serialized and parsed as "any".
        generatedTypes is a class containing typecode classes generated by zsi.
        mapping is a dictionary that maps {schemaTypeName : moduleName,  className}
            and is also used with wsdl2py -m

    Example of use:
        import SchemaToPyTypeMap      # See RegisterTypeWithSchemaAndClass for description
        # The module on the next line is generated by wsdl2py and contains generated typecodes.
        from EchoServer_services_types import urn_ZSI_examples as ExampleTypes
        ZSI.TC.RegisterGeneratedTypesWithMapping(generatedTypes = ExampleTypes, mapping=SchemaToPyTypeMap.mapping)
    """
    for key,value in mapping.items():
        _RegisterTypeWithSchemaAndClass(importedSchemaTypes = generatedTypes, schemaTypeName=key, classModuleName=value[0], className=value[1], generatedClassSuffix=generatedClassSuffix)


class String(SimpleType):
    '''A string type.
    '''
    parselist = [ (None,'string') ]
    seriallist = [ types.StringType, types.UnicodeType ]
    type = (SCHEMA.XSD3, 'string')

    def __init__(self, pname=None, strip=1, **kw):
        TypeCode.__init__(self, pname, **kw)
        if kw.has_key('resolver'): self.resolver = kw['resolver']
        self.strip = strip

    def text_to_data(self, text):
        '''convert text into typecode specific data.
        '''
        if self.strip: text = text.strip()
        if self.pyclass is not None:
            return self.pyclass(text)    
        return text

    def parse(self, elt, ps):
        self.checkname(elt, ps)
        if len(_children(elt)) == 0:
            href = _find_href(elt)
            if not href:
                if self.nilled(elt, ps) is False:
                    # No content, no HREF, not NIL:  empty string
                    return ""
                # No content, no HREF, and is NIL...
                if self.minOccurs == 0 or self.nillable is True: 
                    return None
                raise EvaluateException('Non-optional string missing',
                        ps.Backtrace(elt))
            if href[0] != '#':
                return ps.ResolveHREF(href, self)
            elt = ps.FindLocalHREF(href, elt)
            self.checktype(elt, ps)
        if self.nilled(elt, ps): return None
        if len(_children(elt)) == 0: return ''
        v = self.simple_value(elt, ps)
        return self.text_to_data(v)

    def get_formatted_content(self, pyobj):
        if type(pyobj) not in _stringtypes:
            pyobj = str(pyobj)
        if type(pyobj) == types.UnicodeType: pyobj = pyobj.encode('utf-8')
        return pyobj


class URI(String):
    '''A URI.
    '''
    parselist = [ (None,'anyURI'),(SCHEMA.XSD3, 'anyURI')]
    type = (SCHEMA.XSD3, 'anyURI')

    def parse(self, elt, ps):
        val = String.parse(self, elt, ps)
        return urldecode(val)

    def get_formatted_content(self, pyobj):
        pyobj = String.get_formatted_content(self, pyobj)
        return urlencode(pyobj)



class QName(String):
    '''A QName type
    '''
    parselist = [ (None,'QName') ]
    type = (SCHEMA.XSD3, 'QName')

    def __init__(self, pname=None, strip=1, **kw):
        String.__init__(self, pname, strip, **kw)
        self.prefix = None

    def get_formatted_content(self, pyobj):
        value = pyobj
        if isinstance(pyobj, tuple):
            namespaceURI,localName = pyobj
            if self.prefix is not None:
                value = "%s:%s" %(self.prefix,localName)
        return String.get_formatted_content(self, value)

    def set_prefix(self, elt, pyobj):
        '''use this method to set the prefix of the QName,
        method looks in DOM to find prefix or set new prefix.
        This method must be called before get_formatted_content.
        '''
        if isinstance(pyobj, tuple):
            namespaceURI,localName = pyobj
            self.prefix = elt.getPrefix(namespaceURI)

    def parse(self, elt, ps):
        '''Since this typecode parses value first as a string, and then
        interprets it as a tuple must trick String.parse to not package
        up in pyclass tuple class.
        '''
        pyclass = self.pyclass
        if self.pyclass is not None:
            self.pyclass = None

        val = String.parse(self, elt, ps)
        self.pyclass = pyclass
        prefix,localName = SplitQName(val)
        nsdict = ps.GetElementNSdict(elt)
        try:
            namespaceURI = nsdict[prefix]
        except KeyError, ex:
            raise EvaluateException, 'cannot resolve prefix(%s)'%prefix
        v = (namespaceURI,localName)
        if self.pyclass is not None and self.__class__ is QName:
            return self.pyclass(v)    
        return v

    def serialize(self, elt, sw, pyobj, name=None, orig=None, **kw):
        '''pyobj -- qualifiedName or (namespaceURI,elementName) tuple
        '''
        self.set_prefix(elt, pyobj)
        String.serialize(self, elt, sw, pyobj, name, orig, **kw)

    def serialize_text_node(self, elt, sw, pyobj):
        '''Serialize without an element node.
        '''
        self.set_prefix(elt, pyobj)
        if pyobj is not None:
            text = self.get_formatted_content(pyobj)
            if type(text) not in _stringtypes:
                raise TypeError, 'pyobj must be a formatted string'
            textNode = elt.createAppendTextNode(text)
        return textNode


class Token(String):
    '''an xsd:token type
    '''
    parselist = [ (None, 'token') ]
    type = (SCHEMA.XSD3, 'token')

    def parse(self, elt, ps):
        v = String.parse(self, elt, ps)
        if self.pyclass is not None and self.__class__ is Token:
            return self.pyclass(v)    
        return v


class Base64String(String):
    '''A Base64 encoded string.
    '''
    parselist = [ (None,'base64Binary'), (SOAP.ENC, 'base64') ]
    type = (SOAP.ENC, 'base64')

    def parse(self, elt, ps):
        val = String.parse(self, elt, ps)
        v = b64decode(val.replace(' ', '').replace('\n','').replace('\r',''))

        if self.pyclass is not None and self.__class__ is Base64String:
            return self.pyclass(v) 
        return v

    def get_formatted_content(self, pyobj):
        pyobj = '\n' + b64encode(pyobj)
        return String.get_formatted_content(self, pyobj)


class Base64Binary(String):
    parselist = [ (None,'base64Binary'), ]
    type = (SCHEMA.XSD3, 'base64Binary')

    def parse(self, elt, ps):
        val = String.parse(self, elt, ps)
        if val is None: 
            if self.nillable is True: return None
            raise EvaluateException, "Base64Binary (%s,%s) is not nillable" %(self.nspname,self.pname)

        v = b64decode(val)
        if self.pyclass is not None and self.__class__ is Base64String:
            return self.pyclass(v) 
        return v

    def get_formatted_content(self, pyobj):
        pyobj = b64encode(pyobj).strip()
        #return String.get_formatted_content(self, pyobj)
        return pyobj


class HexBinaryString(String):
    '''Hex-encoded binary (yuk).
    '''
    parselist = [ (None,'hexBinary') ]
    type = (SCHEMA.XSD3, 'hexBinary')

    def parse(self, elt, ps):
        val = String.parse(self, elt, ps)
        v = hexdecode(val)

        if self.pyclass is not None and self.__class__ is Base64String:
            return self.pyclass(v) 
        return v

    def get_formatted_content(self, pyobj):
        pyobj = hexencode(pyobj).upper()
        return String.get_formatted_content(self, pyobj)


class XMLString(String):
    '''A string that represents an XML document
    '''

    def __init__(self, pname=None, readerclass=None, **kw):
        String.__init__(self, pname, **kw)
        self.readerclass = readerclass

    def parse(self, elt, ps):
        if not self.readerclass:
            from xml.dom.ext.reader import PyExpat
            self.readerclass = PyExpat.Reader
        v = String.parse(self, elt, ps)
        return self.readerclass().fromString(v)

    def get_formatted_content(self, pyobj):
        pyobj = Canonicalize(pyobj)
        return String.get_formatted_content(self, pyobj)


class Enumeration(String):
    '''A string type, limited to a set of choices.
    '''

    def __init__(self, choices, pname=None, **kw):
        String.__init__(self, pname, **kw)
        t = type(choices)
        if t in _seqtypes:
            self.choices = tuple(choices)
        elif TypeCode.typechecks:
            raise TypeError(
                'Enumeration choices must be list or sequence, not ' + str(t))
        if TypeCode.typechecks:
            for c in self.choices:
                if type(c) not in _stringtypes:
                    raise TypeError(
                        'Enumeration choice ' + str(c) + ' is not a string')

    def parse(self, elt, ps):
        val = String.parse(self, elt, ps)
        if val not in self.choices:
            raise EvaluateException('Value not in enumeration list',
                    ps.Backtrace(elt))
        return val


# This is outside the Integer class purely for code esthetics.
_ignored = []

class Integer(SimpleType):
    '''Common handling for all integers.
    '''

    ranges = {
        'unsignedByte':         (0, 255),
        'unsignedShort':        (0, 65535),
        'unsignedInt':          (0, 4294967295L),
        'unsignedLong':         (0, 18446744073709551615L),

        'byte':                 (-128, 127),
        'short':                (-32768, 32767),
        'int':                  (-2147483648L, 2147483647),
        'long':                 (-9223372036854775808L, 9223372036854775807L),

        'negativeInteger':      (_ignored, -1),
        'nonPositiveInteger':   (_ignored, 0),
        'nonNegativeInteger':   (0, _ignored),
        'positiveInteger':      (1, _ignored),

        'integer':              (_ignored, _ignored)
    }
    parselist = [ (None,k) for k in ranges.keys() ]
    seriallist = [ types.IntType, types.LongType ]

    def __init__(self, pname=None, format='%d', **kw):
        TypeCode.__init__(self, pname, **kw)
        self.format = format

    def text_to_data(self, text):
        '''convert text into typecode specific data.
        '''
        if self.pyclass is not None:
            v = self.pyclass(text) 
        else:
            try:
                v = int(text)
            except:
                try:
                    v = long(text)
                except:
                    raise EvaluateException('Unparseable integer',
                        ps.Backtrace(elt))
        return v

    def parse(self, elt, ps):
        (ns,type) = self.checkname(elt, ps)
        if self.nilled(elt, ps): return None
        elt = self.SimpleHREF(elt, ps, 'integer')
        if not elt: return None

        if type is None:
           type = self.type[1] 
        elif self.type[1] is not None and type != self.type[1]:
            raise EvaluateException('Integer type mismatch; ' \
                'got %s wanted %s' % (type,self.type[1]), ps.Backtrace(elt))
        
        v = self.simple_value(elt, ps)
        v = self.text_to_data(v)

        (rmin, rmax) = Integer.ranges.get(type, (_ignored, _ignored))
        if rmin != _ignored and v < rmin:
            raise EvaluateException('Underflow, less than ' + repr(rmin),
                    ps.Backtrace(elt))
        if rmax != _ignored and v > rmax:
            raise EvaluateException('Overflow, greater than ' + repr(rmax),
                    ps.Backtrace(elt))
        return v

    def get_formatted_content(self, pyobj):
        return self.format %pyobj



# See credits, below.
def _make_inf():
    x = 2.0
    x2 = x * x
    i = 0
    while i < 100 and x != x2:
        x = x2
        x2 = x * x
        i = i + 1
    if x != x2:
        raise ValueError("This machine's floats go on forever!")
    return x

# This is outside the Decimal class purely for code esthetics.
_magicnums = { }
try:
    _magicnums['INF'] = float('INF')
    _magicnums['-INF'] = float('-INF')
except:
    _magicnums['INF'] = _make_inf()
    _magicnums['-INF'] = -_magicnums['INF']

# The following comment and code was written by Tim Peters in
# article <001401be92d2$09dcb800$5fa02299@tim> in comp.lang.python,
# also available at the following URL:
# http://groups.google.com/groups?selm=001401be92d2%2409dcb800%245fa02299%40tim
# Thanks, Tim!

# NaN-testing.
#
# The usual method (x != x) doesn't work.
# Python forces all comparisons thru a 3-outcome cmp protocol; unordered
# isn't a possible outcome.  The float cmp outcome is essentially defined
# by this C expression (combining some cross-module implementation
# details, and where px and py are pointers to C double):
#   px == py ? 0 : *px < *py ? -1 : *px > *py ? 1 : 0
# Comparing x to itself thus always yields 0 by the first clause, and so
# x != x is never true.
# If px and py point to distinct NaN objects, a strange thing happens:
# 1. On scrupulous 754 implementations, *px < *py returns false, and so
#    does *px > *py.  Python therefore returns 0, i.e. "equal"!
# 2. On Pentium HW, an unordered outcome sets an otherwise-impossible
#    combination of condition codes, including both the "less than" and
#    "equal to" flags.  Microsoft C generates naive code that accepts
#    the "less than" flag at face value, and so the *px < *py clause
#    returns true, and Python returns -1, i.e. "not equal".
# So with a proper C 754 implementation Python returns the wrong result,
# and under MS's improper 754 implementation Python yields the right
# result -- both by accident.  It's unclear who should be shot <wink>.
#
# Anyway, the point of all that was to convince you it's tricky getting
# the right answer in a portable way!
def isnan(x):
    """x -> true iff x is a NaN."""
    # multiply by 1.0 to create a distinct object (x < x *always*
    # false in Python, due to object identity forcing equality)
    if x * 1.0 < x:
        # it's a NaN and this is MS C on a Pentium
        return 1
    # Else it's non-NaN, or NaN on a non-MS+Pentium combo.
    # If it's non-NaN, then x == 1.0 and x == 2.0 can't both be true,
    # so we return false.  If it is NaN, then assuming a good 754 C
    # implementation Python maps both unordered outcomes to true.
    return 1.0 == x and x == 2.0


class Decimal(SimpleType):
    '''Parent class for floating-point numbers.
    '''

    parselist = [ (None,'decimal'), (None,'float'), (None,'double') ]
    seriallist = _floattypes
    type = None
    ranges =  {
        'float': ( 7.0064923216240861E-46,
                        -3.4028234663852886E+38, 3.4028234663852886E+38 ),
        'double': ( 2.4703282292062327E-324,
                        -1.7976931348623158E+308, 1.7976931348623157E+308),
    }
    zeropat = re.compile('[1-9]')

    def __init__(self, pname=None, format='%f', **kw):
        TypeCode.__init__(self, pname, **kw)
        self.format = format


    def text_to_data(self, text):
        '''convert text into typecode specific data.
        '''
        v = text
        if self.pyclass is not None:
            return self.pyclass(v)

        m = _magicnums.get(v)
        if m: return m

        try:
            return float(v)
        except:
            raise EvaluateException('Unparseable floating point number')

    def parse(self, elt, ps):
        (ns,type) = self.checkname(elt, ps)
        elt = self.SimpleHREF(elt, ps, 'floating-point')
        if not elt: return None
        tag = getattr(self.__class__, 'type')
        if tag:
            if type is None:
                type = tag
            elif tag != (ns,type):
                raise EvaluateException('Floating point type mismatch; ' \
                        'got (%s,%s) wanted %s' % (ns,type,tag), ps.Backtrace(elt))
        # Special value?
        if self.nilled(elt, ps): return None
        v = self.simple_value(elt, ps)
        try:
            fp = self.text_to_data(v)
        except EvaluateException, ex:
            ex.args.append(ps.Backtrace(elt))
            raise ex
   
        m = _magicnums.get(v)
        if m: 
            return m

        if str(fp).lower() in [ 'inf', '-inf', 'nan', '-nan' ]:
            raise EvaluateException('Floating point number parsed as "' + \
                    str(fp) + '"', ps.Backtrace(elt))
        if fp == 0 and Decimal.zeropat.search(v):
            raise EvaluateException('Floating point number parsed as zero',
                    ps.Backtrace(elt))
        (rtiny, rneg, rpos) = Decimal.ranges.get(type, (None, None, None))
        if rneg and fp < 0 and fp < rneg:
            raise EvaluateException('Negative underflow', ps.Backtrace(elt))
        if rtiny and fp > 0 and fp < rtiny:
            raise EvaluateException('Positive underflow', ps.Backtrace(elt))
        if rpos and fp > 0 and fp > rpos:
            raise EvaluateException('Overflow', ps.Backtrace(elt))
        return fp

    def get_formatted_content(self, pyobj):
        if pyobj == _magicnums['INF']:
            return 'INF'
        elif pyobj == _magicnums['-INF']:
            return '-INF'
        elif isnan(pyobj):
            return 'NaN'
        else:
            return self.format %pyobj


class Boolean(SimpleType):
    '''A boolean.
    '''

    parselist = [ (None,'boolean') ]
    seriallist = [ bool ]
    type = (SCHEMA.XSD3, 'boolean')

    def text_to_data(self, text):
        '''convert text into typecode specific data.
        '''
        v = text
        if v == 'false': 
            if self.pyclass is None:
                return False
            return self.pyclass(False)

        if v == 'true': 
            if self.pyclass is None:
                return True
            return self.pyclass(True)

        try:
            v = int(v)
        except:
            try:
                v = long(v)
            except:
                raise EvaluateException('Unparseable boolean',
                    ps.Backtrace(elt))

        if v:
            if self.pyclass is None:
                return True
            return self.pyclass(True)

        if self.pyclass is None:
             return False
        return self.pyclass(False)

    def parse(self, elt, ps):
        self.checkname(elt, ps)
        elt = self.SimpleHREF(elt, ps, 'boolean')
        if not elt: return None
        if self.nilled(elt, ps): return None

        v = self.simple_value(elt, ps).lower()
        return self.text_to_data(v)

    def get_formatted_content(self, pyobj):
        if pyobj: return 'true'
        return 'false'


#XXX NOT FIXED YET
class XML(TypeCode):
    '''Opaque XML which shouldn't be parsed.
        comments -- preserve comments
        inline -- don't href/id when serializing
        resolver -- object to resolve href's
        wrapped -- put a wrapper element around it
    '''

    # Clone returned data?
    copyit = 0

    def __init__(self, pname=None, comments=0, inline=0, wrapped=True, **kw):
        TypeCode.__init__(self, pname, **kw)
        self.comments = comments
        self.inline = inline
        if kw.has_key('resolver'): self.resolver = kw['resolver']
        self.wrapped = wrapped
        self.copyit = kw.get('copyit', XML.copyit)

    def parse(self, elt, ps):
        if self.wrapped is False:
            return elt
        c = _child_elements(elt)
        if not c:
            href = _find_href(elt)
            if not href:
                if self.minOccurs == 0: return None
                raise EvaluateException('Embedded XML document missing',
                        ps.Backtrace(elt))
            if href[0] != '#':
                return ps.ResolveHREF(href, self)
            elt = ps.FindLocalHREF(href, elt)
            c = _child_elements(elt)
        if _find_encstyle(elt) != "":
            #raise EvaluateException('Embedded XML has unknown encodingStyle',
            #       ps.Backtrace(elt)
            pass
        if len(c) != 1:
            raise EvaluateException('Embedded XML has more than one child',
                    ps.Backtrace(elt))
        if self.copyit: return c[0].cloneNode(1)
        return c[0]

    def serialize(self, elt, sw, pyobj, name=None, unsuppressedPrefixes=[], **kw):
        if self.wrapped is False:
            Canonicalize(pyobj, sw, unsuppressedPrefixes=unsuppressedPrefixes,
                comments=self.comments)
            return
        objid = _get_object_id(pyobj)
        n = name or self.pname or ('E' + objid)
        xmlelt = elt.createAppendElement(self.nspname, n)

        if type(pyobj) in _stringtypes:
            self.set_attributes(xmlelt, pyobj)
            self.set_attribute_href(xmlelt, objid)
        elif kw.get('inline', self.inline):
            self.cb(xmlelt, sw, pyobj, unsuppressedPrefixes)
        else:
            self.set_attributes(xmlelt, pyobj)
            self.set_attribute_href(xmlelt, objid)
            sw.AddCallback(self.cb, pyobj, unsuppressedPrefixes)

    def cb(self, elt, sw, pyobj, unsuppressedPrefixes=[]):
        if sw.Known(pyobj): return
        objid = _get_object_id(pyobj)
        n = self.pname or ('E' + objid)

        xmlelt = elt.createAppendElement(self.nspname, n)
        self.set_attribute_id(xmlelt, objid)
        xmlelt.setAttributeNS(SOAP.ENC, 'encodingStyle', '""')
        Canonicalize(pyobj, sw, unsuppressedPrefixes=unsuppressedPrefixes,
            comments=self.comments)

# Base class for AnyStrict and AnyLax
class AnyConcrete(Any):
    ''' Base class for handling unspecified types when using concrete schemas.
    '''
    def __init__(self, pname=None, aslist=False, **kw):
        TypeCode.__init__(self, pname, **kw)
        self.aslist = aslist
        self.asarray = False  # don't use arrayType
        self.unique = True # don't print id
        self.optional = kw.get('optional', True) # Any constructor is not called


class AnyStrict(AnyConcrete):
    ''' Handles an unspecified types when using a concrete schemas and
          processContents = "strict".
    '''
    def __init__(self, pname=None, aslist=False, **kw):
        AnyConcrete.__init__(self, pname=pname, aslist=aslist, **kw)

    def serialize(self, elt, sw, pyobj, name=None, **kw):
        tc = type(pyobj)
        if tc == types.DictType and not self.aslist:
            raise EvaluateException, 'Serializing dictionaries not implemented when processContents=\"strict\".  Try as a list or use processContents=\"lax\".'
        else:

            AnyConcrete.serialize(self, elt=elt,sw=sw,pyobj=pyobj,name=name, **kw)

class AnyLax(AnyConcrete):
    ''' Handles unspecified types when using a concrete schemas and
          processContents = "lax".
    '''
    def __init__(self, pname=None, aslist=False, **kw):
        AnyConcrete.__init__(self, pname=pname, aslist=aslist, **kw)

    def parse_into_dict_or_list(self, elt, ps):
        c = _child_elements(elt)
        count = len(c)
        v = []
        if count == 0:
            href = _find_href(elt)
            if not href: return {}
            elt = ps.FindLocalHREF(href, elt)
            self.checktype(elt, ps)
            c = _child_elements(elt)
            count = len(c)
            if count == 0: return self.listify([])
        if self.nilled(elt, ps): return None

        # group consecutive elements with the same name together
        #   We treat consecutive elements with the same name as lists.
        groupedElements = []  # tuples of (name, elementList)
        previousName = ""
        currentElementList = None
        for ce in _child_elements(elt):
            name = ce.nodeName
            if (name != previousName): # new name, so new group
                if currentElementList != None: # store previous group if there is one
                    groupedElements.append( (previousName, currentElementList) )
                currentElementList = list() 
            currentElementList.append(ce) # append to list
            previousName = name
        # add the last group if necessary
        if currentElementList != None: # store previous group if there is one
            groupedElements.append( (previousName, currentElementList) )

        # parse the groups of names 
        if len(groupedElements) < 1: # should return earlier
            return None 
        # return a list if there is one name and multiple data
        elif (len(groupedElements) == 1) and (len(groupedElements[0][0]) > 1):
            self.aslist = 0
        # else return a dictionary

        for name,eltList in groupedElements:
            lst = []
            for elt in eltList:
                #aslist = self.aslist 
                lst.append( self.parse(elt, ps) )
                #self.aslist = aslist # restore the aslist setting
            if len(lst) > 1:  # consecutive elements with the same name means a list
                v.append( (name, lst) )
            elif len(lst) == 1: 
                v.append( (name, lst[0]) )

        return self.listify(v)

    def checkname(self, elt, ps):
        '''See if the name and type of the "elt" element is what we're
        looking for.   Return the element's type.
        Since this is AnyLax, it's ok if names don't resolve.
        '''

        parselist,errorlist = self.get_parse_and_errorlist()
        ns, name = _get_element_nsuri_name(elt)
        if ns == SOAP.ENC:
            # Element is in SOAP namespace, so the name is a type.
            if parselist and \
            (None, name) not in parselist and (ns, name) not in parselist:
                raise EvaluateException(
                'Element mismatch (got %s wanted %s) (SOAP encoding namespace)' % \
                        (name, errorlist), ps.Backtrace(elt))
            return (ns, name)

        # Not a type, check name matches.
        if self.nspname and ns != self.nspname:
            raise EvaluateException('Element NS mismatch (got %s wanted %s)' % \
                (ns, self.nspname), ps.Backtrace(elt))

        #if self.pname and name != self.pname:
        #   this is ok since names don't need to be resolved with AnyLax

        return self.checktype(elt, ps)

class AnyType(TypeCode):
    """XML Schema xsi:anyType type definition wildCard.
       class variables: 
          all -- specifies use of all namespaces.
          other -- specifies use of other namespaces
          type --
    """
    all = '#all'
    other = '#other'
    type = (SCHEMA.XSD3, 'anyType')

    def __init__(self, namespaces=['#all'],pname=None, 
    minOccurs=1, maxOccurs=1, strip=1, **kw):
        TypeCode.__init__(self, pname=pname, minOccurs=minOccurs, maxOccurs=maxOccurs, **kw)
        self.namespaces = namespaces

    def serialize(self, elt, sw, pyobj, **kw):
        nsuri,typeName = _get_xsitype(pyobj)
        if self.all not in self.namespaces and nsuri not in self.namespaces:
            raise EvaluateException, '<anyType> unsupported use of namespaces %s' %self.namespaces
        what = pyobj
        if hasattr(what, 'typecode'):
            what = pyobj.typecode
        elif not isinstance(what, TypeCode):
            #May want to look thru containers and try to find a match
            #raise EvaluateException, '<anyType> pyobj must be self-describing.'
            what = AnyStrict(pname=(self.nspname,self.pname), aslist=False)
            kw['typed'] = True
            what.serialize(elt, sw, pyobj, **kw)
            return

        # Namespace if element AnyType was namespaced.
        if self.nspname != what.nspname:
            what.nspname = self.nspname

        if self.pname != what.pname:
            raise EvaluateException, \
                'element name of typecode(%s) must match element name of AnyType(%s)' \
                %(what.pname,self.pname)

        what.serialize(elt, sw, pyobj, **kw)

    def parse(self, elt, ps):
        #element name must be declared ..
        nspname,pname = _get_element_nsuri_name(elt)
        if nspname != self.nspname or pname != self.pname:
            raise EvaluateException, '<anyType> instance is (%s,%s) found (%s,%s)'\
                %(self.nspname,self.pname,nspname,pname)

        #locate xsi:type
        prefix, typeName = SplitQName(_find_type(elt))
        namespaceURI = _resolve_prefix(elt, prefix)
        pyclass = _get_type_definition(namespaceURI, typeName)
        if not pyclass:
            if _is_xsd_or_soap_ns(namespaceURI):
                pyclass = AnyStrict
            elif (str(namespaceURI).lower()==str(Apache.Map.type[0]).lower())\
                and (str(typeName).lower() ==str(Apache.Map.type[1]).lower()):
                pyclass = Apache.Map
            else:
                # Unknown type, so parse into a dictionary
                pyobj = Any().parse_into_dict_or_list(elt, ps)
                return pyobj
                    
        what = pyclass(pname=(self.nspname,self.pname))
        pyobj = what.parse(elt, ps)
        return pyobj


class AnyElement(AnyType):
    """XML Schema xsi:any element declaration wildCard.
       class variables: 
            tag -- global element declaration
    """
    tag = (SCHEMA.XSD3, 'any')

    def __init__(self, namespaces=['#all'],pname=None, 
    minOccurs=1, maxOccurs=1, strip=1, processContents='strict',**kw):
        self.processContents = processContents
        AnyType.__init__(self, namespaces=namespaces,pname=pname,
            minOccurs=minOccurs, maxOccurs=maxOccurs, strip=strip, **kw)

    def getProcessContents(self, processContents):
        return self._processContents
    def setProcessContents(self, processContents):
        if processContents not in ('lax', 'skip', 'strict'):
            raise EvaluateException, '<any> processContents(%s) is not understood.' %processContents
        self._processContents = processContents
    processContents = property(getProcessContents, setProcessContents, None, '<any> processContents')
       
    def serialize(self, elt, sw, pyobj, **kw):
        '''Must provice typecode to AnyElement for serialization, else
        try to use TC.Any to serialize instance which will serialize 
        based on the data type of pyobj w/o reference to XML schema 
        instance.
        '''
        what = None
        if hasattr(pyobj, 'typecode'):
            what = getattr(pyobj, 'typecode')
            #May want to look thru containers and try to find a match
        elif type(pyobj) == types.InstanceType:
            tc = pyobj.__class__
            what = Any.serialmap.get(tc)
            if not what:
                tc = (types.ClassType, pyobj.__class__.__name__)
                what = Any.serialmap.get(tc)
        if what == None:
            if isinstance(pyobj, TypeCode):
                raise EvaluateException, '<any> pyobj is a typecode instance.'
            #elif type(pyobj) in (list,tuple,dict):
            #    raise EvaluateException, '<any> can\'t serialize pyobj %s' \
            #        %type(pyobj)
            elif kw.has_key('pname'):
                if self.processContents=='lax':
                    what = AnyLax(pname=(kw.get('nspname'),kw['pname']))
                else:
                    what = AnyStrict(pname=(kw.get('nspname'),kw['pname']))
            else:
                if self.processContents=='lax':
                    what = AnyLax()
                else:
                    what = AnyStrict()
        self.logger.debug('AnyElement.serialize with %s', what.__class__.__name__)
        what.serialize(elt, sw, pyobj, **kw)

    def parse(self, elt, ps):
        '''
        processContents -- 'lax' | 'skip' | 'strict', 'strict'
        1) if 'skip' check namespaces, and return the DOM node.
        2) if 'lax' look for declaration, or definition.  If
           not found return DOM node.
        3) if 'strict' get declaration, or raise.
        '''
        nspname,pname = _get_element_nsuri_name(elt)
        pyclass = _get_global_element_declaration(nspname, pname)
        if pyclass is None:
            # if self.processContents == 'strict': raise
            # Allow use of "<any>" element declarations w/ local element declarations
            prefix, typeName = SplitQName(_find_type(elt))
            if typeName:
                namespaceURI = _resolve_prefix(elt, prefix or 'xmlns')
                # First look thru user defined namespaces, if don't find
                # look for 'primitives'.
                pyclass = _get_type_definition(namespaceURI, typeName)
                if pyclass is None:
                    if not _is_xsd_or_soap_ns(namespaceURI):
                        raise EvaluateException, '<any> cant find typecode for type (%s,%s)'\
                            %(namespaceURI,typeName)
                    if self.getProcessContents=='lax':
                        pyclass = AnyLax
                    else:
                        pyclass = AnyStrict

                what = pyclass(pname=(nspname,pname))
                pyobj = what.parse(elt, ps)
                try:
                    pyobj.typecode = what
                except AttributeError, ex:
                    # Assume this means builtin type.
                    pyobj = Wrap(pyobj, what)
            else:
                if self.processContents == 'lax':
                    what = AnyLax(pname=(nspname,pname))
                else: # processContents == 'skip'
                    # All else fails, not typed, attempt to use XML, String
                    what = XML(pname=(nspname,pname), wrapped=False)
                try:
                    pyobj = what.parse(elt, ps)
                except EvaluateException, ex:
                    self.logger.error("Give up, parse (%s,%s) as a String", what.nspname, what.pname)
                    # Try returning "elt"
                    what = String(pname=(nspname,pname))
                    pyobj = Wrap(what.parse(elt, ps), what)
        else:
            what = pyclass()
            pyobj = what.parse(elt, ps)
            try:
                pyobj.typecode = what
            except AttributeError, ex:
                # Assume this means builtin type.
                pyobj = _GetPyobjWrapper.Wrap(pyobj, what)

        return pyobj


class Union(SimpleType):
    '''simpleType Union

    class variables:
        memberTypes -- list [(namespace,name),] tuples, each representing a type defintion.
    '''
    memberTypes = None

    def __init__(self, pname=None, minOccurs=1, maxOccurs=1, **kw):
        SimpleType.__init__(self, pname=pname, minOccurs=minOccurs, maxOccurs=maxOccurs, **kw)
        self.memberTypeCodes = []

    def setMemberTypeCodes(self):
        if len(self.memberTypeCodes) > 0: 
            return
        if self.__class__.memberTypes is None:
            raise EvaluateException, 'uninitialized class variable memberTypes [(namespace,name),]'
        for nsuri,name in self.__class__.memberTypes:
            pyclass = _get_type_definition(nsuri,name)
            if pyclass is None:
                tc = Any.parsemap.get((nsuri,name))
                typecode = tc.__class__(pname=(self.nspname,self.pname))
            else:
                typecode = pyclass(pname=(self.nspname,self.pname))

            if typecode is None:
                raise EvaluateException, \
                    'Typecode class for Union memberType (%s,%s) is missing' %(nsuri,name)
            if isinstance(typecode, Struct):
                raise EvaluateException, \
                    'Illegal: Union memberType (%s,%s) is complexType' %(nsuri,name)
            self.memberTypeCodes.append(typecode)

    def parse(self, elt, ps, **kw):
        '''attempt to parse sequentially.  No way to know ahead of time
        what this instance represents.  Must be simple type so it can
        not have attributes nor children, so this isn't too bad.
        '''
        self.setMemberTypeCodes()
        (nsuri,typeName) = self.checkname(elt, ps)

        #if (nsuri,typeName) not in self.memberTypes:
        #    raise EvaluateException(
        #            'Union Type mismatch got (%s,%s) not in %s' % \
        #            (nsuri, typeName, self.memberTypes), ps.Backtrace(elt))

        for indx in range(len(self.memberTypeCodes)):
            typecode = self.memberTypeCodes[indx]
            try:
                pyobj = typecode.parse(elt, ps)
            except ParseException, ex:
                continue
            except Exception, ex:
                continue

            if indx > 0:
                self.memberTypeCodes.remove(typecode)
                self.memberTypeCodes.insert(0, typecode)
            break

        else:
            raise

        return pyobj

    def get_formatted_content(self, pyobj, **kw): 
        self.setMemberTypeCodes()
        for indx in range(len(self.memberTypeCodes)):
            typecode = self.memberTypeCodes[indx]
            try:
                content = typecode.get_formatted_content(copy.copy(pyobj))
                break
            except ParseException, ex:
                pass

            if indx > 0:
                self.memberTypeCodes.remove(typecode)
                self.memberTypeCodes.insert(0, typecode)

        else:
            raise

        return content


class List(SimpleType):
    '''simpleType List
    Class data:
        itemType -- sequence (namespaceURI,name) or a TypeCode instance
            representing the type definition
    '''
    itemType = None

    def __init__(self, pname=None, itemType=None, **kw):
        '''Currently need to require maxOccurs=1, so list
        is interpreted as a single unit of data.
        '''
        assert kw.get('maxOccurs',1) == 1, \
            'Currently only supporting SimpleType Lists with  maxOccurs=1'

        SimpleType.__init__(self, pname=pname, **kw)
        self.itemType = itemType or self.itemType
        self.itemTypeCode = self.itemType

        itemTypeCode = None
        if type(self.itemTypeCode) in _seqtypes:
            namespaceURI,name = self.itemTypeCode
            try:
                itemTypeCode = _get_type_definition(*self.itemType)(None)
            except:
                if _is_xsd_or_soap_ns(namespaceURI) is False:
                    raise
                for pyclass in TYPES:
                    if pyclass.type == self.itemTypeCode:
                        itemTypeCode =  pyclass(None)
                        break
                    elif pyclass.type[1] == name:
                        itemTypeCode =  pyclass(None)

                if itemTypeCode is None:
                    raise EvaluateException('Filed to locate %s' %self.itemTypeCode)

            if hasattr(itemTypeCode, 'text_to_data') is False:
                raise EvaluateException('TypeCode class %s missing text_to_data method' %itemTypeCode)

            self.itemTypeCode = itemTypeCode


    def text_to_data(self, text):
        '''convert text into typecode specific data.  items in
        list are space separated.
        '''
        v = []
        for item in text.split(' '):
            v.append(self.itemTypeCode.text_to_data(item))

        if self.pyclass is not None:
            return self.pyclass(v)
        return v

    def parse(self, elt, ps):
        '''elt -- the DOM element being parsed
        ps -- the ParsedSoap object.
        '''
        self.checkname(elt, ps)
        if len(_children(elt)) == 0:
            href = _find_href(elt)
            if not href:
                if self.nilled(elt, ps) is False:
                    # No content, no HREF, not NIL:  empty string
                    return ""
                # No content, no HREF, and is NIL...
                if self.minOccurs == 0 or self.nillable is True: 
                    return None
                raise EvaluateException('Non-optional string missing',
                        ps.Backtrace(elt))
            if href[0] != '#':
                return ps.ResolveHREF(href, self)
            elt = ps.FindLocalHREF(href, elt)
            self.checktype(elt, ps)

        if self.nilled(elt, ps): return None
        if len(_children(elt)) == 0: return ''

        v = self.simple_value(elt, ps)
        return self.text_to_data(v)

    def serialize(self, elt, sw, pyobj, name=None, orig=None, **kw):
        '''elt -- the current DOMWrapper element 
           sw -- soapWriter object
           pyobj -- python object to serialize
        '''
        if type(pyobj) not in _seqtypes:
            raise EvaluateException, 'expecting a list'

        el = elt.createAppendElement(self.nspname, self.pname)
        if self.nillable is True and pyobj is None:
            self.serialize_as_nil(el)
            return None
        
        tc = self.itemTypeCode
        s = StringIO()
        for item in pyobj:
            s.write(tc.get_formatted_content(item))
            s.write(' ')

        el.createAppendTextNode(textNode)


class _GetPyobjWrapper:
    '''Get a python object that wraps data and typecode.  Used by
    <any> parse routine, so that typecode information discovered
    during parsing is retained in the pyobj representation
    and thus can be serialized.
    '''
    types_dict = {}
    for builtin_type in [int,float,str,tuple,list,unicode]:
        class Wrapper(builtin_type): pass
        types_dict[builtin_type] = Wrapper

    def RegisterAnyElement(cls):
        for k,v in cls.types_dict.items():
            what = Any.serialmap.get(k)
            if what is None: continue
            if v in what.__class__.seriallist:
                continue
            what.__class__.seriallist.append(v)
            RegisterType(what.__class__, clobber=1)
    RegisterAnyElement = classmethod(RegisterAnyElement)

    def Wrap(cls, pyobj, what):
        d = cls.types_dict
        if type(pyobj) is bool:  
            pyclass = d[int]
        elif d.has_key(type(pyobj)) is True:
            pyclass = d[type(pyobj)]
        else:
            raise TypeError,\
               'Expecting a built-in type in %s (got %s).' %(d.keys(),type(pyobj))

        newobj = pyclass(pyobj)
        newobj.typecode = what
        return newobj
    Wrap = classmethod(Wrap)


def Wrap(pyobj, what):
    return _GetPyobjWrapper.Wrap(pyobj, what)

def RegisterAnyElement():
    return _GetPyobjWrapper.RegisterAnyElement()


from TCnumbers import *
from TCtimes import *
from TCcompound import *
from TCapache import *

f = lambda x: type(x) == types.ClassType and issubclass(x, TypeCode) and getattr(x, 'type', None) is not None
TYPES = filter(f, map(lambda y:eval(y),dir()))

if __name__ == '__main__': print _copyright

