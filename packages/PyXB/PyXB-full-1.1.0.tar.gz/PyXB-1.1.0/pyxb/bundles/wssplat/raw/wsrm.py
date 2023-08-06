# ./pyxb/bundles/wssplat/raw/wsrm.py
# PyXB bindings for NamespaceModule
# NSM:51117966240f7c6b98d95f1b3ed6125f819a832c
# Generated 2009-11-30 18:08:55.229017 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:b6c1dde2-de0d-11de-850c-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsa

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/ws-rx/wsrm/200702', create_if_missing=True)
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
class MessageNumberType (pyxb.binding.datatypes.unsignedLong):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MessageNumberType')
    _Documentation = None
MessageNumberType._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=MessageNumberType, value=pyxb.binding.datatypes.unsignedLong(1L))
MessageNumberType._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=MessageNumberType, value=pyxb.binding.datatypes.unsignedLong(9223372036854775807L))
MessageNumberType._InitializeFacetMap(MessageNumberType._CF_minInclusive,
   MessageNumberType._CF_maxInclusive)
Namespace.addCategoryObject('typeBinding', u'MessageNumberType', MessageNumberType)

# Atomic SimpleTypeDefinition
class FaultCodes (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FaultCodes')
    _Documentation = None
FaultCodes._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=FaultCodes, enum_prefix=None)
FaultCodes.wsrmSequenceTerminated = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:SequenceTerminated')
FaultCodes.wsrmUnknownSequence = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:UnknownSequence')
FaultCodes.wsrmInvalidAcknowledgement = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:InvalidAcknowledgement')
FaultCodes.wsrmMessageNumberRollover = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:MessageNumberRollover')
FaultCodes.wsrmCreateSequenceRefused = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:CreateSequenceRefused')
FaultCodes.wsrmSequenceClosed = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:SequenceClosed')
FaultCodes.wsrmWSRMRequired = FaultCodes._CF_enumeration.addEnumeration(unicode_value=u'wsrm:WSRMRequired')
FaultCodes._InitializeFacetMap(FaultCodes._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'FaultCodes', FaultCodes)

# Atomic SimpleTypeDefinition
class STD_ANON_1 (pyxb.binding.datatypes.QName):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_1._InitializeFacetMap()

# Atomic SimpleTypeDefinition
class IncompleteSequenceBehaviorType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehaviorType')
    _Documentation = None
IncompleteSequenceBehaviorType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=IncompleteSequenceBehaviorType, enum_prefix=None)
IncompleteSequenceBehaviorType.DiscardEntireSequence = IncompleteSequenceBehaviorType._CF_enumeration.addEnumeration(unicode_value=u'DiscardEntireSequence')
IncompleteSequenceBehaviorType.DiscardFollowingFirstGap = IncompleteSequenceBehaviorType._CF_enumeration.addEnumeration(unicode_value=u'DiscardFollowingFirstGap')
IncompleteSequenceBehaviorType.NoDiscard = IncompleteSequenceBehaviorType._CF_enumeration.addEnumeration(unicode_value=u'NoDiscard')
IncompleteSequenceBehaviorType._InitializeFacetMap(IncompleteSequenceBehaviorType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'IncompleteSequenceBehaviorType', IncompleteSequenceBehaviorType)

# Complex type CTD_ANON_1 with content type SIMPLE
class CTD_ANON_1 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.duration
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.duration
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_2 with content type SIMPLE
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyURI
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
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
    
    # Attribute Upper uses Python identifier Upper
    __Upper = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Upper'), 'Upper', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_3_Upper', pyxb.binding.datatypes.unsignedLong, required=True)
    
    Upper = property(__Upper.value, __Upper.set, None, None)

    
    # Attribute Lower uses Python identifier Lower
    __Lower = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Lower'), 'Lower', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_3_Lower', pyxb.binding.datatypes.unsignedLong, required=True)
    
    Lower = property(__Lower.value, __Lower.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Upper.name() : __Upper,
        __Lower.name() : __Lower
    }



# Complex type AckRequestedType with content type ELEMENT_ONLY
class AckRequestedType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AckRequestedType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_AckRequestedType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AckRequestedType', AckRequestedType)


# Complex type CTD_ANON_4 with content type SIMPLE
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyURI
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type DetailType with content type ELEMENT_ONLY
class DetailType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DetailType')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'DetailType', DetailType)


