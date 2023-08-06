# ./pyxb/bundles/wssplat/raw/wscoor.py
# PyXB bindings for NamespaceModule
# NSM:53926fc38ff5e8ef8d845111c1f3663a73eea53c
# Generated 2009-11-30 18:08:52.732156 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:b556fac8-de0d-11de-b4d0-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsa

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06', create_if_missing=True)
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
class ErrorCodes (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ErrorCodes')
    _Documentation = None
ErrorCodes._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ErrorCodes, enum_prefix=None)
ErrorCodes.wscoorInvalidParameters = ErrorCodes._CF_enumeration.addEnumeration(unicode_value=u'wscoor:InvalidParameters')
ErrorCodes.wscoorInvalidProtocol = ErrorCodes._CF_enumeration.addEnumeration(unicode_value=u'wscoor:InvalidProtocol')
ErrorCodes.wscoorInvalidState = ErrorCodes._CF_enumeration.addEnumeration(unicode_value=u'wscoor:InvalidState')
ErrorCodes.wscoorCannotCreateContext = ErrorCodes._CF_enumeration.addEnumeration(unicode_value=u'wscoor:CannotCreateContext')
ErrorCodes.wscoorCannotRegisterParticipant = ErrorCodes._CF_enumeration.addEnumeration(unicode_value=u'wscoor:CannotRegisterParticipant')
ErrorCodes._InitializeFacetMap(ErrorCodes._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'ErrorCodes', ErrorCodes)

