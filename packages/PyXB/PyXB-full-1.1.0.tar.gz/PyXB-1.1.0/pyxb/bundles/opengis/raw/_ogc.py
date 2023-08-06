# ./pyxb/bundles/opengis/raw/_ogc.py
# PyXB bindings for NamespaceModule
# NSM:5b31a14669a98cd6cc4f3673117954e87b7d869b
# Generated 2009-11-30 18:10:59.174645 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:fe297000-de0d-11de-9bb5-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.filter
import pyxb.bundles.opengis.gml

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/ogc', create_if_missing=True)
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
class TemporalOperatorNameType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TemporalOperatorNameType')
    _Documentation = None
TemporalOperatorNameType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TemporalOperatorNameType, enum_prefix=None)
TemporalOperatorNameType.TM_After = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_After')
TemporalOperatorNameType.TM_Before = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_Before')
TemporalOperatorNameType.TM_Begins = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_Begins')
TemporalOperatorNameType.TM_BegunBy = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_BegunBy')
TemporalOperatorNameType.TM_Contains = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_Contains')
TemporalOperatorNameType.TM_During = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_During')
TemporalOperatorNameType.TM_Equals = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_Equals')
TemporalOperatorNameType.TM_Overlaps = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_Overlaps')
TemporalOperatorNameType.TM_Meets = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_Meets')
TemporalOperatorNameType.TM_OverlappedBy = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_OverlappedBy')
TemporalOperatorNameType.TM_MetBy = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_MetBy')
TemporalOperatorNameType.TM_EndedBy = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_EndedBy')
TemporalOperatorNameType.TM_Ends = TemporalOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'TM_Ends')
TemporalOperatorNameType._InitializeFacetMap(TemporalOperatorNameType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'TemporalOperatorNameType', TemporalOperatorNameType)

# Atomic SimpleTypeDefinition
class TemporalOperandType (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TemporalOperandType')
    _Documentation = None
TemporalOperandType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TemporalOperandType, enum_prefix=None)
TemporalOperandType.gmlvalidTime = TemporalOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:validTime')
TemporalOperandType.gmlTimeInstant = TemporalOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:TimeInstant')
TemporalOperandType.gmlTimePeriod = TemporalOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:TimePeriod')
TemporalOperandType.gmltimePosition = TemporalOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:timePosition')
TemporalOperandType.gmltimeInterval = TemporalOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:timeInterval')
TemporalOperandType.gmlduration = TemporalOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:duration')
TemporalOperandType._InitializeFacetMap(TemporalOperandType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'TemporalOperandType', TemporalOperandType)

# Complex type TemporalOpsType with content type EMPTY
class TemporalOpsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TemporalOpsType')
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TemporalOpsType', TemporalOpsType)


# Complex type BinaryTemporalOpType with content type ELEMENT_ONLY
class BinaryTemporalOpType (TemporalOpsType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BinaryTemporalOpType')
    # Base type is TemporalOpsType
    
    # Element {http://www.opengis.net/ogc}PropertyName uses Python identifier PropertyName
    __PropertyName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), 'PropertyName', '__httpwww_opengis_netogc_BinaryTemporalOpType_httpwww_opengis_netogcPropertyName', True)

    
    PropertyName = property(__PropertyName.value, __PropertyName.set, None, None)

    
    # Element {http://www.opengis.net/gml}_TimeObject uses Python identifier TimeObject
    __TimeObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_TimeObject'), 'TimeObject', '__httpwww_opengis_netogc_BinaryTemporalOpType_httpwww_opengis_netgml_TimeObject', False)

    
    TimeObject = property(__TimeObject.value, __TimeObject.set, None, u'This abstract element acts as the head of the substitution group for temporal primitives and complexes.')


    _ElementMap = TemporalOpsType._ElementMap.copy()
    _ElementMap.update({
        __PropertyName.name() : __PropertyName,
        __TimeObject.name() : __TimeObject
    })
    _AttributeMap = TemporalOpsType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BinaryTemporalOpType', BinaryTemporalOpType)


