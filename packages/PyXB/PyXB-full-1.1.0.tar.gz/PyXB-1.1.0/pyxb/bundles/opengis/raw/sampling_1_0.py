# ./pyxb/bundles/opengis/raw/sampling_1_0.py
# PyXB bindings for NamespaceModule
# NSM:090788a666183117c942ebaf2d5667f8b0b3eeca
# Generated 2009-11-30 18:11:04.247776 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:01ab7a66-de0e-11de-b9a7-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.gml
import pyxb.bundles.opengis.misc.xlinks
import pyxb.bundles.opengis.om_1_0

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/sampling/1.0', create_if_missing=True)
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
class STD_ANON_1 (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_1._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_1, enum_prefix=None)
STD_ANON_1.geometryLocation = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'geometryLocation')
STD_ANON_1.nameLocation = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'nameLocation')
STD_ANON_1._InitializeFacetMap(STD_ANON_1._CF_enumeration)

# Complex type SamplingFeaturePropertyType with content type ELEMENT_ONLY
class SamplingFeaturePropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingFeaturePropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}SamplingFeature uses Python identifier SamplingFeature
    __SamplingFeature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeature'), 'SamplingFeature', '__httpwww_opengis_netsampling1_0_SamplingFeaturePropertyType_httpwww_opengis_netsampling1_0SamplingFeature', False)

    
    SamplingFeature = property(__SamplingFeature.value, __SamplingFeature.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_SamplingFeaturePropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_SamplingFeaturePropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_SamplingFeaturePropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_SamplingFeaturePropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_SamplingFeaturePropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_SamplingFeaturePropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_SamplingFeaturePropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_SamplingFeaturePropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __SamplingFeature.name() : __SamplingFeature
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __title.name() : __title,
        __actuate.name() : __actuate,
        __role.name() : __role,
        __type.name() : __type
    }
Namespace.addCategoryObject('typeBinding', u'SamplingFeaturePropertyType', SamplingFeaturePropertyType)


# Complex type SamplingFeatureRelationType with content type ELEMENT_ONLY
class SamplingFeatureRelationType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureRelationType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}target uses Python identifier target
    __target = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'target'), 'target', '__httpwww_opengis_netsampling1_0_SamplingFeatureRelationType_httpwww_opengis_netsampling1_0target', False)

    
    target = property(__target.value, __target.set, None, None)

    
    # Element {http://www.opengis.net/sampling/1.0}role uses Python identifier role
    __role = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'role'), 'role', '__httpwww_opengis_netsampling1_0_SamplingFeatureRelationType_httpwww_opengis_netsampling1_0role', False)

    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        __target.name() : __target,
        __role.name() : __role
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SamplingFeatureRelationType', SamplingFeatureRelationType)


# Complex type AnyOrReferenceType with content type ELEMENT_ONLY
class AnyOrReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AnyOrReferenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_AnyOrReferenceType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_AnyOrReferenceType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_AnyOrReferenceType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_AnyOrReferenceType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_AnyOrReferenceType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_AnyOrReferenceType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_AnyOrReferenceType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_AnyOrReferenceType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __href.name() : __href,
        __remoteSchema.name() : __remoteSchema,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __title.name() : __title,
        __role.name() : __role,
        __actuate.name() : __actuate,
        __type.name() : __type
    }
Namespace.addCategoryObject('typeBinding', u'AnyOrReferenceType', AnyOrReferenceType)


# Complex type SamplingFeatureType with content type ELEMENT_ONLY
class SamplingFeatureType (pyxb.bundles.opengis.gml.AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureType')
    # Base type is pyxb.bundles.opengis.gml.AbstractFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sampling/1.0}surveyDetails uses Python identifier surveyDetails
    __surveyDetails = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'), 'surveyDetails', '__httpwww_opengis_netsampling1_0_SamplingFeatureType_httpwww_opengis_netsampling1_0surveyDetails', False)

    
    surveyDetails = property(__surveyDetails.value, __surveyDetails.set, None, u'A common requirement for sampling features is an indication of the SurveyProcedure \n\t\t\t\t\t\t\tthat provides the surveyDetails related to determination of its location and shape. ')

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}relatedSamplingFeature uses Python identifier relatedSamplingFeature
    __relatedSamplingFeature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'), 'relatedSamplingFeature', '__httpwww_opengis_netsampling1_0_SamplingFeatureType_httpwww_opengis_netsampling1_0relatedSamplingFeature', True)

    
    relatedSamplingFeature = property(__relatedSamplingFeature.value, __relatedSamplingFeature.set, None, u'Sampling features are frequently related to each other, as parts of complexes, networks, through sub-sampling, etc. \n\t\t\t\t\t\t\tThis is supported by the relatedSamplingFeature association with a SamplingFeatureRelation association class, which carries a source, target and role.')

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sampling/1.0}sampledFeature uses Python identifier sampledFeature
    __sampledFeature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'), 'sampledFeature', '__httpwww_opengis_netsampling1_0_SamplingFeatureType_httpwww_opengis_netsampling1_0sampledFeature', True)

    
    sampledFeature = property(__sampledFeature.value, __sampledFeature.set, None, u'A SamplingFeature must be associated with one or more other features through an association role sampledFeature. \n\t\t\t\t\t\t\tThis association records the intention of the sample design. \n\t\t\t\t\t\t\tThe target of this association will usually be a domain feature.')

    
    # Element {http://www.opengis.net/sampling/1.0}relatedObservation uses Python identifier relatedObservation
    __relatedObservation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'), 'relatedObservation', '__httpwww_opengis_netsampling1_0_SamplingFeatureType_httpwww_opengis_netsampling1_0relatedObservation', True)

    
    relatedObservation = property(__relatedObservation.value, __relatedObservation.set, None, u'A SamplingFeature is distinguished from typical domain feature types in that it has a set of [0..*] navigable associations with Observations, given the rolename relatedObservation. \n\t\t\t\t\tThis complements the association role \u201cfeatureOfInterest\u201d which is constrained to point back from the Observation to the Sampling-Feature. \n\t\t\t\t\tThe usual requirement of an Observation feature-of-interest is that its type has a property matching the observed-property on the Observation. \n\t\t\t\t\tIn the case of Sampling-features, the topology of the model and navigability of the relatedObservation role means that this requirement is satisfied automatically: \n\t\t\t\t\ta property of the sampling-feature is implied by the observedProperty of a related observation. \n\t\t\t\t\tThis effectively provides an unlimited set of \u201csoft-typed\u201d properties on a Sampling Feature.')

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        __surveyDetails.name() : __surveyDetails,
        __relatedSamplingFeature.name() : __relatedSamplingFeature,
        __sampledFeature.name() : __sampledFeature,
        __relatedObservation.name() : __relatedObservation
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SamplingFeatureType', SamplingFeatureType)


