# ./pyxb/bundles/wssplat/raw/httpbind.py
# PyXB bindings for NamespaceModule
# NSM:700d4ca8e0588f8b897f9c60d123e08fa4d56b36
# Generated 2009-11-30 18:08:37.589163 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:ac5658a6-de0d-11de-b59f-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsdl11

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/wsdl/http/', create_if_missing=True)
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


# Complex type CTD_ANON_1 with content type EMPTY
class CTD_ANON_1 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type addressType with content type EMPTY
class addressType (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'addressType')
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute location uses Python identifier location
    __location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'location'), 'location', '__httpschemas_xmlsoap_orgwsdlhttp_addressType_location', pyxb.binding.datatypes.anyURI, required=True)
    
    location = property(__location.value, __location.set, None, None)


    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        __location.name() : __location
    })
Namespace.addCategoryObject('typeBinding', u'addressType', addressType)


# Complex type CTD_ANON_2 with content type EMPTY
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type bindingType with content type EMPTY
class bindingType (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'bindingType')
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute verb uses Python identifier verb
    __verb = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'verb'), 'verb', '__httpschemas_xmlsoap_orgwsdlhttp_bindingType_verb', pyxb.binding.datatypes.NMTOKEN, required=True)
    
    verb = property(__verb.value, __verb.set, None, None)


    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        __verb.name() : __verb
    })
Namespace.addCategoryObject('typeBinding', u'bindingType', bindingType)


# Complex type operationType with content type EMPTY
class operationType (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'operationType')
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute location uses Python identifier location
    __location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'location'), 'location', '__httpschemas_xmlsoap_orgwsdlhttp_operationType_location', pyxb.binding.datatypes.anyURI, required=True)
    
    location = property(__location.value, __location.set, None, None)


    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        __location.name() : __location
    })
Namespace.addCategoryObject('typeBinding', u'operationType', operationType)


urlEncoded = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'urlEncoded'), CTD_ANON_1)
Namespace.addCategoryObject('elementBinding', urlEncoded.name().localName(), urlEncoded)

address = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), addressType)
Namespace.addCategoryObject('elementBinding', address.name().localName(), address)

urlReplacement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'urlReplacement'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', urlReplacement.name().localName(), urlReplacement)

binding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'binding'), bindingType)
Namespace.addCategoryObject('elementBinding', binding.name().localName(), binding)

operation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operation'), operationType)
Namespace.addCategoryObject('elementBinding', operation.name().localName(), operation)
