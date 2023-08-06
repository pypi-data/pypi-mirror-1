# ./pyxb/bundles/wssplat/raw/wsa.py
# PyXB bindings for NamespaceModule
# NSM:0ecbd27a42302a2dbf33a51269e14ce6419c0738
# Generated 2009-11-30 18:08:50.143182 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:b3ce0746-de0d-11de-80f6-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/08/addressing', create_if_missing=True)
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
class RelationshipType (pyxb.binding.datatypes.anyURI, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RelationshipType')
    _Documentation = None
RelationshipType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=RelationshipType, enum_prefix=None)
RelationshipType.httpwww_w3_org200508addressingreply = RelationshipType._CF_enumeration.addEnumeration(unicode_value=u'http://www.w3.org/2005/08/addressing/reply')
RelationshipType._InitializeFacetMap(RelationshipType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'RelationshipType', RelationshipType)

# Union SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class RelationshipTypeOpenEnum (pyxb.binding.basis.STD_union):

    """Simple type that is a union of RelationshipType, pyxb.binding.datatypes.anyURI."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RelationshipTypeOpenEnum')
    _Documentation = None

    _MemberTypes = ( RelationshipType, pyxb.binding.datatypes.anyURI, )
RelationshipTypeOpenEnum._CF_pattern = pyxb.binding.facets.CF_pattern()
RelationshipTypeOpenEnum._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=RelationshipTypeOpenEnum)
RelationshipTypeOpenEnum.httpwww_w3_org200508addressingreply = u'http://www.w3.org/2005/08/addressing/reply'# originally RelationshipType.httpwww_w3_org200508addressingreply
RelationshipTypeOpenEnum._InitializeFacetMap(RelationshipTypeOpenEnum._CF_pattern,
   RelationshipTypeOpenEnum._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'RelationshipTypeOpenEnum', RelationshipTypeOpenEnum)

# Atomic SimpleTypeDefinition
class FaultCodesType (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FaultCodesType')
    _Documentation = None
FaultCodesType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=FaultCodesType, enum_prefix=None)
FaultCodesType.tnsInvalidAddressingHeader = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:InvalidAddressingHeader')
FaultCodesType.tnsInvalidAddress = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:InvalidAddress')
FaultCodesType.tnsInvalidEPR = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:InvalidEPR')
FaultCodesType.tnsInvalidCardinality = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:InvalidCardinality')
FaultCodesType.tnsMissingAddressInEPR = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:MissingAddressInEPR')
FaultCodesType.tnsDuplicateMessageID = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:DuplicateMessageID')
FaultCodesType.tnsActionMismatch = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:ActionMismatch')
FaultCodesType.tnsMessageAddressingHeaderRequired = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:MessageAddressingHeaderRequired')
FaultCodesType.tnsDestinationUnreachable = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:DestinationUnreachable')
FaultCodesType.tnsActionNotSupported = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:ActionNotSupported')
FaultCodesType.tnsEndpointUnavailable = FaultCodesType._CF_enumeration.addEnumeration(unicode_value=u'tns:EndpointUnavailable')
FaultCodesType._InitializeFacetMap(FaultCodesType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'FaultCodesType', FaultCodesType)

# Union SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class FaultCodesOpenEnumType (pyxb.binding.basis.STD_union):

    """Simple type that is a union of FaultCodesType, pyxb.binding.datatypes.QName."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FaultCodesOpenEnumType')
    _Documentation = None

    _MemberTypes = ( FaultCodesType, pyxb.binding.datatypes.QName, )