# Complex type SpatiallyExtensiveSamplingFeatureType with content type ELEMENT_ONLY
class SpatiallyExtensiveSamplingFeatureType (SamplingFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SpatiallyExtensiveSamplingFeatureType')
    # Base type is SamplingFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element surveyDetails ({http://www.opengis.net/sampling/1.0}surveyDetails) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element relatedSamplingFeature ({http://www.opengis.net/sampling/1.0}relatedSamplingFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element sampledFeature ({http://www.opengis.net/sampling/1.0}sampledFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element relatedObservation ({http://www.opengis.net/sampling/1.0}relatedObservation) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = SamplingFeatureType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = SamplingFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SpatiallyExtensiveSamplingFeatureType', SpatiallyExtensiveSamplingFeatureType)


# Complex type SamplingSolidType with content type ELEMENT_ONLY
class SamplingSolidType (SpatiallyExtensiveSamplingFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingSolidType')
    # Base type is SpatiallyExtensiveSamplingFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element surveyDetails ({http://www.opengis.net/sampling/1.0}surveyDetails) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}shape uses Python identifier shape
    __shape = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'shape'), 'shape', '__httpwww_opengis_netsampling1_0_SamplingSolidType_httpwww_opengis_netsampling1_0shape', False)

    
    shape = property(__shape.value, __shape.set, None, None)

    
    # Element relatedSamplingFeature ({http://www.opengis.net/sampling/1.0}relatedSamplingFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}volume uses Python identifier volume
    __volume = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'volume'), 'volume', '__httpwww_opengis_netsampling1_0_SamplingSolidType_httpwww_opengis_netsampling1_0volume', False)

    
    volume = property(__volume.value, __volume.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element sampledFeature ({http://www.opengis.net/sampling/1.0}sampledFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element relatedObservation ({http://www.opengis.net/sampling/1.0}relatedObservation) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = SpatiallyExtensiveSamplingFeatureType._ElementMap.copy()
    _ElementMap.update({
        __shape.name() : __shape,
        __volume.name() : __volume
    })
    _AttributeMap = SpatiallyExtensiveSamplingFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SamplingSolidType', SamplingSolidType)


# Complex type SamplingSolidPropertyType with content type ELEMENT_ONLY
class SamplingSolidPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingSolidPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}SamplingSolid uses Python identifier SamplingSolid
    __SamplingSolid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SamplingSolid'), 'SamplingSolid', '__httpwww_opengis_netsampling1_0_SamplingSolidPropertyType_httpwww_opengis_netsampling1_0SamplingSolid', False)

    
    SamplingSolid = property(__SamplingSolid.value, __SamplingSolid.set, None, u'A "SamplingSolid" is an identified 3-D spatial feature used in sampling.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_SamplingSolidPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_SamplingSolidPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_SamplingSolidPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_SamplingSolidPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_SamplingSolidPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_SamplingSolidPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_SamplingSolidPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_SamplingSolidPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")


    _ElementMap = {
        __SamplingSolid.name() : __SamplingSolid
    }
    _AttributeMap = {
        __type.name() : __type,
        __remoteSchema.name() : __remoteSchema,
        __arcrole.name() : __arcrole,
        __title.name() : __title,
        __show.name() : __show,
        __href.name() : __href,
        __role.name() : __role,
        __actuate.name() : __actuate
    }
Namespace.addCategoryObject('typeBinding', u'SamplingSolidPropertyType', SamplingSolidPropertyType)


# Complex type CTD_ANON_1 with content type SIMPLE
class CTD_ANON_1 (pyxb.bundles.opengis.gml.MeasureType):
    _TypeDefinition = pyxb.binding.datatypes.double
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.bundles.opengis.gml.MeasureType
    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_CTD_ANON_1_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute uom inherited from {http://www.opengis.net/gml}MeasureType
    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_CTD_ANON_1_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_CTD_ANON_1_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_CTD_ANON_1_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_CTD_ANON_1_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_CTD_ANON_1_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_CTD_ANON_1_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_CTD_ANON_1_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)


    _ElementMap = pyxb.bundles.opengis.gml.MeasureType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.opengis.gml.MeasureType._AttributeMap.copy()
    _AttributeMap.update({
        __remoteSchema.name() : __remoteSchema,
        __href.name() : __href,
        __title.name() : __title,
        __role.name() : __role,
        __actuate.name() : __actuate,
        __show.name() : __show,
        __type.name() : __type,
        __arcrole.name() : __arcrole
    })



# Complex type SpecimenPropertyType with content type ELEMENT_ONLY
class SpecimenPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SpecimenPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}Specimen uses Python identifier Specimen
    __Specimen = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Specimen'), 'Specimen', '__httpwww_opengis_netsampling1_0_SpecimenPropertyType_httpwww_opengis_netsampling1_0Specimen', False)

    
    Specimen = property(__Specimen.value, __Specimen.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_SpecimenPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_SpecimenPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_SpecimenPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_SpecimenPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_SpecimenPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_SpecimenPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_SpecimenPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_SpecimenPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        __Specimen.name() : __Specimen
    }
    _AttributeMap = {
        __role.name() : __role,
        __remoteSchema.name() : __remoteSchema,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __title.name() : __title,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __href.name() : __href
    }
Namespace.addCategoryObject('typeBinding', u'SpecimenPropertyType', SpecimenPropertyType)


# Complex type SamplingFeatureCollectionPropertyType with content type ELEMENT_ONLY
class SamplingFeatureCollectionPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureCollectionPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}SamplingFeatureCollection uses Python identifier SamplingFeatureCollection
    __SamplingFeatureCollection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureCollection'), 'SamplingFeatureCollection', '__httpwww_opengis_netsampling1_0_SamplingFeatureCollectionPropertyType_httpwww_opengis_netsampling1_0SamplingFeatureCollection', False)

    
    SamplingFeatureCollection = property(__SamplingFeatureCollection.value, __SamplingFeatureCollection.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_SamplingFeatureCollectionPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_SamplingFeatureCollectionPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_SamplingFeatureCollectionPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_SamplingFeatureCollectionPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_SamplingFeatureCollectionPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_SamplingFeatureCollectionPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_SamplingFeatureCollectionPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_SamplingFeatureCollectionPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __SamplingFeatureCollection.name() : __SamplingFeatureCollection
    }
    _AttributeMap = {
        __show.name() : __show,
        __remoteSchema.name() : __remoteSchema,
        __arcrole.name() : __arcrole,
        __role.name() : __role,
        __title.name() : __title,
        __actuate.name() : __actuate,
        __href.name() : __href,
        __type.name() : __type
    }
Namespace.addCategoryObject('typeBinding', u'SamplingFeatureCollectionPropertyType', SamplingFeatureCollectionPropertyType)


# Complex type SpecimenType with content type ELEMENT_ONLY
class SpecimenType (SamplingFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SpecimenType')
    # Base type is SamplingFeatureType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element relatedSamplingFeature ({http://www.opengis.net/sampling/1.0}relatedSamplingFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}samplingTime uses Python identifier samplingTime
    __samplingTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'samplingTime'), 'samplingTime', '__httpwww_opengis_netsampling1_0_SpecimenType_httpwww_opengis_netsampling1_0samplingTime', False)

    
    samplingTime = property(__samplingTime.value, __samplingTime.set, None, u'Time and date when the specimen was initially retrieved')

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element sampledFeature ({http://www.opengis.net/sampling/1.0}sampledFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}materialClass uses Python identifier materialClass
    __materialClass = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'materialClass'), 'materialClass', '__httpwww_opengis_netsampling1_0_SpecimenType_httpwww_opengis_netsampling1_0materialClass', False)

    
    materialClass = property(__materialClass.value, __materialClass.set, None, u'Material type, usually taken from a controlled vocabulary\n\t\t\t\t\tSpecialised domains may choose to fix the vocabulary to be used\n\t\t\t\t\tIts value may be relatively generic (rock, pulp) or may reflect a detailed classification (calcrete, adamellite, biotite-schist). \n\t\t\tIn the latter case it is wise to use the codeSpace attribute to provide a link to the classification scheme/vocabulary used. \n')

    
    # Element {http://www.opengis.net/sampling/1.0}processingDetails uses Python identifier processingDetails
    __processingDetails = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'processingDetails'), 'processingDetails', '__httpwww_opengis_netsampling1_0_SpecimenType_httpwww_opengis_netsampling1_0processingDetails', True)

    
    processingDetails = property(__processingDetails.value, __processingDetails.set, None, u'One or more procedures may have been applied to a specimen.  \n            May contain collection, sampling and preparation procedures')

    
    # Element {http://www.opengis.net/sampling/1.0}size uses Python identifier size
    __size = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'size'), 'size', '__httpwww_opengis_netsampling1_0_SpecimenType_httpwww_opengis_netsampling1_0size', False)

    
    size = property(__size.value, __size.set, None, u'The size of the specimen: mass, length, volume, etc')

    
    # Element {http://www.opengis.net/sampling/1.0}samplingMethod uses Python identifier samplingMethod
    __samplingMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'samplingMethod'), 'samplingMethod', '__httpwww_opengis_netsampling1_0_SpecimenType_httpwww_opengis_netsampling1_0samplingMethod', False)

    
    samplingMethod = property(__samplingMethod.value, __samplingMethod.set, None, u'Method used when retrieving specimen from host sampledFeature')

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element surveyDetails ({http://www.opengis.net/sampling/1.0}surveyDetails) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element relatedObservation ({http://www.opengis.net/sampling/1.0}relatedObservation) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}currentLocation uses Python identifier currentLocation
    __currentLocation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'currentLocation'), 'currentLocation', '__httpwww_opengis_netsampling1_0_SpecimenType_httpwww_opengis_netsampling1_0currentLocation', False)

    
    currentLocation = property(__currentLocation.value, __currentLocation.set, None, u'Storage location of specimen if it still exists. If destroyed in analysis, then either omit or use xlink:href to point to a suitable URN, e.g. urn:cgi:def:nil:destroyed')

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = SamplingFeatureType._ElementMap.copy()
    _ElementMap.update({
        __samplingTime.name() : __samplingTime,
        __materialClass.name() : __materialClass,
        __processingDetails.name() : __processingDetails,
        __size.name() : __size,
        __samplingMethod.name() : __samplingMethod,
        __currentLocation.name() : __currentLocation
    })
    _AttributeMap = SamplingFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SpecimenType', SpecimenType)


