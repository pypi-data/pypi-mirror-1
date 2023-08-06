# ./pyxb/bundles/wssplat/raw/wsp.py
# PyXB bindings for NamespaceModule
# NSM:f4837f0658228740211c38471cfc1510d0fdb629
# Generated 2009-11-30 18:08:48.564744 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:b2b7831e-de0d-11de-9df5-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/ns/ws-policy', create_if_missing=True)
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


# List SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON_1 (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.anyURI."""

    _ExpandedName = None
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.anyURI
STD_ANON_1._InitializeFacetMap()

# Complex type CTD_ANON_1 with content type ELEMENT_ONLY
class CTD_ANON_1 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute DigestAlgorithm uses Python identifier DigestAlgorithm
    __DigestAlgorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DigestAlgorithm'), 'DigestAlgorithm', '__httpwww_w3_orgnsws_policy_CTD_ANON_1_DigestAlgorithm', pyxb.binding.datatypes.anyURI, unicode_default=u'http://www.w3.org/ns/ws-policy/Sha1Exc')
    
    DigestAlgorithm = property(__DigestAlgorithm.value, __DigestAlgorithm.set, None, None)

    
    # Attribute URI uses Python identifier URI
    __URI = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'URI'), 'URI', '__httpwww_w3_orgnsws_policy_CTD_ANON_1_URI', pyxb.binding.datatypes.anyURI, required=True)
    
    URI = property(__URI.value, __URI.set, None, None)

    
    # Attribute Digest uses Python identifier Digest
    __Digest = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Digest'), 'Digest', '__httpwww_w3_orgnsws_policy_CTD_ANON_1_Digest', pyxb.binding.datatypes.base64Binary)
    
    Digest = property(__Digest.value, __Digest.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __DigestAlgorithm.name() : __DigestAlgorithm,
        __URI.name() : __URI,
        __Digest.name() : __Digest
    }



# Complex type CTD_ANON_2 with content type SIMPLE
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyURI
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type OperatorContentType with content type ELEMENT_ONLY
class OperatorContentType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'OperatorContentType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/ns/ws-policy}PolicyReference uses Python identifier PolicyReference
    __PolicyReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'), 'PolicyReference', '__httpwww_w3_orgnsws_policy_OperatorContentType_httpwww_w3_orgnsws_policyPolicyReference', True)

    
    PolicyReference = property(__PolicyReference.value, __PolicyReference.set, None, None)

    
    # Element {http://www.w3.org/ns/ws-policy}ExactlyOne uses Python identifier ExactlyOne
    __ExactlyOne = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ExactlyOne'), 'ExactlyOne', '__httpwww_w3_orgnsws_policy_OperatorContentType_httpwww_w3_orgnsws_policyExactlyOne', True)

    
    ExactlyOne = property(__ExactlyOne.value, __ExactlyOne.set, None, None)

    
    # Element {http://www.w3.org/ns/ws-policy}Policy uses Python identifier Policy
    __Policy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Policy'), 'Policy', '__httpwww_w3_orgnsws_policy_OperatorContentType_httpwww_w3_orgnsws_policyPolicy', True)

    
    Policy = property(__Policy.value, __Policy.set, None, None)

    
    # Element {http://www.w3.org/ns/ws-policy}All uses Python identifier All
    __All = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'All'), 'All', '__httpwww_w3_orgnsws_policy_OperatorContentType_httpwww_w3_orgnsws_policyAll', True)

    
    All = property(__All.value, __All.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __PolicyReference.name() : __PolicyReference,
        __ExactlyOne.name() : __ExactlyOne,
        __Policy.name() : __Policy,
        __All.name() : __All
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'OperatorContentType', OperatorContentType)