# Complex type CoordinationContextType with content type ELEMENT_ONLY
class CoordinationContextType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CoordinationContextType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}RegistrationService uses Python identifier RegistrationService
    __RegistrationService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RegistrationService'), 'RegistrationService', '__httpdocs_oasis_open_orgws_txwscoor200606_CoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606RegistrationService', False)

    
    RegistrationService = property(__RegistrationService.value, __RegistrationService.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_txwscoor200606_CoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606Identifier', False)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgws_txwscoor200606_CoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606Expires', False)

    
    Expires = property(__Expires.value, __Expires.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationType uses Python identifier CoordinationType
    __CoordinationType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'), 'CoordinationType', '__httpdocs_oasis_open_orgws_txwscoor200606_CoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606CoordinationType', False)

    
    CoordinationType = property(__CoordinationType.value, __CoordinationType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))

    _ElementMap = {
        __RegistrationService.name() : __RegistrationService,
        __Identifier.name() : __Identifier,
        __Expires.name() : __Expires,
        __CoordinationType.name() : __CoordinationType
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CoordinationContextType', CoordinationContextType)


# Complex type CTD_ANON_1 with content type ELEMENT_ONLY
class CTD_ANON_1 (CoordinationContextType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is CoordinationContextType
    
    # Element RegistrationService ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}RegistrationService) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element Identifier ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Identifier) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element Expires ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Expires) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element CoordinationType ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationType) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = CoordinationContextType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = CoordinationContextType._AttributeMap.copy()
    _AttributeMap.update({
        
    })



# Complex type CTD_ANON_2 with content type SIMPLE
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.unsignedInt
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.unsignedInt
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_3 with content type SIMPLE
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyURI
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type RegisterResponseType with content type ELEMENT_ONLY
class RegisterResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RegisterResponseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinatorProtocolService uses Python identifier CoordinatorProtocolService
    __CoordinatorProtocolService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CoordinatorProtocolService'), 'CoordinatorProtocolService', '__httpdocs_oasis_open_orgws_txwscoor200606_RegisterResponseType_httpdocs_oasis_open_orgws_txwscoor200606CoordinatorProtocolService', False)

    
    CoordinatorProtocolService = property(__CoordinatorProtocolService.value, __CoordinatorProtocolService.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = {
        __CoordinatorProtocolService.name() : __CoordinatorProtocolService
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'RegisterResponseType', RegisterResponseType)


# Complex type CreateCoordinationContextResponseType with content type ELEMENT_ONLY
class CreateCoordinationContextResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CreateCoordinationContextResponseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContext uses Python identifier CoordinationContext
    __CoordinationContext = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CoordinationContext'), 'CoordinationContext', '__httpdocs_oasis_open_orgws_txwscoor200606_CreateCoordinationContextResponseType_httpdocs_oasis_open_orgws_txwscoor200606CoordinationContext', False)

    
    CoordinationContext = property(__CoordinationContext.value, __CoordinationContext.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = {
        __CoordinationContext.name() : __CoordinationContext
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CreateCoordinationContextResponseType', CreateCoordinationContextResponseType)


# Complex type CTD_ANON_4 with content type ELEMENT_ONLY
class CTD_ANON_4 (CoordinationContextType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is CoordinationContextType
    
    # Element RegistrationService ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}RegistrationService) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element Identifier ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Identifier) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element Expires ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Expires) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element CoordinationType ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationType) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = CoordinationContextType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = CoordinationContextType._AttributeMap.copy()
    _AttributeMap.update({
        
    })



# Complex type CreateCoordinationContextType with content type ELEMENT_ONLY
class CreateCoordinationContextType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CreateCoordinationContextType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgws_txwscoor200606_CreateCoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606Expires', False)

    
    Expires = property(__Expires.value, __Expires.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CurrentContext uses Python identifier CurrentContext
    __CurrentContext = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CurrentContext'), 'CurrentContext', '__httpdocs_oasis_open_orgws_txwscoor200606_CreateCoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606CurrentContext', False)

    
    CurrentContext = property(__CurrentContext.value, __CurrentContext.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationType uses Python identifier CoordinationType
    __CoordinationType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'), 'CoordinationType', '__httpdocs_oasis_open_orgws_txwscoor200606_CreateCoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606CoordinationType', False)

    
    CoordinationType = property(__CoordinationType.value, __CoordinationType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = {
        __Expires.name() : __Expires,
        __CurrentContext.name() : __CurrentContext,
        __CoordinationType.name() : __CoordinationType
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CreateCoordinationContextType', CreateCoordinationContextType)


# Complex type RegisterType with content type ELEMENT_ONLY
class RegisterType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RegisterType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}ProtocolIdentifier uses Python identifier ProtocolIdentifier
    __ProtocolIdentifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ProtocolIdentifier'), 'ProtocolIdentifier', '__httpdocs_oasis_open_orgws_txwscoor200606_RegisterType_httpdocs_oasis_open_orgws_txwscoor200606ProtocolIdentifier', False)

    
    ProtocolIdentifier = property(__ProtocolIdentifier.value, __ProtocolIdentifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}ParticipantProtocolService uses Python identifier ParticipantProtocolService
    __ParticipantProtocolService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ParticipantProtocolService'), 'ParticipantProtocolService', '__httpdocs_oasis_open_orgws_txwscoor200606_RegisterType_httpdocs_oasis_open_orgws_txwscoor200606ParticipantProtocolService', False)

    
    ParticipantProtocolService = property(__ParticipantProtocolService.value, __ParticipantProtocolService.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = {
        __ProtocolIdentifier.name() : __ProtocolIdentifier,
        __ParticipantProtocolService.name() : __ParticipantProtocolService
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'RegisterType', RegisterType)


Expires = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', Expires.name().localName(), Expires)

RegisterResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RegisterResponse'), RegisterResponseType)
Namespace.addCategoryObject('elementBinding', RegisterResponse.name().localName(), RegisterResponse)

CreateCoordinationContextResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreateCoordinationContextResponse'), CreateCoordinationContextResponseType)
Namespace.addCategoryObject('elementBinding', CreateCoordinationContextResponse.name().localName(), CreateCoordinationContextResponse)

CoordinationContext = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CoordinationContext'), CTD_ANON_4)
Namespace.addCategoryObject('elementBinding', CoordinationContext.name().localName(), CoordinationContext)

CreateCoordinationContext = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreateCoordinationContext'), CreateCoordinationContextType)
Namespace.addCategoryObject('elementBinding', CreateCoordinationContext.name().localName(), CreateCoordinationContext)

Register = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Register'), RegisterType)
Namespace.addCategoryObject('elementBinding', Register.name().localName(), Register)



CoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RegistrationService'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CoordinationContextType))

CoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_3, scope=CoordinationContextType))

CoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_2, scope=CoordinationContextType))

CoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'), pyxb.binding.datatypes.anyURI, scope=CoordinationContextType))
CoordinationContextType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RegistrationService'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
    ])
})


CTD_ANON_1._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_1._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_1._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_1._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_1._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RegistrationService'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_1._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'))),
    ])
})



RegisterResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CoordinatorProtocolService'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=RegisterResponseType))
RegisterResponseType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RegisterResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinatorProtocolService'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})



CreateCoordinationContextResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CoordinationContext'), CTD_ANON_4, scope=CreateCoordinationContextResponseType))
CreateCoordinationContextResponseType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CreateCoordinationContextResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationContext'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))),
    ])
})


CTD_ANON_4._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RegistrationService'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'))),
    ])
})



CreateCoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON_2, scope=CreateCoordinationContextType))

CreateCoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CurrentContext'), CTD_ANON_1, scope=CreateCoordinationContextType))

CreateCoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'), pyxb.binding.datatypes.anyURI, scope=CreateCoordinationContextType))
CreateCoordinationContextType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CreateCoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CreateCoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CreateCoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CurrentContext'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CreateCoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CreateCoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CurrentContext'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CreateCoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'))),
    ])
})



RegisterType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProtocolIdentifier'), pyxb.binding.datatypes.anyURI, scope=RegisterType))

RegisterType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ParticipantProtocolService'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=RegisterType))
RegisterType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RegisterType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ProtocolIdentifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RegisterType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ParticipantProtocolService'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})