# Complex type SequenceFaultType with content type ELEMENT_ONLY
class SequenceFaultType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SequenceFaultType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}FaultCode uses Python identifier FaultCode
    __FaultCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FaultCode'), 'FaultCode', '__httpdocs_oasis_open_orgws_rxwsrm200702_SequenceFaultType_httpdocs_oasis_open_orgws_rxwsrm200702FaultCode', False)

    
    FaultCode = property(__FaultCode.value, __FaultCode.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Detail uses Python identifier Detail
    __Detail = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Detail'), 'Detail', '__httpdocs_oasis_open_orgws_rxwsrm200702_SequenceFaultType_httpdocs_oasis_open_orgws_rxwsrm200702Detail', False)

    
    Detail = property(__Detail.value, __Detail.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __FaultCode.name() : __FaultCode,
        __Detail.name() : __Detail
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SequenceFaultType', SequenceFaultType)


# Complex type CreateSequenceType with content type ELEMENT_ONLY
class CreateSequenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CreateSequenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}AcksTo uses Python identifier AcksTo
    __AcksTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'), 'AcksTo', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702AcksTo', False)

    
    AcksTo = property(__AcksTo.value, __AcksTo.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702Expires', False)

    
    Expires = property(__Expires.value, __Expires.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Offer uses Python identifier Offer
    __Offer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Offer'), 'Offer', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702Offer', False)

    
    Offer = property(__Offer.value, __Offer.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __AcksTo.name() : __AcksTo,
        __Expires.name() : __Expires,
        __Offer.name() : __Offer
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CreateSequenceType', CreateSequenceType)


# Complex type CreateSequenceResponseType with content type ELEMENT_ONLY
class CreateSequenceResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CreateSequenceResponseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702Expires', False)

    
    Expires = property(__Expires.value, __Expires.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}IncompleteSequenceBehavior uses Python identifier IncompleteSequenceBehavior
    __IncompleteSequenceBehavior = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'), 'IncompleteSequenceBehavior', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702IncompleteSequenceBehavior', False)

    
    IncompleteSequenceBehavior = property(__IncompleteSequenceBehavior.value, __IncompleteSequenceBehavior.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Accept uses Python identifier Accept
    __Accept = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Accept'), 'Accept', '__httpdocs_oasis_open_orgws_rxwsrm200702_CreateSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702Accept', False)

    
    Accept = property(__Accept.value, __Accept.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __Expires.name() : __Expires,
        __IncompleteSequenceBehavior.name() : __IncompleteSequenceBehavior,
        __Accept.name() : __Accept
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CreateSequenceResponseType', CreateSequenceResponseType)


# Complex type CloseSequenceType with content type ELEMENT_ONLY
class CloseSequenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CloseSequenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_CloseSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}LastMsgNumber uses Python identifier LastMsgNumber
    __LastMsgNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber'), 'LastMsgNumber', '__httpdocs_oasis_open_orgws_rxwsrm200702_CloseSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702LastMsgNumber', False)

    
    LastMsgNumber = property(__LastMsgNumber.value, __LastMsgNumber.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __LastMsgNumber.name() : __LastMsgNumber
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CloseSequenceType', CloseSequenceType)


# Complex type CloseSequenceResponseType with content type ELEMENT_ONLY
class CloseSequenceResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CloseSequenceResponseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_CloseSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CloseSequenceResponseType', CloseSequenceResponseType)


# Complex type TerminateSequenceType with content type ELEMENT_ONLY
class TerminateSequenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TerminateSequenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_TerminateSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}LastMsgNumber uses Python identifier LastMsgNumber
    __LastMsgNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber'), 'LastMsgNumber', '__httpdocs_oasis_open_orgws_rxwsrm200702_TerminateSequenceType_httpdocs_oasis_open_orgws_rxwsrm200702LastMsgNumber', False)

    
    LastMsgNumber = property(__LastMsgNumber.value, __LastMsgNumber.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __LastMsgNumber.name() : __LastMsgNumber
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TerminateSequenceType', TerminateSequenceType)


# Complex type TerminateSequenceResponseType with content type ELEMENT_ONLY
class TerminateSequenceResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TerminateSequenceResponseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_TerminateSequenceResponseType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TerminateSequenceResponseType', TerminateSequenceResponseType)


# Complex type OfferType with content type ELEMENT_ONLY
class OfferType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'OfferType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_OfferType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Endpoint uses Python identifier Endpoint
    __Endpoint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Endpoint'), 'Endpoint', '__httpdocs_oasis_open_orgws_rxwsrm200702_OfferType_httpdocs_oasis_open_orgws_rxwsrm200702Endpoint', False)

    
    Endpoint = property(__Endpoint.value, __Endpoint.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgws_rxwsrm200702_OfferType_httpdocs_oasis_open_orgws_rxwsrm200702Expires', False)

    
    Expires = property(__Expires.value, __Expires.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}IncompleteSequenceBehavior uses Python identifier IncompleteSequenceBehavior
    __IncompleteSequenceBehavior = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'), 'IncompleteSequenceBehavior', '__httpdocs_oasis_open_orgws_rxwsrm200702_OfferType_httpdocs_oasis_open_orgws_rxwsrm200702IncompleteSequenceBehavior', False)

    
    IncompleteSequenceBehavior = property(__IncompleteSequenceBehavior.value, __IncompleteSequenceBehavior.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __Endpoint.name() : __Endpoint,
        __Expires.name() : __Expires,
        __IncompleteSequenceBehavior.name() : __IncompleteSequenceBehavior
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'OfferType', OfferType)


# Complex type SequenceType with content type ELEMENT_ONLY
class SequenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SequenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_SequenceType_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}MessageNumber uses Python identifier MessageNumber
    __MessageNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MessageNumber'), 'MessageNumber', '__httpdocs_oasis_open_orgws_rxwsrm200702_SequenceType_httpdocs_oasis_open_orgws_rxwsrm200702MessageNumber', False)

    
    MessageNumber = property(__MessageNumber.value, __MessageNumber.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __MessageNumber.name() : __MessageNumber
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SequenceType', SequenceType)


# Complex type CTD_ANON_5 with content type EMPTY
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_6 with content type EMPTY
class CTD_ANON_6 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_7 with content type ELEMENT_ONLY
class CTD_ANON_7 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_7_httpdocs_oasis_open_orgws_rxwsrm200702Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Final uses Python identifier Final
    __Final = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Final'), 'Final', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_7_httpdocs_oasis_open_orgws_rxwsrm200702Final', False)

    
    Final = property(__Final.value, __Final.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}AcknowledgementRange uses Python identifier AcknowledgementRange
    __AcknowledgementRange = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AcknowledgementRange'), 'AcknowledgementRange', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_7_httpdocs_oasis_open_orgws_rxwsrm200702AcknowledgementRange', True)

    
    AcknowledgementRange = property(__AcknowledgementRange.value, __AcknowledgementRange.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}Nack uses Python identifier Nack
    __Nack = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Nack'), 'Nack', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_7_httpdocs_oasis_open_orgws_rxwsrm200702Nack', True)

    
    Nack = property(__Nack.value, __Nack.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}None uses Python identifier None_
    __None = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'None'), 'None_', '__httpdocs_oasis_open_orgws_rxwsrm200702_CTD_ANON_7_httpdocs_oasis_open_orgws_rxwsrm200702None', False)

    
    None_ = property(__None.value, __None.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __Identifier.name() : __Identifier,
        __Final.name() : __Final,
        __AcknowledgementRange.name() : __AcknowledgementRange,
        __Nack.name() : __Nack,
        __None.name() : __None
    }
    _AttributeMap = {
        
    }