FaultCodesOpenEnumType._CF_pattern = pyxb.binding.facets.CF_pattern()
FaultCodesOpenEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=FaultCodesOpenEnumType)
FaultCodesOpenEnumType.tnsInvalidAddressingHeader = u'tns:InvalidAddressingHeader'# originally FaultCodesType.tnsInvalidAddressingHeader
FaultCodesOpenEnumType.tnsInvalidAddress = u'tns:InvalidAddress'# originally FaultCodesType.tnsInvalidAddress
FaultCodesOpenEnumType.tnsInvalidEPR = u'tns:InvalidEPR'# originally FaultCodesType.tnsInvalidEPR
FaultCodesOpenEnumType.tnsInvalidCardinality = u'tns:InvalidCardinality'# originally FaultCodesType.tnsInvalidCardinality
FaultCodesOpenEnumType.tnsMissingAddressInEPR = u'tns:MissingAddressInEPR'# originally FaultCodesType.tnsMissingAddressInEPR
FaultCodesOpenEnumType.tnsDuplicateMessageID = u'tns:DuplicateMessageID'# originally FaultCodesType.tnsDuplicateMessageID
FaultCodesOpenEnumType.tnsActionMismatch = u'tns:ActionMismatch'# originally FaultCodesType.tnsActionMismatch
FaultCodesOpenEnumType.tnsMessageAddressingHeaderRequired = u'tns:MessageAddressingHeaderRequired'# originally FaultCodesType.tnsMessageAddressingHeaderRequired
FaultCodesOpenEnumType.tnsDestinationUnreachable = u'tns:DestinationUnreachable'# originally FaultCodesType.tnsDestinationUnreachable
FaultCodesOpenEnumType.tnsActionNotSupported = u'tns:ActionNotSupported'# originally FaultCodesType.tnsActionNotSupported
FaultCodesOpenEnumType.tnsEndpointUnavailable = u'tns:EndpointUnavailable'# originally FaultCodesType.tnsEndpointUnavailable
FaultCodesOpenEnumType._InitializeFacetMap(FaultCodesOpenEnumType._CF_pattern,
   FaultCodesOpenEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'FaultCodesOpenEnumType', FaultCodesOpenEnumType)

# Complex type RelatesToType with content type SIMPLE
class RelatesToType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RelatesToType')
    # Base type is pyxb.binding.datatypes.anyURI
    
    # Attribute RelationshipType uses Python identifier RelationshipType
    __RelationshipType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'RelationshipType'), 'RelationshipType', '__httpwww_w3_org200508addressing_RelatesToType_RelationshipType', RelationshipTypeOpenEnum, unicode_default=u'http://www.w3.org/2005/08/addressing/reply')
    
    RelationshipType = property(__RelationshipType.value, __RelationshipType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __RelationshipType.name() : __RelationshipType
    }
Namespace.addCategoryObject('typeBinding', u'RelatesToType', RelatesToType)


# Complex type MetadataType with content type ELEMENT_ONLY
class MetadataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MetadataType')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'MetadataType', MetadataType)


# Complex type AttributedURIType with content type SIMPLE
class AttributedURIType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedURIType')
    # Base type is pyxb.binding.datatypes.anyURI
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AttributedURIType', AttributedURIType)


# Complex type AttributedUnsignedLongType with content type SIMPLE
class AttributedUnsignedLongType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.unsignedLong
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedUnsignedLongType')
    # Base type is pyxb.binding.datatypes.unsignedLong
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AttributedUnsignedLongType', AttributedUnsignedLongType)


# Complex type EndpointReferenceType with content type ELEMENT_ONLY
class EndpointReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EndpointReferenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2005/08/addressing}Address uses Python identifier Address
    __Address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Address'), 'Address', '__httpwww_w3_org200508addressing_EndpointReferenceType_httpwww_w3_org200508addressingAddress', False)

    
    Address = property(__Address.value, __Address.set, None, None)

    
    # Element {http://www.w3.org/2005/08/addressing}ReferenceParameters uses Python identifier ReferenceParameters
    __ReferenceParameters = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ReferenceParameters'), 'ReferenceParameters', '__httpwww_w3_org200508addressing_EndpointReferenceType_httpwww_w3_org200508addressingReferenceParameters', False)

    
    ReferenceParameters = property(__ReferenceParameters.value, __ReferenceParameters.set, None, None)

    
    # Element {http://www.w3.org/2005/08/addressing}Metadata uses Python identifier Metadata
    __Metadata = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Metadata'), 'Metadata', '__httpwww_w3_org200508addressing_EndpointReferenceType_httpwww_w3_org200508addressingMetadata', False)

    
    Metadata = property(__Metadata.value, __Metadata.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))
    _HasWildcardElement = True

    _ElementMap = {
        __Address.name() : __Address,
        __ReferenceParameters.name() : __ReferenceParameters,
        __Metadata.name() : __Metadata
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'EndpointReferenceType', EndpointReferenceType)