# Complex type LocatedSpecimenType with content type ELEMENT_ONLY
class LocatedSpecimenType (SpecimenType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LocatedSpecimenType')
    # Base type is SpecimenType
    
    # Element samplingMethod ({http://www.opengis.net/sampling/1.0}samplingMethod) inherited from {http://www.opengis.net/sampling/1.0}SpecimenType
    
    # Element {http://www.opengis.net/sampling/1.0}samplingLocation uses Python identifier samplingLocation
    __samplingLocation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'samplingLocation'), 'samplingLocation', '__httpwww_opengis_netsampling1_0_LocatedSpecimenType_httpwww_opengis_netsampling1_0samplingLocation', False)

    
    samplingLocation = property(__samplingLocation.value, __samplingLocation.set, None, u'Sampling location may be provided directly if not available through its association with either the sampledFeature or a relatedSamplingFeature')

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element samplingTime ({http://www.opengis.net/sampling/1.0}samplingTime) inherited from {http://www.opengis.net/sampling/1.0}SpecimenType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element sampledFeature ({http://www.opengis.net/sampling/1.0}sampledFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element materialClass ({http://www.opengis.net/sampling/1.0}materialClass) inherited from {http://www.opengis.net/sampling/1.0}SpecimenType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element size ({http://www.opengis.net/sampling/1.0}size) inherited from {http://www.opengis.net/sampling/1.0}SpecimenType
    
    # Element relatedSamplingFeature ({http://www.opengis.net/sampling/1.0}relatedSamplingFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element processingDetails ({http://www.opengis.net/sampling/1.0}processingDetails) inherited from {http://www.opengis.net/sampling/1.0}SpecimenType
    
    # Element surveyDetails ({http://www.opengis.net/sampling/1.0}surveyDetails) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element relatedObservation ({http://www.opengis.net/sampling/1.0}relatedObservation) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element currentLocation ({http://www.opengis.net/sampling/1.0}currentLocation) inherited from {http://www.opengis.net/sampling/1.0}SpecimenType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = SpecimenType._ElementMap.copy()
    _ElementMap.update({
        __samplingLocation.name() : __samplingLocation
    })
    _AttributeMap = SpecimenType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LocatedSpecimenType', LocatedSpecimenType)


# Complex type LocatedSpecimenPropertyType with content type ELEMENT_ONLY
class LocatedSpecimenPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LocatedSpecimenPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}LocatedSpecimen uses Python identifier LocatedSpecimen
    __LocatedSpecimen = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LocatedSpecimen'), 'LocatedSpecimen', '__httpwww_opengis_netsampling1_0_LocatedSpecimenPropertyType_httpwww_opengis_netsampling1_0LocatedSpecimen', False)

    
    LocatedSpecimen = property(__LocatedSpecimen.value, __LocatedSpecimen.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_LocatedSpecimenPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_LocatedSpecimenPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_LocatedSpecimenPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_LocatedSpecimenPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_LocatedSpecimenPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_LocatedSpecimenPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_LocatedSpecimenPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_LocatedSpecimenPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __LocatedSpecimen.name() : __LocatedSpecimen
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __role.name() : __role,
        __actuate.name() : __actuate,
        __title.name() : __title,
        __show.name() : __show,
        __type.name() : __type
    }
Namespace.addCategoryObject('typeBinding', u'LocatedSpecimenPropertyType', LocatedSpecimenPropertyType)


# Complex type SamplingPointPropertyType with content type ELEMENT_ONLY
class SamplingPointPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingPointPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}SamplingPoint uses Python identifier SamplingPoint
    __SamplingPoint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SamplingPoint'), 'SamplingPoint', '__httpwww_opengis_netsampling1_0_SamplingPointPropertyType_httpwww_opengis_netsampling1_0SamplingPoint', False)

    
    SamplingPoint = property(__SamplingPoint.value, __SamplingPoint.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_SamplingPointPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_SamplingPointPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_SamplingPointPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_SamplingPointPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_SamplingPointPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_SamplingPointPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_SamplingPointPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_SamplingPointPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")


    _ElementMap = {
        __SamplingPoint.name() : __SamplingPoint
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __type.name() : __type,
        __role.name() : __role,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __show.name() : __show,
        __actuate.name() : __actuate
    }
Namespace.addCategoryObject('typeBinding', u'SamplingPointPropertyType', SamplingPointPropertyType)


# Complex type SurveyProcedureType with content type ELEMENT_ONLY
class SurveyProcedureType (pyxb.bundles.opengis.gml.AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SurveyProcedureType')
    # Base type is pyxb.bundles.opengis.gml.AbstractFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}elevationAccuracy uses Python identifier elevationAccuracy
    __elevationAccuracy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'elevationAccuracy'), 'elevationAccuracy', '__httpwww_opengis_netsampling1_0_SurveyProcedureType_httpwww_opengis_netsampling1_0elevationAccuracy', False)

    
    elevationAccuracy = property(__elevationAccuracy.value, __elevationAccuracy.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}projection uses Python identifier projection
    __projection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'projection'), 'projection', '__httpwww_opengis_netsampling1_0_SurveyProcedureType_httpwww_opengis_netsampling1_0projection', False)

    
    projection = property(__projection.value, __projection.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}geodeticDatum uses Python identifier geodeticDatum
    __geodeticDatum = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'geodeticDatum'), 'geodeticDatum', '__httpwww_opengis_netsampling1_0_SurveyProcedureType_httpwww_opengis_netsampling1_0geodeticDatum', False)

    
    geodeticDatum = property(__geodeticDatum.value, __geodeticDatum.set, None, None)

    
    # Element {http://www.opengis.net/sampling/1.0}positionAccuracy uses Python identifier positionAccuracy
    __positionAccuracy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'positionAccuracy'), 'positionAccuracy', '__httpwww_opengis_netsampling1_0_SurveyProcedureType_httpwww_opengis_netsampling1_0positionAccuracy', False)

    
    positionAccuracy = property(__positionAccuracy.value, __positionAccuracy.set, None, None)

    
    # Element {http://www.opengis.net/sampling/1.0}operator uses Python identifier operator
    __operator = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'operator'), 'operator', '__httpwww_opengis_netsampling1_0_SurveyProcedureType_httpwww_opengis_netsampling1_0operator', False)

    
    operator = property(__operator.value, __operator.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sampling/1.0}elevationDatum uses Python identifier elevationDatum
    __elevationDatum = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'elevationDatum'), 'elevationDatum', '__httpwww_opengis_netsampling1_0_SurveyProcedureType_httpwww_opengis_netsampling1_0elevationDatum', False)

    
    elevationDatum = property(__elevationDatum.value, __elevationDatum.set, None, None)

    
    # Element {http://www.opengis.net/sampling/1.0}surveyTime uses Python identifier surveyTime
    __surveyTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'surveyTime'), 'surveyTime', '__httpwww_opengis_netsampling1_0_SurveyProcedureType_httpwww_opengis_netsampling1_0surveyTime', False)

    
    surveyTime = property(__surveyTime.value, __surveyTime.set, None, None)

    
    # Element {http://www.opengis.net/sampling/1.0}elevationMethod uses Python identifier elevationMethod
    __elevationMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'elevationMethod'), 'elevationMethod', '__httpwww_opengis_netsampling1_0_SurveyProcedureType_httpwww_opengis_netsampling1_0elevationMethod', False)

    
    elevationMethod = property(__elevationMethod.value, __elevationMethod.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sampling/1.0}positionMethod uses Python identifier positionMethod
    __positionMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'), 'positionMethod', '__httpwww_opengis_netsampling1_0_SurveyProcedureType_httpwww_opengis_netsampling1_0positionMethod', False)

    
    positionMethod = property(__positionMethod.value, __positionMethod.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        __elevationAccuracy.name() : __elevationAccuracy,
        __projection.name() : __projection,
        __geodeticDatum.name() : __geodeticDatum,
        __positionAccuracy.name() : __positionAccuracy,
        __operator.name() : __operator,
        __elevationDatum.name() : __elevationDatum,
        __surveyTime.name() : __surveyTime,
        __elevationMethod.name() : __elevationMethod,
        __positionMethod.name() : __positionMethod
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SurveyProcedureType', SurveyProcedureType)


# Complex type SamplingFeatureCollectionType with content type ELEMENT_ONLY
class SamplingFeatureCollectionType (SamplingFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureCollectionType')
    # Base type is SamplingFeatureType
    
    # Element relatedObservation ({http://www.opengis.net/sampling/1.0}relatedObservation) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element relatedSamplingFeature ({http://www.opengis.net/sampling/1.0}relatedSamplingFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element surveyDetails ({http://www.opengis.net/sampling/1.0}surveyDetails) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element sampledFeature ({http://www.opengis.net/sampling/1.0}sampledFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}member uses Python identifier member
    __member = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'member'), 'member', '__httpwww_opengis_netsampling1_0_SamplingFeatureCollectionType_httpwww_opengis_netsampling1_0member', True)

    
    member = property(__member.value, __member.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = SamplingFeatureType._ElementMap.copy()
    _ElementMap.update({
        __member.name() : __member
    })
    _AttributeMap = SamplingFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SamplingFeatureCollectionType', SamplingFeatureCollectionType)


# Complex type SpatiallyExtensiveSamplingFeaturePropertyType with content type ELEMENT_ONLY
class SpatiallyExtensiveSamplingFeaturePropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SpatiallyExtensiveSamplingFeaturePropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}SpatiallyExtensiveSamplingFeature uses Python identifier SpatiallyExtensiveSamplingFeature
    __SpatiallyExtensiveSamplingFeature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SpatiallyExtensiveSamplingFeature'), 'SpatiallyExtensiveSamplingFeature', '__httpwww_opengis_netsampling1_0_SpatiallyExtensiveSamplingFeaturePropertyType_httpwww_opengis_netsampling1_0SpatiallyExtensiveSamplingFeature', False)

    
    SpatiallyExtensiveSamplingFeature = property(__SpatiallyExtensiveSamplingFeature.value, __SpatiallyExtensiveSamplingFeature.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_SpatiallyExtensiveSamplingFeaturePropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_SpatiallyExtensiveSamplingFeaturePropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_SpatiallyExtensiveSamplingFeaturePropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_SpatiallyExtensiveSamplingFeaturePropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_SpatiallyExtensiveSamplingFeaturePropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_SpatiallyExtensiveSamplingFeaturePropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_SpatiallyExtensiveSamplingFeaturePropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_SpatiallyExtensiveSamplingFeaturePropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __SpatiallyExtensiveSamplingFeature.name() : __SpatiallyExtensiveSamplingFeature
    }
    _AttributeMap = {
        __show.name() : __show,
        __remoteSchema.name() : __remoteSchema,
        __role.name() : __role,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __title.name() : __title,
        __actuate.name() : __actuate,
        __type.name() : __type
    }