# Complex type AcceptType with content type ELEMENT_ONLY
class AcceptType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AcceptType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-rx/wsrm/200702}AcksTo uses Python identifier AcksTo
    __AcksTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'), 'AcksTo', '__httpdocs_oasis_open_orgws_rxwsrm200702_AcceptType_httpdocs_oasis_open_orgws_rxwsrm200702AcksTo', False)

    
    AcksTo = property(__AcksTo.value, __AcksTo.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))
    _HasWildcardElement = True

    _ElementMap = {
        __AcksTo.name() : __AcksTo
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AcceptType', AcceptType)


# Complex type CTD_ANON_8 with content type EMPTY
class CTD_ANON_8 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_9 with content type EMPTY
class CTD_ANON_9 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



AckRequested = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AckRequested'), AckRequestedType)
Namespace.addCategoryObject('elementBinding', AckRequested.name().localName(), AckRequested)

Identifier = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', Identifier.name().localName(), Identifier)

Address = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Address'), CTD_ANON_4)
Namespace.addCategoryObject('elementBinding', Address.name().localName(), Address)

AcksTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'), pyxb.bundles.wssplat.wsa.EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', AcksTo.name().localName(), AcksTo)

SequenceFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SequenceFault'), SequenceFaultType)
Namespace.addCategoryObject('elementBinding', SequenceFault.name().localName(), SequenceFault)

CreateSequence = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreateSequence'), CreateSequenceType)
Namespace.addCategoryObject('elementBinding', CreateSequence.name().localName(), CreateSequence)

CreateSequenceResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreateSequenceResponse'), CreateSequenceResponseType)
Namespace.addCategoryObject('elementBinding', CreateSequenceResponse.name().localName(), CreateSequenceResponse)

CloseSequence = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CloseSequence'), CloseSequenceType)
Namespace.addCategoryObject('elementBinding', CloseSequence.name().localName(), CloseSequence)

CloseSequenceResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CloseSequenceResponse'), CloseSequenceResponseType)
Namespace.addCategoryObject('elementBinding', CloseSequenceResponse.name().localName(), CloseSequenceResponse)

TerminateSequence = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TerminateSequence'), TerminateSequenceType)
Namespace.addCategoryObject('elementBinding', TerminateSequence.name().localName(), TerminateSequence)

TerminateSequenceResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TerminateSequenceResponse'), TerminateSequenceResponseType)
Namespace.addCategoryObject('elementBinding', TerminateSequenceResponse.name().localName(), TerminateSequenceResponse)

Expires = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_1)
Namespace.addCategoryObject('elementBinding', Expires.name().localName(), Expires)

Sequence = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Sequence'), SequenceType)
Namespace.addCategoryObject('elementBinding', Sequence.name().localName(), Sequence)

UsesSequenceSTR = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UsesSequenceSTR'), CTD_ANON_5)
Namespace.addCategoryObject('elementBinding', UsesSequenceSTR.name().localName(), UsesSequenceSTR)

UsesSequenceSSL = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UsesSequenceSSL'), CTD_ANON_6)
Namespace.addCategoryObject('elementBinding', UsesSequenceSSL.name().localName(), UsesSequenceSSL)

SequenceAcknowledgement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SequenceAcknowledgement'), CTD_ANON_7)
Namespace.addCategoryObject('elementBinding', SequenceAcknowledgement.name().localName(), SequenceAcknowledgement)

UnsupportedElement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnsupportedElement'), STD_ANON_1)
Namespace.addCategoryObject('elementBinding', UnsupportedElement.name().localName(), UnsupportedElement)



AckRequestedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_2, scope=AckRequestedType))
AckRequestedType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AckRequestedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})


DetailType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})



SequenceFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FaultCode'), FaultCodes, scope=SequenceFaultType))

SequenceFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Detail'), DetailType, scope=SequenceFaultType))
SequenceFaultType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SequenceFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FaultCode'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SequenceFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Detail'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})



CreateSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CreateSequenceType))

CreateSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_1, scope=CreateSequenceType))

CreateSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Offer'), OfferType, scope=CreateSequenceType))
CreateSequenceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CreateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CreateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CreateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Offer'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CreateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Offer'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})



CreateSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_2, scope=CreateSequenceResponseType))

CreateSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_1, scope=CreateSequenceResponseType))

CreateSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'), IncompleteSequenceBehaviorType, scope=CreateSequenceResponseType))

CreateSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Accept'), AcceptType, scope=CreateSequenceResponseType))
CreateSequenceResponseType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Accept'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Accept'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CreateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Accept'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})



CloseSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_2, scope=CloseSequenceType))

CloseSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber'), MessageNumberType, scope=CloseSequenceType))
CloseSequenceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CloseSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CloseSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})



CloseSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_2, scope=CloseSequenceResponseType))
CloseSequenceResponseType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CloseSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})



TerminateSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_2, scope=TerminateSequenceType))

TerminateSequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber'), MessageNumberType, scope=TerminateSequenceType))
TerminateSequenceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TerminateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TerminateSequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LastMsgNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})



TerminateSequenceResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_2, scope=TerminateSequenceResponseType))
TerminateSequenceResponseType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TerminateSequenceResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})



OfferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_2, scope=OfferType))

OfferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Endpoint'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=OfferType))

OfferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_1, scope=OfferType))

OfferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'), IncompleteSequenceBehaviorType, scope=OfferType))
OfferType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=OfferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=OfferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Endpoint'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=OfferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=OfferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=OfferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IncompleteSequenceBehavior'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})



SequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_2, scope=SequenceType))

SequenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MessageNumber'), MessageNumberType, scope=SequenceType))
SequenceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SequenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MessageNumber'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})



CTD_ANON_7._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_2, scope=CTD_ANON_7))

CTD_ANON_7._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Final'), CTD_ANON_9, scope=CTD_ANON_7))

CTD_ANON_7._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AcknowledgementRange'), CTD_ANON_3, scope=CTD_ANON_7))

CTD_ANON_7._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Nack'), pyxb.binding.datatypes.unsignedLong, scope=CTD_ANON_7))

CTD_ANON_7._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'None'), CTD_ANON_8, scope=CTD_ANON_7))
CTD_ANON_7._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AcknowledgementRange'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Nack'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'None'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AcknowledgementRange'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Final'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Nack'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Final'))),
    ])
})



AcceptType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=AcceptType))
AcceptType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AcceptType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AcksTo'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-rx/wsrm/200702'))),
    ])
})