# Complex type TemporalOperatorType with content type ELEMENT_ONLY
class TemporalOperatorType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TemporalOperatorType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}TemporalOperands uses Python identifier TemporalOperands
    __TemporalOperands = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperands'), 'TemporalOperands', '__httpwww_opengis_netogc_TemporalOperatorType_httpwww_opengis_netogcTemporalOperands', False)

    
    TemporalOperands = property(__TemporalOperands.value, __TemporalOperands.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netogc_TemporalOperatorType_name', TemporalOperatorNameType)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        __TemporalOperands.name() : __TemporalOperands
    }
    _AttributeMap = {
        __name.name() : __name
    }
Namespace.addCategoryObject('typeBinding', u'TemporalOperatorType', TemporalOperatorType)


# Complex type Temporal_CapabilitiesType with content type ELEMENT_ONLY
class Temporal_CapabilitiesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Temporal_CapabilitiesType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}TemporalOperators uses Python identifier TemporalOperators
    __TemporalOperators = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperators'), 'TemporalOperators', '__httpwww_opengis_netogc_Temporal_CapabilitiesType_httpwww_opengis_netogcTemporalOperators', False)

    
    TemporalOperators = property(__TemporalOperators.value, __TemporalOperators.set, None, None)

    
    # Element {http://www.opengis.net/ogc}TemporalOperands uses Python identifier TemporalOperands
    __TemporalOperands = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperands'), 'TemporalOperands', '__httpwww_opengis_netogc_Temporal_CapabilitiesType_httpwww_opengis_netogcTemporalOperands', False)

    
    TemporalOperands = property(__TemporalOperands.value, __TemporalOperands.set, None, None)


    _ElementMap = {
        __TemporalOperators.name() : __TemporalOperators,
        __TemporalOperands.name() : __TemporalOperands
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Temporal_CapabilitiesType', Temporal_CapabilitiesType)


# Complex type TemporalOperandsType with content type ELEMENT_ONLY
class TemporalOperandsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TemporalOperandsType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}TemporalOperand uses Python identifier TemporalOperand
    __TemporalOperand = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperand'), 'TemporalOperand', '__httpwww_opengis_netogc_TemporalOperandsType_httpwww_opengis_netogcTemporalOperand', True)

    
    TemporalOperand = property(__TemporalOperand.value, __TemporalOperand.set, None, None)


    _ElementMap = {
        __TemporalOperand.name() : __TemporalOperand
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TemporalOperandsType', TemporalOperandsType)


# Complex type TemporalOperatorsType with content type ELEMENT_ONLY
class TemporalOperatorsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TemporalOperatorsType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}TemporalOperator uses Python identifier TemporalOperator
    __TemporalOperator = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperator'), 'TemporalOperator', '__httpwww_opengis_netogc_TemporalOperatorsType_httpwww_opengis_netogcTemporalOperator', True)

    
    TemporalOperator = property(__TemporalOperator.value, __TemporalOperator.set, None, None)


    _ElementMap = {
        __TemporalOperator.name() : __TemporalOperator
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TemporalOperatorsType', TemporalOperatorsType)


TM_Ends = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_Ends'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_Ends.name().localName(), TM_Ends)

TM_Equals = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_Equals'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_Equals.name().localName(), TM_Equals)

TM_After = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_After'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_After.name().localName(), TM_After)

TM_Overalps = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_Overalps'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_Overalps.name().localName(), TM_Overalps)

Temporal_Capabilities = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Temporal_Capabilities'), Temporal_CapabilitiesType)
Namespace.addCategoryObject('elementBinding', Temporal_Capabilities.name().localName(), Temporal_Capabilities)

TM_Before = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_Before'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_Before.name().localName(), TM_Before)

Id_Capabilities = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Id_Capabilities'), pyxb.bundles.opengis.filter.Id_CapabilitiesType)
Namespace.addCategoryObject('elementBinding', Id_Capabilities.name().localName(), Id_Capabilities)

TM_Begins = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_Begins'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_Begins.name().localName(), TM_Begins)

TM_EndedBy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_EndedBy'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_EndedBy.name().localName(), TM_EndedBy)

TM_MetBy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_MetBy'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_MetBy.name().localName(), TM_MetBy)

TM_Contains = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_Contains'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_Contains.name().localName(), TM_Contains)

TM_During = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_During'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_During.name().localName(), TM_During)

temporalOps = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'temporalOps'), TemporalOpsType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', temporalOps.name().localName(), temporalOps)