Namespace.addCategoryObject('typeBinding', u'SpatiallyExtensiveSamplingFeaturePropertyType', SpatiallyExtensiveSamplingFeaturePropertyType)


# Complex type SamplingPointType with content type ELEMENT_ONLY
class SamplingPointType (SamplingFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingPointType')
    # Base type is SamplingFeatureType
    
    # Element sampledFeature ({http://www.opengis.net/sampling/1.0}sampledFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element relatedSamplingFeature ({http://www.opengis.net/sampling/1.0}relatedSamplingFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element surveyDetails ({http://www.opengis.net/sampling/1.0}surveyDetails) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sampling/1.0}position uses Python identifier position
    __position = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'position'), 'position', '__httpwww_opengis_netsampling1_0_SamplingPointType_httpwww_opengis_netsampling1_0position', False)

    
    position = property(__position.value, __position.set, None, None)

    
    # Element relatedObservation ({http://www.opengis.net/sampling/1.0}relatedObservation) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = SamplingFeatureType._ElementMap.copy()
    _ElementMap.update({
        __position.name() : __position
    })
    _AttributeMap = SamplingFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SamplingPointType', SamplingPointType)


# Complex type SamplingCurveType with content type ELEMENT_ONLY
class SamplingCurveType (SpatiallyExtensiveSamplingFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingCurveType')
    # Base type is SpatiallyExtensiveSamplingFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element surveyDetails ({http://www.opengis.net/sampling/1.0}surveyDetails) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element relatedSamplingFeature ({http://www.opengis.net/sampling/1.0}relatedSamplingFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sampling/1.0}shape uses Python identifier shape
    __shape = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'shape'), 'shape', '__httpwww_opengis_netsampling1_0_SamplingCurveType_httpwww_opengis_netsampling1_0shape', False)

    
    shape = property(__shape.value, __shape.set, None, None)

    
    # Element sampledFeature ({http://www.opengis.net/sampling/1.0}sampledFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}length uses Python identifier length
    __length = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'length'), 'length', '__httpwww_opengis_netsampling1_0_SamplingCurveType_httpwww_opengis_netsampling1_0length', False)

    
    length = property(__length.value, __length.set, None, None)

    
    # Element relatedObservation ({http://www.opengis.net/sampling/1.0}relatedObservation) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = SpatiallyExtensiveSamplingFeatureType._ElementMap.copy()
    _ElementMap.update({
        __shape.name() : __shape,
        __length.name() : __length
    })
    _AttributeMap = SpatiallyExtensiveSamplingFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SamplingCurveType', SamplingCurveType)


