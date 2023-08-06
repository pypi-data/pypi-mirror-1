# ./pyxb/bundles/wssplat/raw/soap11.py
# PyXB bindings for NamespaceModule
# NSM:124ab58ff634848548cf6d9d1320f856ff23519e
# Generated 2009-11-30 18:08:39.046365 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:ad35e566-de0d-11de-a41c-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/soap/envelope/', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])
ModuleRecord = Namespace.lookupModuleRecordByUID(_GenerationUID, create_if_missing=True)
ModuleRecord._setModule(sys.modules[__name__])

def CreateFromDocument (xml_text, default_namespace=None):
    """Parse the given XML and use the document element to create a Python instance."""
    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement)
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=Namespace.fallbackNamespace())
    handler = saxer.getContentHandler()
    saxer.parse(StringIO.StringIO(xml_text))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, _fallback_namespace=default_namespace)


# Atomic SimpleTypeDefinition
class STD_ANON_1 (pyxb.binding.datatypes.boolean):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_1._CF_pattern = pyxb.binding.facets.CF_pattern()
STD_ANON_1._CF_pattern.addPattern(pattern=u'0|1')
STD_ANON_1._InitializeFacetMap(STD_ANON_1._CF_pattern)

# List SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class encodingStyle (pyxb.binding.basis.STD_list):

    """
	    'encodingStyle' indicates any canonicalization conventions followed in the contents of the containing element.  For example, the value 'http://schemas.xmlsoap.org/soap/encoding/' indicates the pattern described in SOAP specification
	  """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'encodingStyle')
    _Documentation = u"\n\t    'encodingStyle' indicates any canonicalization conventions followed in the contents of the containing element.  For example, the value 'http://schemas.xmlsoap.org/soap/encoding/' indicates the pattern described in SOAP specification\n\t  "

    _ItemType = pyxb.binding.datatypes.anyURI
encodingStyle._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'encodingStyle', encodingStyle)

# Complex type Body_ with content type ELEMENT_ONLY
class Body_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Body')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Body', Body_)


# Complex type Envelope_ with content type ELEMENT_ONLY
class Envelope_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Envelope')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schemas.xmlsoap.org/soap/envelope/}Header uses Python identifier Header
    __Header = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Header'), 'Header', '__httpschemas_xmlsoap_orgsoapenvelope_Envelope__httpschemas_xmlsoap_orgsoapenvelopeHeader', False)

    
    Header = property(__Header.value, __Header.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/soap/envelope/}Body uses Python identifier Body
    __Body = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Body'), 'Body', '__httpschemas_xmlsoap_orgsoapenvelope_Envelope__httpschemas_xmlsoap_orgsoapenvelopeBody', False)

    
    Body = property(__Body.value, __Body.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/soap/envelope/'))
    _HasWildcardElement = True

    _ElementMap = {
        __Header.name() : __Header,
        __Body.name() : __Body
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Envelope', Envelope_)


# Complex type Header_ with content type ELEMENT_ONLY
class Header_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Header')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/soap/envelope/'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Header', Header_)


# Complex type detail with content type ELEMENT_ONLY
class detail (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'detail')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'detail', detail)


# Complex type Fault_ with content type ELEMENT_ONLY
class Fault_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Fault')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element detail uses Python identifier detail
    __detail = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(None, u'detail'), 'detail', '__httpschemas_xmlsoap_orgsoapenvelope_Fault__detail', False)

    
    detail = property(__detail.value, __detail.set, None, None)

    
    # Element faultcode uses Python identifier faultcode
    __faultcode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(None, u'faultcode'), 'faultcode', '__httpschemas_xmlsoap_orgsoapenvelope_Fault__faultcode', False)

    
    faultcode = property(__faultcode.value, __faultcode.set, None, None)

    
    # Element faultactor uses Python identifier faultactor
    __faultactor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(None, u'faultactor'), 'faultactor', '__httpschemas_xmlsoap_orgsoapenvelope_Fault__faultactor', False)

    
    faultactor = property(__faultactor.value, __faultactor.set, None, None)

    
    # Element faultstring uses Python identifier faultstring
    __faultstring = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(None, u'faultstring'), 'faultstring', '__httpschemas_xmlsoap_orgsoapenvelope_Fault__faultstring', False)

    
    faultstring = property(__faultstring.value, __faultstring.set, None, None)


    _ElementMap = {
        __detail.name() : __detail,
        __faultcode.name() : __faultcode,
        __faultactor.name() : __faultactor,
        __faultstring.name() : __faultstring
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Fault', Fault_)


Envelope = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Envelope'), Envelope_)
Namespace.addCategoryObject('elementBinding', Envelope.name().localName(), Envelope)

Header = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Header'), Header_)
Namespace.addCategoryObject('elementBinding', Header.name().localName(), Header)

Fault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Fault'), Fault_)
Namespace.addCategoryObject('elementBinding', Fault.name().localName(), Fault)

Body = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Body'), Body_)
Namespace.addCategoryObject('elementBinding', Body.name().localName(), Body)


Body_._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})



Envelope_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Header'), Header_, scope=Envelope_))

Envelope_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Body'), Body_, scope=Envelope_))
Envelope_._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Envelope_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Header'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Envelope_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Body'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Envelope_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Body'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/soap/envelope/'))),
    ])
})


Header_._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/soap/envelope/'))),
    ])
})


detail._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})



Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, u'detail'), detail, scope=Fault_))

Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, u'faultcode'), pyxb.binding.datatypes.QName, scope=Fault_))

Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, u'faultactor'), pyxb.binding.datatypes.anyURI, scope=Fault_))

Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, u'faultstring'), pyxb.binding.datatypes.string, scope=Fault_))
Fault_._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(None, u'faultcode'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(None, u'faultstring'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(None, u'faultactor'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(None, u'detail'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(None, u'detail'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
    ])
})
