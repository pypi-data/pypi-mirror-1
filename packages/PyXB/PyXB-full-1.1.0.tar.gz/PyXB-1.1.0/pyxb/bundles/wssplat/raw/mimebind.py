# ./pyxb/bundles/wssplat/raw/mimebind.py
# PyXB bindings for NamespaceModule
# NSM:5404248094c8a480a41150c00669c3a55d100562
# Generated 2009-11-30 18:08:38.311232 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:acc2b690-de0d-11de-a343-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.bundles.wssplat.wsdl11
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/wsdl/mime/', create_if_missing=True)
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


# Complex type multipartRelatedType with content type ELEMENT_ONLY
class multipartRelatedType (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'multipartRelatedType')
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Element part uses Python identifier part
    __part = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(None, u'part'), 'part', '__httpschemas_xmlsoap_orgwsdlmime_multipartRelatedType_part', True)

    
    part = property(__part.value, __part.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement

    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        __part.name() : __part
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'multipartRelatedType', multipartRelatedType)


# Complex type contentType with content type EMPTY
class contentType (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'contentType')
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute part uses Python identifier part
    __part = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'part'), 'part', '__httpschemas_xmlsoap_orgwsdlmime_contentType_part', pyxb.binding.datatypes.NMTOKEN)
    
    part = property(__part.value, __part.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpschemas_xmlsoap_orgwsdlmime_contentType_type', pyxb.binding.datatypes.string)
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        __part.name() : __part,
        __type.name() : __type
    })
Namespace.addCategoryObject('typeBinding', u'contentType', contentType)


# Complex type tMimeXml with content type EMPTY
class tMimeXml (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tMimeXml')
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute part uses Python identifier part
    __part = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'part'), 'part', '__httpschemas_xmlsoap_orgwsdlmime_tMimeXml_part', pyxb.binding.datatypes.NMTOKEN)
    
    part = property(__part.value, __part.set, None, None)


    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        __part.name() : __part
    })
Namespace.addCategoryObject('typeBinding', u'tMimeXml', tMimeXml)


# Complex type tPart with content type ELEMENT_ONLY
class tPart (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPart')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdlmime_tPart_name', pyxb.binding.datatypes.NMTOKEN, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __name.name() : __name
    }
Namespace.addCategoryObject('typeBinding', u'tPart', tPart)


multipartRelated = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'multipartRelated'), multipartRelatedType)
Namespace.addCategoryObject('elementBinding', multipartRelated.name().localName(), multipartRelated)

content = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'content'), contentType)
Namespace.addCategoryObject('elementBinding', content.name().localName(), content)

mimeXml = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'mimeXml'), tMimeXml)
Namespace.addCategoryObject('elementBinding', mimeXml.name().localName(), mimeXml)



multipartRelatedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, u'part'), tPart, scope=multipartRelatedType))
multipartRelatedType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=multipartRelatedType._UseForTag(pyxb.namespace.ExpandedName(None, u'part'))),
    ])
})


tPart._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=set(u'http://schemas.xmlsoap.org/wsdl/mime/'))),
    ])
})