# Complex type SamplingSurfacePropertyType with content type ELEMENT_ONLY
class SamplingSurfacePropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingSurfacePropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}SamplingSurface uses Python identifier SamplingSurface
    __SamplingSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SamplingSurface'), 'SamplingSurface', '__httpwww_opengis_netsampling1_0_SamplingSurfacePropertyType_httpwww_opengis_netsampling1_0SamplingSurface', False)

    
    SamplingSurface = property(__SamplingSurface.value, __SamplingSurface.set, None, u'A "SamplingSurface" is an identified 2-D spatial feature. \n\t\tIt may be used for various purposes, in particular for observations of cross sections through features.\n\t\tSpecialized names for SamplingSurface include CrossSection, Section, Flitch, Swath, Scene, MapHorizon.')

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_SamplingSurfacePropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_SamplingSurfacePropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_SamplingSurfacePropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_SamplingSurfacePropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_SamplingSurfacePropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_SamplingSurfacePropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_SamplingSurfacePropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_SamplingSurfacePropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __SamplingSurface.name() : __SamplingSurface
    }
    _AttributeMap = {
        __arcrole.name() : __arcrole,
        __remoteSchema.name() : __remoteSchema,
        __href.name() : __href,
        __role.name() : __role,
        __title.name() : __title,
        __actuate.name() : __actuate,
        __show.name() : __show,
        __type.name() : __type
    }
Namespace.addCategoryObject('typeBinding', u'SamplingSurfacePropertyType', SamplingSurfacePropertyType)