Scalar_Capabilities = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Scalar_Capabilities'), pyxb.bundles.opengis.filter.Scalar_CapabilitiesType)
Namespace.addCategoryObject('elementBinding', Scalar_Capabilities.name().localName(), Scalar_Capabilities)

TM_OverlappedBy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_OverlappedBy'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_OverlappedBy.name().localName(), TM_OverlappedBy)

TM_Meets = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_Meets'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_Meets.name().localName(), TM_Meets)

TM_BegunBy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TM_BegunBy'), BinaryTemporalOpType)
Namespace.addCategoryObject('elementBinding', TM_BegunBy.name().localName(), TM_BegunBy)

Spatial_Capabilities = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Spatial_Capabilities'), pyxb.bundles.opengis.filter.Spatial_CapabilitiesType)
Namespace.addCategoryObject('elementBinding', Spatial_Capabilities.name().localName(), Spatial_Capabilities)



BinaryTemporalOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), pyxb.bundles.opengis.filter.PropertyNameType, scope=BinaryTemporalOpType))

BinaryTemporalOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_TimeObject'), pyxb.bundles.opengis.gml.AbstractTimeObjectType, abstract=pyxb.binding.datatypes.boolean(1), scope=BinaryTemporalOpType, documentation=u'This abstract element acts as the head of the substitution group for temporal primitives and complexes.'))
BinaryTemporalOpType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BinaryTemporalOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinaryTemporalOpType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_TimeObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinaryTemporalOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



TemporalOperatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperands'), TemporalOperandsType, scope=TemporalOperatorType))
TemporalOperatorType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TemporalOperatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperands'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



Temporal_CapabilitiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperators'), TemporalOperatorsType, scope=Temporal_CapabilitiesType))

Temporal_CapabilitiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperands'), TemporalOperandsType, scope=Temporal_CapabilitiesType))
Temporal_CapabilitiesType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Temporal_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperands'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Temporal_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperators'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



TemporalOperandsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperand'), TemporalOperandType, scope=TemporalOperandsType))
TemporalOperandsType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TemporalOperandsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperand'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TemporalOperandsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperand'))),
    ])
})



TemporalOperatorsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperator'), TemporalOperatorType, scope=TemporalOperatorsType))
TemporalOperatorsType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TemporalOperatorsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperator'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TemporalOperatorsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TemporalOperator'))),
    ])
})

TM_Ends._setSubstitutionGroup(temporalOps)

TM_Equals._setSubstitutionGroup(temporalOps)

TM_After._setSubstitutionGroup(temporalOps)

TM_Overalps._setSubstitutionGroup(temporalOps)

TM_Before._setSubstitutionGroup(temporalOps)

TM_Begins._setSubstitutionGroup(temporalOps)

TM_EndedBy._setSubstitutionGroup(temporalOps)

TM_MetBy._setSubstitutionGroup(temporalOps)

TM_Contains._setSubstitutionGroup(temporalOps)

TM_During._setSubstitutionGroup(temporalOps)

TM_OverlappedBy._setSubstitutionGroup(temporalOps)

TM_Meets._setSubstitutionGroup(temporalOps)

TM_BegunBy._setSubstitutionGroup(temporalOps)
