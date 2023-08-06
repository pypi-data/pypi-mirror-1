# ./pyxb/bundles/wssplat/raw/wsam.py
# PyXB bindings for NamespaceModule
# NSM:8412da32cb8f7a70943a9934e4bb13ceb5b27944
# Generated 2009-11-30 18:08:51.029507 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:b45a55b6-de0d-11de-8b9c-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsp200607

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2007/02/addressing/metadata', create_if_missing=True)
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
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2007/02/addressing/metadata'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type AttributedQNameType with content type SIMPLE
class AttributedQNameType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.QName
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedQNameType')
    # Base type is pyxb.binding.datatypes.QName
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2007/02/addressing/metadata'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AttributedQNameType', AttributedQNameType)


# Complex type ServiceNameType with content type SIMPLE
class ServiceNameType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.QName
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ServiceNameType')
    # Base type is pyxb.binding.datatypes.QName
    
    # Attribute EndpointName uses Python identifier EndpointName
    __EndpointName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'EndpointName'), 'EndpointName', '__httpwww_w3_org200702addressingmetadata_ServiceNameType_EndpointName', pyxb.binding.datatypes.NCName)
    
    EndpointName = property(__EndpointName.value, __EndpointName.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2007/02/addressing/metadata'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __EndpointName.name() : __EndpointName
    }
Namespace.addCategoryObject('typeBinding', u'ServiceNameType', ServiceNameType)


# Complex type CTD_ANON_2 with content type ELEMENT_ONLY
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2006/07/ws-policy}Policy uses Python identifier Policy
    __Policy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2006/07/ws-policy'), u'Policy'), 'Policy', '__httpwww_w3_org200702addressingmetadata_CTD_ANON_2_httpwww_w3_org200607ws_policyPolicy', False)

    
    Policy = property(__Policy.value, __Policy.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2007/02/addressing/metadata'))

    _ElementMap = {
        __Policy.name() : __Policy
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_3 with content type EMPTY
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2007/02/addressing/metadata'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



NonAnonymousResponses = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NonAnonymousResponses'), CTD_ANON_1)
Namespace.addCategoryObject('elementBinding', NonAnonymousResponses.name().localName(), NonAnonymousResponses)

InterfaceName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InterfaceName'), AttributedQNameType)
Namespace.addCategoryObject('elementBinding', InterfaceName.name().localName(), InterfaceName)

ServiceName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ServiceName'), ServiceNameType)
Namespace.addCategoryObject('elementBinding', ServiceName.name().localName(), ServiceName)

Addressing = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Addressing'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', Addressing.name().localName(), Addressing)

AnonymousResponses = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AnonymousResponses'), CTD_ANON_3)
Namespace.addCategoryObject('elementBinding', AnonymousResponses.name().localName(), AnonymousResponses)



CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2006/07/ws-policy'), u'Policy'), pyxb.bundles.wssplat.wsp200607.CTD_ANON_1, scope=CTD_ANON_2))
CTD_ANON_2._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2006/07/ws-policy'), u'Policy'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})