# Complex type SamplingSurfaceType with content type ELEMENT_ONLY
class SamplingSurfaceType (SpatiallyExtensiveSamplingFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingSurfaceType')
    # Base type is SpatiallyExtensiveSamplingFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}area uses Python identifier area
    __area = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'area'), 'area', '__httpwww_opengis_netsampling1_0_SamplingSurfaceType_httpwww_opengis_netsampling1_0area', False)

    
    area = property(__area.value, __area.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element surveyDetails ({http://www.opengis.net/sampling/1.0}surveyDetails) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element relatedSamplingFeature ({http://www.opengis.net/sampling/1.0}relatedSamplingFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element {http://www.opengis.net/sampling/1.0}shape uses Python identifier shape
    __shape = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'shape'), 'shape', '__httpwww_opengis_netsampling1_0_SamplingSurfaceType_httpwww_opengis_netsampling1_0shape', False)

    
    shape = property(__shape.value, __shape.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element sampledFeature ({http://www.opengis.net/sampling/1.0}sampledFeature) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element relatedObservation ({http://www.opengis.net/sampling/1.0}relatedObservation) inherited from {http://www.opengis.net/sampling/1.0}SamplingFeatureType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = SpatiallyExtensiveSamplingFeatureType._ElementMap.copy()
    _ElementMap.update({
        __area.name() : __area,
        __shape.name() : __shape
    })
    _AttributeMap = SpatiallyExtensiveSamplingFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SamplingSurfaceType', SamplingSurfaceType)


# Complex type SamplingCurvePropertyType with content type ELEMENT_ONLY
class SamplingCurvePropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingCurvePropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}SamplingCurve uses Python identifier SamplingCurve
    __SamplingCurve = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SamplingCurve'), 'SamplingCurve', '__httpwww_opengis_netsampling1_0_SamplingCurvePropertyType_httpwww_opengis_netsampling1_0SamplingCurve', False)

    
    SamplingCurve = property(__SamplingCurve.value, __SamplingCurve.set, None, u'A "SamplingCurve" is an identified 1-D spatial feature. \n\t\tIt may be revisited for various purposes, in particular to retrieve multiple specimens or make repeated or complementary observations.\n\t\tSpecialized names for SamplingCurve include Profile, ObservationWell, FlightLine, Transect.')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_SamplingCurvePropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_SamplingCurvePropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_SamplingCurvePropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_SamplingCurvePropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_SamplingCurvePropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_SamplingCurvePropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_SamplingCurvePropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_SamplingCurvePropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        __SamplingCurve.name() : __SamplingCurve
    }
    _AttributeMap = {
        __actuate.name() : __actuate,
        __remoteSchema.name() : __remoteSchema,
        __type.name() : __type,
        __show.name() : __show,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __role.name() : __role
    }
Namespace.addCategoryObject('typeBinding', u'SamplingCurvePropertyType', SamplingCurvePropertyType)


# Complex type SamplingFeatureRelationPropertyType with content type ELEMENT_ONLY
class SamplingFeatureRelationPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureRelationPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}SamplingFeatureRelation uses Python identifier SamplingFeatureRelation
    __SamplingFeatureRelation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureRelation'), 'SamplingFeatureRelation', '__httpwww_opengis_netsampling1_0_SamplingFeatureRelationPropertyType_httpwww_opengis_netsampling1_0SamplingFeatureRelation', False)

    
    SamplingFeatureRelation = property(__SamplingFeatureRelation.value, __SamplingFeatureRelation.set, None, None)


    _ElementMap = {
        __SamplingFeatureRelation.name() : __SamplingFeatureRelation
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SamplingFeatureRelationPropertyType', SamplingFeatureRelationPropertyType)


# Complex type SurveyProcedurePropertyType with content type ELEMENT_ONLY
class SurveyProcedurePropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SurveyProcedurePropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sampling/1.0}SurveyProcedure uses Python identifier SurveyProcedure
    __SurveyProcedure = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SurveyProcedure'), 'SurveyProcedure', '__httpwww_opengis_netsampling1_0_SurveyProcedurePropertyType_httpwww_opengis_netsampling1_0SurveyProcedure', False)

    
    SurveyProcedure = property(__SurveyProcedure.value, __SurveyProcedure.set, None, u'Specialized procedure related to surveying positions and locations.')

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_SurveyProcedurePropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_SurveyProcedurePropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_SurveyProcedurePropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_SurveyProcedurePropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_SurveyProcedurePropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_SurveyProcedurePropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_SurveyProcedurePropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_SurveyProcedurePropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        __SurveyProcedure.name() : __SurveyProcedure
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __href.name() : __href,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __role.name() : __role
    }
Namespace.addCategoryObject('typeBinding', u'SurveyProcedurePropertyType', SurveyProcedurePropertyType)


# Complex type LocationPropertyType with content type ELEMENT_ONLY
class LocationPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LocationPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/gml}_Geometry uses Python identifier Geometry
    __Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Geometry'), 'Geometry', '__httpwww_opengis_netsampling1_0_LocationPropertyType_httpwww_opengis_netgml_Geometry', False)

    
    Geometry = property(__Geometry.value, __Geometry.set, None, u'The "_Geometry" element is the abstract head of the substituition group for all geometry elements of GML 3. This \n\t\t\tincludes pre-defined and user-defined geometry elements. Any geometry element must be a direct or indirect extension/restriction \n\t\t\tof AbstractGeometryType and must be directly or indirectly in the substitution group of "_Geometry".')

    
    # Element {http://www.opengis.net/sampling/1.0}EX_GeographicDescription uses Python identifier EX_GeographicDescription
    __EX_GeographicDescription = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EX_GeographicDescription'), 'EX_GeographicDescription', '__httpwww_opengis_netsampling1_0_LocationPropertyType_httpwww_opengis_netsampling1_0EX_GeographicDescription', False)

    
    EX_GeographicDescription = property(__EX_GeographicDescription.value, __EX_GeographicDescription.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsampling1_0_LocationPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsampling1_0_LocationPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsampling1_0_LocationPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsampling1_0_LocationPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsampling1_0_LocationPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsampling1_0_LocationPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsampling1_0_LocationPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute unionSemantics uses Python identifier unionSemantics
    __unionSemantics = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'unionSemantics'), 'unionSemantics', '__httpwww_opengis_netsampling1_0_LocationPropertyType_unionSemantics', STD_ANON_1)
    
    unionSemantics = property(__unionSemantics.value, __unionSemantics.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsampling1_0_LocationPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)


    _ElementMap = {
        __Geometry.name() : __Geometry,
        __EX_GeographicDescription.name() : __EX_GeographicDescription
    }
    _AttributeMap = {
        __href.name() : __href,
        __remoteSchema.name() : __remoteSchema,
        __role.name() : __role,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __title.name() : __title,
        __show.name() : __show,
        __unionSemantics.name() : __unionSemantics,
        __arcrole.name() : __arcrole
    }
Namespace.addCategoryObject('typeBinding', u'LocationPropertyType', LocationPropertyType)


SamplingFeatureRelation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureRelation'), SamplingFeatureRelationType)
Namespace.addCategoryObject('elementBinding', SamplingFeatureRelation.name().localName(), SamplingFeatureRelation)

SamplingSolid = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingSolid'), SamplingSolidType, documentation=u'A "SamplingSolid" is an identified 3-D spatial feature used in sampling.')
Namespace.addCategoryObject('elementBinding', SamplingSolid.name().localName(), SamplingSolid)

SamplingFeature = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeature'), SamplingFeatureType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', SamplingFeature.name().localName(), SamplingFeature)

LocatedSpecimen = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LocatedSpecimen'), LocatedSpecimenType)
Namespace.addCategoryObject('elementBinding', LocatedSpecimen.name().localName(), LocatedSpecimen)

SpatiallyExtensiveSamplingFeature = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SpatiallyExtensiveSamplingFeature'), SpatiallyExtensiveSamplingFeatureType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', SpatiallyExtensiveSamplingFeature.name().localName(), SpatiallyExtensiveSamplingFeature)

SurveyProcedure = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SurveyProcedure'), SurveyProcedureType, documentation=u'Specialized procedure related to surveying positions and locations.')
Namespace.addCategoryObject('elementBinding', SurveyProcedure.name().localName(), SurveyProcedure)

Specimen = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Specimen'), SpecimenType)
Namespace.addCategoryObject('elementBinding', Specimen.name().localName(), Specimen)