# Complex type CTD_ANON_3 with content type ELEMENT_ONLY
class CTD_ANON_3 (OperatorContentType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is OperatorContentType
    
    # Element PolicyReference ({http://www.w3.org/ns/ws-policy}PolicyReference) inherited from {http://www.w3.org/ns/ws-policy}OperatorContentType
    
    # Element ExactlyOne ({http://www.w3.org/ns/ws-policy}ExactlyOne) inherited from {http://www.w3.org/ns/ws-policy}OperatorContentType
    
    # Element Policy ({http://www.w3.org/ns/ws-policy}Policy) inherited from {http://www.w3.org/ns/ws-policy}OperatorContentType
    
    # Element All ({http://www.w3.org/ns/ws-policy}All) inherited from {http://www.w3.org/ns/ws-policy}OperatorContentType
    
    # Attribute Name uses Python identifier Name
    __Name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Name'), 'Name', '__httpwww_w3_orgnsws_policy_CTD_ANON_3_Name', pyxb.binding.datatypes.anyURI)
    
    Name = property(__Name.value, __Name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = OperatorContentType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = OperatorContentType._AttributeMap.copy()
    _AttributeMap.update({
        __Name.name() : __Name
    })



# Complex type CTD_ANON_4 with content type ELEMENT_ONLY
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_5 with content type ELEMENT_ONLY
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/ns/ws-policy}AppliesTo uses Python identifier AppliesTo
    __AppliesTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AppliesTo'), 'AppliesTo', '__httpwww_w3_orgnsws_policy_CTD_ANON_5_httpwww_w3_orgnsws_policyAppliesTo', False)

    
    AppliesTo = property(__AppliesTo.value, __AppliesTo.set, None, None)

    
    # Element {http://www.w3.org/ns/ws-policy}PolicyReference uses Python identifier PolicyReference
    __PolicyReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'), 'PolicyReference', '__httpwww_w3_orgnsws_policy_CTD_ANON_5_httpwww_w3_orgnsws_policyPolicyReference', True)

    
    PolicyReference = property(__PolicyReference.value, __PolicyReference.set, None, None)

    
    # Element {http://www.w3.org/ns/ws-policy}Policy uses Python identifier Policy
    __Policy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Policy'), 'Policy', '__httpwww_w3_orgnsws_policy_CTD_ANON_5_httpwww_w3_orgnsws_policyPolicy', True)

    
    Policy = property(__Policy.value, __Policy.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        __AppliesTo.name() : __AppliesTo,
        __PolicyReference.name() : __PolicyReference,
        __Policy.name() : __Policy
    }
    _AttributeMap = {
        
    }



PolicyReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'), CTD_ANON_1)
Namespace.addCategoryObject('elementBinding', PolicyReference.name().localName(), PolicyReference)

URI = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'URI'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', URI.name().localName(), URI)

ExactlyOne = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ExactlyOne'), OperatorContentType)
Namespace.addCategoryObject('elementBinding', ExactlyOne.name().localName(), ExactlyOne)

Policy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Policy'), CTD_ANON_3)
Namespace.addCategoryObject('elementBinding', Policy.name().localName(), Policy)

All = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'All'), OperatorContentType)
Namespace.addCategoryObject('elementBinding', All.name().localName(), All)

PolicyAttachment = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolicyAttachment'), CTD_ANON_5)
Namespace.addCategoryObject('elementBinding', PolicyAttachment.name().localName(), PolicyAttachment)

AppliesTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AppliesTo'), CTD_ANON_4)
Namespace.addCategoryObject('elementBinding', AppliesTo.name().localName(), AppliesTo)


CTD_ANON_1._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})



OperatorContentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'), CTD_ANON_1, scope=OperatorContentType))

OperatorContentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ExactlyOne'), OperatorContentType, scope=OperatorContentType))

OperatorContentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Policy'), CTD_ANON_3, scope=OperatorContentType))

OperatorContentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'All'), OperatorContentType, scope=OperatorContentType))
OperatorContentType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=OperatorContentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=OperatorContentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExactlyOne'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=OperatorContentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Policy'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=OperatorContentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'All'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/ws-policy'))),
    ])
})


CTD_ANON_3._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExactlyOne'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Policy'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'All'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/ws-policy'))),
    ])
})


CTD_ANON_4._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})



CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AppliesTo'), CTD_ANON_4, scope=CTD_ANON_5))

CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'), CTD_ANON_1, scope=CTD_ANON_5))

CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Policy'), CTD_ANON_3, scope=CTD_ANON_5))
CTD_ANON_5._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AppliesTo'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Policy'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/ws-policy'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Policy'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/ws-policy'))),
    ])
})