# Complex type AttributedQNameType with content type SIMPLE
class AttributedQNameType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.QName
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedQNameType')
    # Base type is pyxb.binding.datatypes.QName
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AttributedQNameType', AttributedQNameType)


# Complex type ReferenceParametersType with content type ELEMENT_ONLY
class ReferenceParametersType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ReferenceParametersType')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ReferenceParametersType', ReferenceParametersType)


# Complex type ProblemActionType with content type ELEMENT_ONLY
class ProblemActionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ProblemActionType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2005/08/addressing}SoapAction uses Python identifier SoapAction
    __SoapAction = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SoapAction'), 'SoapAction', '__httpwww_w3_org200508addressing_ProblemActionType_httpwww_w3_org200508addressingSoapAction', False)

    
    SoapAction = property(__SoapAction.value, __SoapAction.set, None, None)

    
    # Element {http://www.w3.org/2005/08/addressing}Action uses Python identifier Action
    __Action = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Action'), 'Action', '__httpwww_w3_org200508addressing_ProblemActionType_httpwww_w3_org200508addressingAction', False)

    
    Action = property(__Action.value, __Action.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))

    _ElementMap = {
        __SoapAction.name() : __SoapAction,
        __Action.name() : __Action
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ProblemActionType', ProblemActionType)


RelatesTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RelatesTo'), RelatesToType)
Namespace.addCategoryObject('elementBinding', RelatesTo.name().localName(), RelatesTo)

MessageID = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MessageID'), AttributedURIType)
Namespace.addCategoryObject('elementBinding', MessageID.name().localName(), MessageID)

RetryAfter = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RetryAfter'), AttributedUnsignedLongType)
Namespace.addCategoryObject('elementBinding', RetryAfter.name().localName(), RetryAfter)

FaultTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FaultTo'), EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', FaultTo.name().localName(), FaultTo)

ProblemHeaderQName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProblemHeaderQName'), AttributedQNameType)
Namespace.addCategoryObject('elementBinding', ProblemHeaderQName.name().localName(), ProblemHeaderQName)

ReferenceParameters = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ReferenceParameters'), ReferenceParametersType)
Namespace.addCategoryObject('elementBinding', ReferenceParameters.name().localName(), ReferenceParameters)

EndpointReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EndpointReference'), EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', EndpointReference.name().localName(), EndpointReference)

ProblemAction = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProblemAction'), ProblemActionType)
Namespace.addCategoryObject('elementBinding', ProblemAction.name().localName(), ProblemAction)

ReplyTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ReplyTo'), EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', ReplyTo.name().localName(), ReplyTo)

From = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'From'), EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', From.name().localName(), From)

ProblemIRI = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProblemIRI'), AttributedURIType)
Namespace.addCategoryObject('elementBinding', ProblemIRI.name().localName(), ProblemIRI)

Metadata = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Metadata'), MetadataType)
Namespace.addCategoryObject('elementBinding', Metadata.name().localName(), Metadata)

To = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'To'), AttributedURIType)
Namespace.addCategoryObject('elementBinding', To.name().localName(), To)

Action = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Action'), AttributedURIType)
Namespace.addCategoryObject('elementBinding', Action.name().localName(), Action)


MetadataType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})



EndpointReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Address'), AttributedURIType, scope=EndpointReferenceType))

EndpointReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ReferenceParameters'), ReferenceParametersType, scope=EndpointReferenceType))

EndpointReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Metadata'), MetadataType, scope=EndpointReferenceType))
EndpointReferenceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=EndpointReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Address'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=EndpointReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=EndpointReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ReferenceParameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=EndpointReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2005/08/addressing'))),
    ])
})


ReferenceParametersType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})



ProblemActionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SoapAction'), pyxb.binding.datatypes.anyURI, scope=ProblemActionType))

ProblemActionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Action'), AttributedURIType, scope=ProblemActionType))
ProblemActionType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProblemActionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Action'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProblemActionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SoapAction'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProblemActionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SoapAction'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})