SamplingFeatureCollection = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureCollection'), SamplingFeatureCollectionType)
Namespace.addCategoryObject('elementBinding', SamplingFeatureCollection.name().localName(), SamplingFeatureCollection)

SamplingCurve = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingCurve'), SamplingCurveType, documentation=u'A "SamplingCurve" is an identified 1-D spatial feature. \n\t\tIt may be revisited for various purposes, in particular to retrieve multiple specimens or make repeated or complementary observations.\n\t\tSpecialized names for SamplingCurve include Profile, ObservationWell, FlightLine, Transect.')
Namespace.addCategoryObject('elementBinding', SamplingCurve.name().localName(), SamplingCurve)

SamplingPoint = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingPoint'), SamplingPointType)
Namespace.addCategoryObject('elementBinding', SamplingPoint.name().localName(), SamplingPoint)

SamplingSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingSurface'), SamplingSurfaceType, documentation=u'A "SamplingSurface" is an identified 2-D spatial feature. \n\t\tIt may be used for various purposes, in particular for observations of cross sections through features.\n\t\tSpecialized names for SamplingSurface include CrossSection, Section, Flitch, Swath, Scene, MapHorizon.')
Namespace.addCategoryObject('elementBinding', SamplingSurface.name().localName(), SamplingSurface)



SamplingFeaturePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeature'), SamplingFeatureType, abstract=pyxb.binding.datatypes.boolean(1), scope=SamplingFeaturePropertyType))
SamplingFeaturePropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingFeaturePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeature'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SamplingFeatureRelationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'target'), SamplingFeaturePropertyType, scope=SamplingFeatureRelationType))

SamplingFeatureRelationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'role'), pyxb.bundles.opengis.gml.CodeType, scope=SamplingFeatureRelationType))
SamplingFeatureRelationType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingFeatureRelationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'role'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingFeatureRelationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})


AnyOrReferenceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SamplingFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'), SurveyProcedurePropertyType, scope=SamplingFeatureType, documentation=u'A common requirement for sampling features is an indication of the SurveyProcedure \n\t\t\t\t\t\t\tthat provides the surveyDetails related to determination of its location and shape. '))

SamplingFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'), SamplingFeatureRelationPropertyType, scope=SamplingFeatureType, documentation=u'Sampling features are frequently related to each other, as parts of complexes, networks, through sub-sampling, etc. \n\t\t\t\t\t\t\tThis is supported by the relatedSamplingFeature association with a SamplingFeatureRelation association class, which carries a source, target and role.'))

SamplingFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'), pyxb.bundles.opengis.gml.FeaturePropertyType, scope=SamplingFeatureType, documentation=u'A SamplingFeature must be associated with one or more other features through an association role sampledFeature. \n\t\t\t\t\t\t\tThis association records the intention of the sample design. \n\t\t\t\t\t\t\tThe target of this association will usually be a domain feature.'))

SamplingFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'), pyxb.bundles.opengis.om_1_0.ObservationPropertyType, scope=SamplingFeatureType, documentation=u'A SamplingFeature is distinguished from typical domain feature types in that it has a set of [0..*] navigable associations with Observations, given the rolename relatedObservation. \n\t\t\t\t\tThis complements the association role \u201cfeatureOfInterest\u201d which is constrained to point back from the Observation to the Sampling-Feature. \n\t\t\t\t\tThe usual requirement of an Observation feature-of-interest is that its type has a property matching the observed-property on the Observation. \n\t\t\t\t\tIn the case of Sampling-features, the topology of the model and navigability of the relatedObservation role means that this requirement is satisfied automatically: \n\t\t\t\t\ta property of the sampling-feature is implied by the observedProperty of a related observation. \n\t\t\t\t\tThis effectively provides an unlimited set of \u201csoft-typed\u201d properties on a Sampling Feature.'))
SamplingFeatureType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
    ])
})


SpatiallyExtensiveSamplingFeatureType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SpatiallyExtensiveSamplingFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
    ])
})



SamplingSolidType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'shape'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=SamplingSolidType))

SamplingSolidType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'volume'), pyxb.bundles.opengis.gml.MeasureType, scope=SamplingSolidType))
SamplingSolidType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shape'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'volume'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shape'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingSolidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shape'))),
    ])
})



SamplingSolidPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingSolid'), SamplingSolidType, scope=SamplingSolidPropertyType, documentation=u'A "SamplingSolid" is an identified 3-D spatial feature used in sampling.'))
SamplingSolidPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingSolidPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SamplingSolid'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SpecimenPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Specimen'), SpecimenType, scope=SpecimenPropertyType))
SpecimenPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpecimenPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Specimen'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SamplingFeatureCollectionPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureCollection'), SamplingFeatureCollectionType, scope=SamplingFeatureCollectionPropertyType))
SamplingFeatureCollectionPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingFeatureCollectionPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureCollection'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SpecimenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'samplingTime'), pyxb.bundles.opengis.gml.TimePrimitivePropertyType, scope=SpecimenType, documentation=u'Time and date when the specimen was initially retrieved'))

SpecimenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'materialClass'), pyxb.bundles.opengis.gml.CodeType, scope=SpecimenType, documentation=u'Material type, usually taken from a controlled vocabulary\n\t\t\t\t\tSpecialised domains may choose to fix the vocabulary to be used\n\t\t\t\t\tIts value may be relatively generic (rock, pulp) or may reflect a detailed classification (calcrete, adamellite, biotite-schist). \n\t\t\tIn the latter case it is wise to use the codeSpace attribute to provide a link to the classification scheme/vocabulary used. \n'))

SpecimenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'processingDetails'), pyxb.bundles.opengis.gml.ReferenceType, scope=SpecimenType, documentation=u'One or more procedures may have been applied to a specimen.  \n            May contain collection, sampling and preparation procedures'))

SpecimenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'size'), CTD_ANON_1, scope=SpecimenType, documentation=u'The size of the specimen: mass, length, volume, etc'))

SpecimenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'samplingMethod'), pyxb.bundles.opengis.gml.ReferenceType, scope=SpecimenType, documentation=u'Method used when retrieving specimen from host sampledFeature'))

SpecimenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'currentLocation'), LocationPropertyType, scope=SpecimenType, documentation=u'Storage location of specimen if it still exists. If destroyed in analysis, then either omit or use xlink:href to point to a suitable URN, e.g. urn:cgi:def:nil:destroyed'))
SpecimenType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'currentLocation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'size'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'materialClass'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'materialClass'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingTime'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'processingDetails'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingTime'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'materialClass'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'size'))),
    ])
})



LocatedSpecimenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'samplingLocation'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=LocatedSpecimenType, documentation=u'Sampling location may be provided directly if not available through its association with either the sampledFeature or a relatedSamplingFeature'))
LocatedSpecimenType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingLocation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'processingDetails'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'size'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'currentLocation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingTime'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'materialClass'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'materialClass'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingTime'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingTime'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'materialClass'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'size'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LocatedSpecimenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'samplingTime'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
    ])
})



LocatedSpecimenPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LocatedSpecimen'), LocatedSpecimenType, scope=LocatedSpecimenPropertyType))
LocatedSpecimenPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LocatedSpecimenPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LocatedSpecimen'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SamplingPointPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingPoint'), SamplingPointType, scope=SamplingPointPropertyType))
SamplingPointPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingPointPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SamplingPoint'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SurveyProcedureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'elevationAccuracy'), pyxb.bundles.opengis.gml.MeasureType, scope=SurveyProcedureType))

SurveyProcedureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'projection'), pyxb.bundles.opengis.gml.ReferenceType, scope=SurveyProcedureType))

SurveyProcedureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'geodeticDatum'), pyxb.bundles.opengis.gml.ReferenceType, scope=SurveyProcedureType))

SurveyProcedureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'positionAccuracy'), pyxb.bundles.opengis.gml.MeasureType, scope=SurveyProcedureType))

SurveyProcedureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operator'), AnyOrReferenceType, scope=SurveyProcedureType))

SurveyProcedureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'elevationDatum'), pyxb.bundles.opengis.gml.ReferenceType, scope=SurveyProcedureType))

SurveyProcedureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'surveyTime'), pyxb.bundles.opengis.gml.TimePrimitivePropertyType, scope=SurveyProcedureType))

SurveyProcedureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'elevationMethod'), pyxb.bundles.opengis.om_1_0.ProcessPropertyType, scope=SurveyProcedureType))

SurveyProcedureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'), pyxb.bundles.opengis.om_1_0.ProcessPropertyType, scope=SurveyProcedureType))
SurveyProcedureType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'geodeticDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationAccuracy'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operator'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'geodeticDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationAccuracy'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operator'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'geodeticDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationAccuracy'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operator'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationMethod'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'projection'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionAccuracy'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyTime'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'geodeticDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationAccuracy'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'geodeticDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationAccuracy'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operator'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationMethod'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'geodeticDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyTime'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'geodeticDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationAccuracy'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'projection'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyTime'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'geodeticDatum'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationAccuracy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationMethod'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SurveyProcedureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'elevationDatum'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
    ])
})



SamplingFeatureCollectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'member'), SamplingFeaturePropertyType, scope=SamplingFeatureCollectionType))
SamplingFeatureCollectionType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingFeatureCollectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
    ])
})



SpatiallyExtensiveSamplingFeaturePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SpatiallyExtensiveSamplingFeature'), SpatiallyExtensiveSamplingFeatureType, abstract=pyxb.binding.datatypes.boolean(1), scope=SpatiallyExtensiveSamplingFeaturePropertyType))
SpatiallyExtensiveSamplingFeaturePropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpatiallyExtensiveSamplingFeaturePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SpatiallyExtensiveSamplingFeature'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SamplingPointType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'position'), pyxb.bundles.opengis.gml.PointPropertyType, scope=SamplingPointType))
SamplingPointType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingPointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
    ])
})



SamplingCurveType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'shape'), pyxb.bundles.opengis.gml.CurvePropertyType, scope=SamplingCurveType))

SamplingCurveType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'length'), pyxb.bundles.opengis.gml.MeasureType, scope=SamplingCurveType))
SamplingCurveType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shape'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'length'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shape'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shape'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingCurveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
    ])
})



SamplingSurfacePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingSurface'), SamplingSurfaceType, scope=SamplingSurfacePropertyType, documentation=u'A "SamplingSurface" is an identified 2-D spatial feature. \n\t\tIt may be used for various purposes, in particular for observations of cross sections through features.\n\t\tSpecialized names for SamplingSurface include CrossSection, Section, Flitch, Swath, Scene, MapHorizon.'))
SamplingSurfacePropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingSurfacePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SamplingSurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SamplingSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'area'), pyxb.bundles.opengis.gml.MeasureType, scope=SamplingSurfaceType))

SamplingSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'shape'), pyxb.bundles.opengis.gml.SurfacePropertyType, scope=SamplingSurfaceType))
SamplingSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shape'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'area'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shape'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sampledFeature'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedSamplingFeature'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surveyDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shape'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SamplingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relatedObservation'))),
    ])
})



SamplingCurvePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingCurve'), SamplingCurveType, scope=SamplingCurvePropertyType, documentation=u'A "SamplingCurve" is an identified 1-D spatial feature. \n\t\tIt may be revisited for various purposes, in particular to retrieve multiple specimens or make repeated or complementary observations.\n\t\tSpecialized names for SamplingCurve include Profile, ObservationWell, FlightLine, Transect.'))
SamplingCurvePropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingCurvePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SamplingCurve'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SamplingFeatureRelationPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureRelation'), SamplingFeatureRelationType, scope=SamplingFeatureRelationPropertyType))
SamplingFeatureRelationPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SamplingFeatureRelationPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SamplingFeatureRelation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SurveyProcedurePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SurveyProcedure'), SurveyProcedureType, scope=SurveyProcedurePropertyType, documentation=u'Specialized procedure related to surveying positions and locations.'))
SurveyProcedurePropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SurveyProcedurePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SurveyProcedure'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



LocationPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Geometry'), pyxb.bundles.opengis.gml.AbstractGeometryType, abstract=pyxb.binding.datatypes.boolean(1), scope=LocationPropertyType, documentation=u'The "_Geometry" element is the abstract head of the substituition group for all geometry elements of GML 3. This \n\t\t\tincludes pre-defined and user-defined geometry elements. Any geometry element must be a direct or indirect extension/restriction \n\t\t\tof AbstractGeometryType and must be directly or indirectly in the substitution group of "_Geometry".'))

LocationPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EX_GeographicDescription'), AnyOrReferenceType, scope=LocationPropertyType))
LocationPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LocationPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LocationPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EX_GeographicDescription'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})

SamplingSolid._setSubstitutionGroup(SpatiallyExtensiveSamplingFeature)

SamplingFeature._setSubstitutionGroup(pyxb.bundles.opengis.gml.Feature)

LocatedSpecimen._setSubstitutionGroup(Specimen)

SpatiallyExtensiveSamplingFeature._setSubstitutionGroup(SamplingFeature)

SurveyProcedure._setSubstitutionGroup(pyxb.bundles.opengis.gml.Feature)

Specimen._setSubstitutionGroup(SamplingFeature)

SamplingFeatureCollection._setSubstitutionGroup(SamplingFeature)

SamplingCurve._setSubstitutionGroup(SpatiallyExtensiveSamplingFeature)

SamplingPoint._setSubstitutionGroup(SamplingFeature)

SamplingSurface._setSubstitutionGroup(SpatiallyExtensiveSamplingFeature)
