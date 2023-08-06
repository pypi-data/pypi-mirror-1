# ./pyxb/bundles/opengis/citygml/raw/transportation.py
# PyXB bindings for NamespaceModule
# NSM:65845cfd54082c8f90fd61bb44aef8d930fc8df0
# Generated 2009-11-30 18:12:07.207337 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:2799c494-de0e-11de-b563-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.citygml.base
import pyxb.bundles.opengis.gml

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/transportation/1.0', create_if_missing=True)
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
class TrafficSurfaceMaterialType (pyxb.binding.datatypes.string):

    """Type for surface materials of transportation objects. The values of this type are defined in the XML
                file TrafficSurfaceMaterialType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TrafficSurfaceMaterialType')
    _Documentation = u'Type for surface materials of transportation objects. The values of this type are defined in the XML\n                file TrafficSurfaceMaterialType.xml, according to the dictionary concept of GML3. '
TrafficSurfaceMaterialType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'TrafficSurfaceMaterialType', TrafficSurfaceMaterialType)

# Atomic SimpleTypeDefinition
class TransportationComplexFunctionType (pyxb.binding.datatypes.string):

    """Function of a transportation complex. The values of this type are defined in the XML file
                TransportationComplexFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransportationComplexFunctionType')
    _Documentation = u'Function of a transportation complex. The values of this type are defined in the XML file\n                TransportationComplexFunctionType.xml, according to the dictionary concept of GML3. '
TransportationComplexFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'TransportationComplexFunctionType', TransportationComplexFunctionType)

# Atomic SimpleTypeDefinition
class TransportationComplexUsageType (pyxb.binding.datatypes.string):

    """Actual Usage of a transportation complex. The values of this type are defined in the XML file
                TransportationComplexUsageType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransportationComplexUsageType')
    _Documentation = u'Actual Usage of a transportation complex. The values of this type are defined in the XML file\n                TransportationComplexUsageType.xml, according to the dictionary concept of GML3. '
TransportationComplexUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'TransportationComplexUsageType', TransportationComplexUsageType)

# Atomic SimpleTypeDefinition
class TrafficAreaUsageType (pyxb.binding.datatypes.string):

    """Usage of a traffic area. The values of this type are defined in the XML file
                TrafficAreaUsageType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TrafficAreaUsageType')
    _Documentation = u'Usage of a traffic area. The values of this type are defined in the XML file\n                TrafficAreaUsageType.xml, according to the dictionary concept of GML3. '
TrafficAreaUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'TrafficAreaUsageType', TrafficAreaUsageType)

# Atomic SimpleTypeDefinition
class TrafficAreaFunctionType (pyxb.binding.datatypes.string):

    """Function of a traffic area. The values of this type are defined in the XML file
                TrafficAreaFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TrafficAreaFunctionType')
    _Documentation = u'Function of a traffic area. The values of this type are defined in the XML file\n                TrafficAreaFunctionType.xml, according to the dictionary concept of GML3. '
TrafficAreaFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'TrafficAreaFunctionType', TrafficAreaFunctionType)

# Atomic SimpleTypeDefinition
class AuxiliaryTrafficAreaFunctionType (pyxb.binding.datatypes.string):

    """Function of an auxiliary traffic area. The values of this type are defined in the XML file
                AuxiliaryTrafficAreaFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuxiliaryTrafficAreaFunctionType')
    _Documentation = u'Function of an auxiliary traffic area. The values of this type are defined in the XML file\n                AuxiliaryTrafficAreaFunctionType.xml, according to the dictionary concept of GML3. '
AuxiliaryTrafficAreaFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'AuxiliaryTrafficAreaFunctionType', AuxiliaryTrafficAreaFunctionType)

# Complex type AbstractTransportationObjectType with content type ELEMENT_ONLY
class AbstractTransportationObjectType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractTransportationObjectType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationObject uses Python identifier GenericApplicationPropertyOfTransportationObject
    __GenericApplicationPropertyOfTransportationObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'), 'GenericApplicationPropertyOfTransportationObject', '__httpwww_opengis_netcitygmltransportation1_0_AbstractTransportationObjectType_httpwww_opengis_netcitygmltransportation1_0_GenericApplicationPropertyOfTransportationObject', True)

    
    GenericApplicationPropertyOfTransportationObject = property(__GenericApplicationPropertyOfTransportationObject.value, __GenericApplicationPropertyOfTransportationObject.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfTransportationObject.name() : __GenericApplicationPropertyOfTransportationObject
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractTransportationObjectType', AbstractTransportationObjectType)


# Complex type AuxiliaryTrafficAreaType with content type ELEMENT_ONLY
class AuxiliaryTrafficAreaType (AbstractTransportationObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuxiliaryTrafficAreaType')
    # Base type is AbstractTransportationObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}surfaceMaterial uses Python identifier surfaceMaterial
    __surfaceMaterial = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'), 'surfaceMaterial', '__httpwww_opengis_netcitygmltransportation1_0_AuxiliaryTrafficAreaType_httpwww_opengis_netcitygmltransportation1_0surfaceMaterial', False)

    
    surfaceMaterial = property(__surfaceMaterial.value, __surfaceMaterial.set, None, None)

    
    # Element {http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfAuxiliaryTrafficArea uses Python identifier GenericApplicationPropertyOfAuxiliaryTrafficArea
    __GenericApplicationPropertyOfAuxiliaryTrafficArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'), 'GenericApplicationPropertyOfAuxiliaryTrafficArea', '__httpwww_opengis_netcitygmltransportation1_0_AuxiliaryTrafficAreaType_httpwww_opengis_netcitygmltransportation1_0_GenericApplicationPropertyOfAuxiliaryTrafficArea', True)

    
    GenericApplicationPropertyOfAuxiliaryTrafficArea = property(__GenericApplicationPropertyOfAuxiliaryTrafficArea.value, __GenericApplicationPropertyOfAuxiliaryTrafficArea.set, None, None)

    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod2MultiSurface uses Python identifier lod2MultiSurface
    __lod2MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), 'lod2MultiSurface', '__httpwww_opengis_netcitygmltransportation1_0_AuxiliaryTrafficAreaType_httpwww_opengis_netcitygmltransportation1_0lod2MultiSurface', False)

    
    lod2MultiSurface = property(__lod2MultiSurface.value, __lod2MultiSurface.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmltransportation1_0_AuxiliaryTrafficAreaType_httpwww_opengis_netcitygmltransportation1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmltransportation1_0_AuxiliaryTrafficAreaType_httpwww_opengis_netcitygmltransportation1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfTransportationObject ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationObject) inherited from {http://www.opengis.net/citygml/transportation/1.0}AbstractTransportationObjectType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmltransportation1_0_AuxiliaryTrafficAreaType_httpwww_opengis_netcitygmltransportation1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractTransportationObjectType._ElementMap.copy()
    _ElementMap.update({
        __surfaceMaterial.name() : __surfaceMaterial,
        __GenericApplicationPropertyOfAuxiliaryTrafficArea.name() : __GenericApplicationPropertyOfAuxiliaryTrafficArea,
        __lod2MultiSurface.name() : __lod2MultiSurface,
        __lod3MultiSurface.name() : __lod3MultiSurface,
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __function.name() : __function
    })
    _AttributeMap = AbstractTransportationObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AuxiliaryTrafficAreaType', AuxiliaryTrafficAreaType)


# Complex type TrafficAreaType with content type ELEMENT_ONLY
class TrafficAreaType (AbstractTransportationObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TrafficAreaType')
    # Base type is AbstractTransportationObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfTransportationObject ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationObject) inherited from {http://www.opengis.net/citygml/transportation/1.0}AbstractTransportationObjectType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod2MultiSurface uses Python identifier lod2MultiSurface
    __lod2MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), 'lod2MultiSurface', '__httpwww_opengis_netcitygmltransportation1_0_TrafficAreaType_httpwww_opengis_netcitygmltransportation1_0lod2MultiSurface', False)

    
    lod2MultiSurface = property(__lod2MultiSurface.value, __lod2MultiSurface.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmltransportation1_0_TrafficAreaType_httpwww_opengis_netcitygmltransportation1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}surfaceMaterial uses Python identifier surfaceMaterial
    __surfaceMaterial = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'), 'surfaceMaterial', '__httpwww_opengis_netcitygmltransportation1_0_TrafficAreaType_httpwww_opengis_netcitygmltransportation1_0surfaceMaterial', False)

    
    surfaceMaterial = property(__surfaceMaterial.value, __surfaceMaterial.set, None, None)

    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmltransportation1_0_TrafficAreaType_httpwww_opengis_netcitygmltransportation1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmltransportation1_0_TrafficAreaType_httpwww_opengis_netcitygmltransportation1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element {http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTrafficArea uses Python identifier GenericApplicationPropertyOfTrafficArea
    __GenericApplicationPropertyOfTrafficArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'), 'GenericApplicationPropertyOfTrafficArea', '__httpwww_opengis_netcitygmltransportation1_0_TrafficAreaType_httpwww_opengis_netcitygmltransportation1_0_GenericApplicationPropertyOfTrafficArea', True)

    
    GenericApplicationPropertyOfTrafficArea = property(__GenericApplicationPropertyOfTrafficArea.value, __GenericApplicationPropertyOfTrafficArea.set, None, None)

    
    # Element {http://www.opengis.net/citygml/transportation/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmltransportation1_0_TrafficAreaType_httpwww_opengis_netcitygmltransportation1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractTransportationObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod2MultiSurface.name() : __lod2MultiSurface,
        __lod3MultiSurface.name() : __lod3MultiSurface,
        __surfaceMaterial.name() : __surfaceMaterial,
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __function.name() : __function,
        __GenericApplicationPropertyOfTrafficArea.name() : __GenericApplicationPropertyOfTrafficArea,
        __usage.name() : __usage
    })
    _AttributeMap = AbstractTransportationObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TrafficAreaType', TrafficAreaType)


# Complex type TrafficAreaPropertyType with content type ELEMENT_ONLY
class TrafficAreaPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TrafficAreaPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}TrafficArea uses Python identifier TrafficArea
    __TrafficArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TrafficArea'), 'TrafficArea', '__httpwww_opengis_netcitygmltransportation1_0_TrafficAreaPropertyType_httpwww_opengis_netcitygmltransportation1_0TrafficArea', False)

    
    TrafficArea = property(__TrafficArea.value, __TrafficArea.set, None, None)

    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __TrafficArea.name() : __TrafficArea
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TrafficAreaPropertyType', TrafficAreaPropertyType)


# Complex type AuxiliaryTrafficAreaPropertyType with content type ELEMENT_ONLY
class AuxiliaryTrafficAreaPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuxiliaryTrafficAreaPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}AuxiliaryTrafficArea uses Python identifier AuxiliaryTrafficArea
    __AuxiliaryTrafficArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuxiliaryTrafficArea'), 'AuxiliaryTrafficArea', '__httpwww_opengis_netcitygmltransportation1_0_AuxiliaryTrafficAreaPropertyType_httpwww_opengis_netcitygmltransportation1_0AuxiliaryTrafficArea', False)

    
    AuxiliaryTrafficArea = property(__AuxiliaryTrafficArea.value, __AuxiliaryTrafficArea.set, None, None)

    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __AuxiliaryTrafficArea.name() : __AuxiliaryTrafficArea
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AuxiliaryTrafficAreaPropertyType', AuxiliaryTrafficAreaPropertyType)


# Complex type TransportationComplexType with content type ELEMENT_ONLY
class TransportationComplexType (AbstractTransportationObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransportationComplexType')
    # Base type is AbstractTransportationObjectType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmltransportation1_0_TransportationComplexType_httpwww_opengis_netcitygmltransportation1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationComplex uses Python identifier GenericApplicationPropertyOfTransportationComplex
    __GenericApplicationPropertyOfTransportationComplex = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'), 'GenericApplicationPropertyOfTransportationComplex', '__httpwww_opengis_netcitygmltransportation1_0_TransportationComplexType_httpwww_opengis_netcitygmltransportation1_0_GenericApplicationPropertyOfTransportationComplex', True)

    
    GenericApplicationPropertyOfTransportationComplex = property(__GenericApplicationPropertyOfTransportationComplex.value, __GenericApplicationPropertyOfTransportationComplex.set, None, None)

    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmltransportation1_0_TransportationComplexType_httpwww_opengis_netcitygmltransportation1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmltransportation1_0_TransportationComplexType_httpwww_opengis_netcitygmltransportation1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element GenericApplicationPropertyOfTransportationObject ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationObject) inherited from {http://www.opengis.net/citygml/transportation/1.0}AbstractTransportationObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}trafficArea uses Python identifier trafficArea
    __trafficArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'), 'trafficArea', '__httpwww_opengis_netcitygmltransportation1_0_TransportationComplexType_httpwww_opengis_netcitygmltransportation1_0trafficArea', True)

    
    trafficArea = property(__trafficArea.value, __trafficArea.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmltransportation1_0_TransportationComplexType_httpwww_opengis_netcitygmltransportation1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod0Network uses Python identifier lod0Network
    __lod0Network = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'), 'lod0Network', '__httpwww_opengis_netcitygmltransportation1_0_TransportationComplexType_httpwww_opengis_netcitygmltransportation1_0lod0Network', True)

    
    lod0Network = property(__lod0Network.value, __lod0Network.set, None, None)

    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod1MultiSurface uses Python identifier lod1MultiSurface
    __lod1MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), 'lod1MultiSurface', '__httpwww_opengis_netcitygmltransportation1_0_TransportationComplexType_httpwww_opengis_netcitygmltransportation1_0lod1MultiSurface', False)

    
    lod1MultiSurface = property(__lod1MultiSurface.value, __lod1MultiSurface.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}lod2MultiSurface uses Python identifier lod2MultiSurface
    __lod2MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), 'lod2MultiSurface', '__httpwww_opengis_netcitygmltransportation1_0_TransportationComplexType_httpwww_opengis_netcitygmltransportation1_0lod2MultiSurface', False)

    
    lod2MultiSurface = property(__lod2MultiSurface.value, __lod2MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/transportation/1.0}auxiliaryTrafficArea uses Python identifier auxiliaryTrafficArea
    __auxiliaryTrafficArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'), 'auxiliaryTrafficArea', '__httpwww_opengis_netcitygmltransportation1_0_TransportationComplexType_httpwww_opengis_netcitygmltransportation1_0auxiliaryTrafficArea', True)

    
    auxiliaryTrafficArea = property(__auxiliaryTrafficArea.value, __auxiliaryTrafficArea.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractTransportationObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod3MultiSurface.name() : __lod3MultiSurface,
        __GenericApplicationPropertyOfTransportationComplex.name() : __GenericApplicationPropertyOfTransportationComplex,
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __usage.name() : __usage,
        __trafficArea.name() : __trafficArea,
        __function.name() : __function,
        __lod0Network.name() : __lod0Network,
        __lod1MultiSurface.name() : __lod1MultiSurface,
        __lod2MultiSurface.name() : __lod2MultiSurface,
        __auxiliaryTrafficArea.name() : __auxiliaryTrafficArea
    })
    _AttributeMap = AbstractTransportationObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TransportationComplexType', TransportationComplexType)


# Complex type TrackType with content type ELEMENT_ONLY
class TrackType (TransportationComplexType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TrackType')
    # Base type is TransportationComplexType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTrack uses Python identifier GenericApplicationPropertyOfTrack
    __GenericApplicationPropertyOfTrack = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'), 'GenericApplicationPropertyOfTrack', '__httpwww_opengis_netcitygmltransportation1_0_TrackType_httpwww_opengis_netcitygmltransportation1_0_GenericApplicationPropertyOfTrack', True)

    
    GenericApplicationPropertyOfTrack = property(__GenericApplicationPropertyOfTrack.value, __GenericApplicationPropertyOfTrack.set, None, None)

    
    # Element GenericApplicationPropertyOfTransportationComplex ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationComplex) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element usage ({http://www.opengis.net/citygml/transportation/1.0}usage) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element trafficArea ({http://www.opengis.net/citygml/transportation/1.0}trafficArea) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod0Network ({http://www.opengis.net/citygml/transportation/1.0}lod0Network) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod1MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod1MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element function ({http://www.opengis.net/citygml/transportation/1.0}function) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfTransportationObject ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationObject) inherited from {http://www.opengis.net/citygml/transportation/1.0}AbstractTransportationObjectType
    
    # Element auxiliaryTrafficArea ({http://www.opengis.net/citygml/transportation/1.0}auxiliaryTrafficArea) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = TransportationComplexType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfTrack.name() : __GenericApplicationPropertyOfTrack
    })
    _AttributeMap = TransportationComplexType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TrackType', TrackType)


# Complex type RailwayType with content type ELEMENT_ONLY
class RailwayType (TransportationComplexType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RailwayType')
    # Base type is TransportationComplexType
    
    # Element GenericApplicationPropertyOfTransportationComplex ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationComplex) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfRailway uses Python identifier GenericApplicationPropertyOfRailway
    __GenericApplicationPropertyOfRailway = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'), 'GenericApplicationPropertyOfRailway', '__httpwww_opengis_netcitygmltransportation1_0_RailwayType_httpwww_opengis_netcitygmltransportation1_0_GenericApplicationPropertyOfRailway', True)

    
    GenericApplicationPropertyOfRailway = property(__GenericApplicationPropertyOfRailway.value, __GenericApplicationPropertyOfRailway.set, None, None)

    
    # Element usage ({http://www.opengis.net/citygml/transportation/1.0}usage) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element trafficArea ({http://www.opengis.net/citygml/transportation/1.0}trafficArea) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod0Network ({http://www.opengis.net/citygml/transportation/1.0}lod0Network) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod1MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod1MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element function ({http://www.opengis.net/citygml/transportation/1.0}function) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfTransportationObject ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationObject) inherited from {http://www.opengis.net/citygml/transportation/1.0}AbstractTransportationObjectType
    
    # Element auxiliaryTrafficArea ({http://www.opengis.net/citygml/transportation/1.0}auxiliaryTrafficArea) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = TransportationComplexType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfRailway.name() : __GenericApplicationPropertyOfRailway
    })
    _AttributeMap = TransportationComplexType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'RailwayType', RailwayType)


# Complex type SquareType with content type ELEMENT_ONLY
class SquareType (TransportationComplexType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SquareType')
    # Base type is TransportationComplexType
    
    # Element GenericApplicationPropertyOfTransportationComplex ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationComplex) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element usage ({http://www.opengis.net/citygml/transportation/1.0}usage) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element trafficArea ({http://www.opengis.net/citygml/transportation/1.0}trafficArea) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod0Network ({http://www.opengis.net/citygml/transportation/1.0}lod0Network) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod1MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod1MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element function ({http://www.opengis.net/citygml/transportation/1.0}function) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfSquare uses Python identifier GenericApplicationPropertyOfSquare
    __GenericApplicationPropertyOfSquare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'), 'GenericApplicationPropertyOfSquare', '__httpwww_opengis_netcitygmltransportation1_0_SquareType_httpwww_opengis_netcitygmltransportation1_0_GenericApplicationPropertyOfSquare', True)

    
    GenericApplicationPropertyOfSquare = property(__GenericApplicationPropertyOfSquare.value, __GenericApplicationPropertyOfSquare.set, None, None)

    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfTransportationObject ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationObject) inherited from {http://www.opengis.net/citygml/transportation/1.0}AbstractTransportationObjectType
    
    # Element auxiliaryTrafficArea ({http://www.opengis.net/citygml/transportation/1.0}auxiliaryTrafficArea) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = TransportationComplexType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfSquare.name() : __GenericApplicationPropertyOfSquare
    })
    _AttributeMap = TransportationComplexType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SquareType', SquareType)


# Complex type RoadType with content type ELEMENT_ONLY
class RoadType (TransportationComplexType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoadType')
    # Base type is TransportationComplexType
    
    # Element GenericApplicationPropertyOfTransportationComplex ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationComplex) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfRoad uses Python identifier GenericApplicationPropertyOfRoad
    __GenericApplicationPropertyOfRoad = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'), 'GenericApplicationPropertyOfRoad', '__httpwww_opengis_netcitygmltransportation1_0_RoadType_httpwww_opengis_netcitygmltransportation1_0_GenericApplicationPropertyOfRoad', True)

    
    GenericApplicationPropertyOfRoad = property(__GenericApplicationPropertyOfRoad.value, __GenericApplicationPropertyOfRoad.set, None, None)

    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element usage ({http://www.opengis.net/citygml/transportation/1.0}usage) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element trafficArea ({http://www.opengis.net/citygml/transportation/1.0}trafficArea) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod0Network ({http://www.opengis.net/citygml/transportation/1.0}lod0Network) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod1MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod1MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element function ({http://www.opengis.net/citygml/transportation/1.0}function) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/transportation/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfTransportationObject ({http://www.opengis.net/citygml/transportation/1.0}_GenericApplicationPropertyOfTransportationObject) inherited from {http://www.opengis.net/citygml/transportation/1.0}AbstractTransportationObjectType
    
    # Element auxiliaryTrafficArea ({http://www.opengis.net/citygml/transportation/1.0}auxiliaryTrafficArea) inherited from {http://www.opengis.net/citygml/transportation/1.0}TransportationComplexType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = TransportationComplexType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfRoad.name() : __GenericApplicationPropertyOfRoad
    })
    _AttributeMap = TransportationComplexType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'RoadType', RoadType)


AuxiliaryTrafficArea = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuxiliaryTrafficArea'), AuxiliaryTrafficAreaType)
Namespace.addCategoryObject('elementBinding', AuxiliaryTrafficArea.name().localName(), AuxiliaryTrafficArea)

GenericApplicationPropertyOfAuxiliaryTrafficArea = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfAuxiliaryTrafficArea.name().localName(), GenericApplicationPropertyOfAuxiliaryTrafficArea)

GenericApplicationPropertyOfTransportationObject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfTransportationObject.name().localName(), GenericApplicationPropertyOfTransportationObject)

Track = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Track'), TrackType)
Namespace.addCategoryObject('elementBinding', Track.name().localName(), Track)

GenericApplicationPropertyOfTrack = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfTrack.name().localName(), GenericApplicationPropertyOfTrack)

GenericApplicationPropertyOfRoad = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfRoad.name().localName(), GenericApplicationPropertyOfRoad)

TransportationComplex = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TransportationComplex'), TransportationComplexType)
Namespace.addCategoryObject('elementBinding', TransportationComplex.name().localName(), TransportationComplex)

GenericApplicationPropertyOfTransportationComplex = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfTransportationComplex.name().localName(), GenericApplicationPropertyOfTransportationComplex)

GenericApplicationPropertyOfSquare = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfSquare.name().localName(), GenericApplicationPropertyOfSquare)

Railway = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Railway'), RailwayType)
Namespace.addCategoryObject('elementBinding', Railway.name().localName(), Railway)

GenericApplicationPropertyOfRailway = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfRailway.name().localName(), GenericApplicationPropertyOfRailway)

Square = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Square'), SquareType)
Namespace.addCategoryObject('elementBinding', Square.name().localName(), Square)

TransportationObject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_TransportationObject'), AbstractTransportationObjectType)
Namespace.addCategoryObject('elementBinding', TransportationObject.name().localName(), TransportationObject)

TrafficArea = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TrafficArea'), TrafficAreaType)
Namespace.addCategoryObject('elementBinding', TrafficArea.name().localName(), TrafficArea)

GenericApplicationPropertyOfTrafficArea = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfTrafficArea.name().localName(), GenericApplicationPropertyOfTrafficArea)

Road = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Road'), RoadType)
Namespace.addCategoryObject('elementBinding', Road.name().localName(), Road)



AbstractTransportationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractTransportationObjectType))
AbstractTransportationObjectType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractTransportationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
    ])
})



AuxiliaryTrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'), TrafficSurfaceMaterialType, scope=AuxiliaryTrafficAreaType))

AuxiliaryTrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AuxiliaryTrafficAreaType))

AuxiliaryTrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AuxiliaryTrafficAreaType))

AuxiliaryTrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AuxiliaryTrafficAreaType))

AuxiliaryTrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AuxiliaryTrafficAreaType))

AuxiliaryTrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), AuxiliaryTrafficAreaFunctionType, scope=AuxiliaryTrafficAreaType))
AuxiliaryTrafficAreaType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AuxiliaryTrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAuxiliaryTrafficArea'))),
    ])
})



TrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=TrafficAreaType))

TrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=TrafficAreaType))

TrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'), TrafficSurfaceMaterialType, scope=TrafficAreaType))

TrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=TrafficAreaType))

TrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), TrafficAreaFunctionType, scope=TrafficAreaType))

TrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=TrafficAreaType))

TrafficAreaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), TrafficAreaUsageType, scope=TrafficAreaType))
TrafficAreaType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrafficAreaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceMaterial'))),
    ])
})



TrafficAreaPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TrafficArea'), TrafficAreaType, scope=TrafficAreaPropertyType))
TrafficAreaPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrafficAreaPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TrafficArea'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



AuxiliaryTrafficAreaPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuxiliaryTrafficArea'), AuxiliaryTrafficAreaType, scope=AuxiliaryTrafficAreaPropertyType))
AuxiliaryTrafficAreaPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AuxiliaryTrafficAreaPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuxiliaryTrafficArea'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



TransportationComplexType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=TransportationComplexType))

TransportationComplexType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=TransportationComplexType))

TransportationComplexType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=TransportationComplexType))

TransportationComplexType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), TransportationComplexUsageType, scope=TransportationComplexType))

TransportationComplexType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'), TrafficAreaPropertyType, scope=TransportationComplexType))

TransportationComplexType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), TransportationComplexFunctionType, scope=TransportationComplexType))

TransportationComplexType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'), pyxb.bundles.opengis.gml.GeometricComplexPropertyType, scope=TransportationComplexType))

TransportationComplexType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=TransportationComplexType))

TransportationComplexType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=TransportationComplexType))

TransportationComplexType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'), AuxiliaryTrafficAreaPropertyType, scope=TransportationComplexType))
TransportationComplexType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TransportationComplexType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
    ])
})



TrackType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=TrackType))
TrackType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTrack'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TrackType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
    ])
})



RailwayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=RailwayType))
RailwayType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RailwayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRailway'))),
    ])
})



SquareType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=SquareType))
SquareType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SquareType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSquare'))),
    ])
})



RoadType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=RoadType))
RoadType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trafficArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0Network'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'auxiliaryTrafficArea'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTransportationComplex'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoad'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoadType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
    ])
})

AuxiliaryTrafficArea._setSubstitutionGroup(TransportationObject)

Track._setSubstitutionGroup(TransportationComplex)

TransportationComplex._setSubstitutionGroup(TransportationObject)

Railway._setSubstitutionGroup(TransportationComplex)

Square._setSubstitutionGroup(TransportationComplex)

TransportationObject._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

TrafficArea._setSubstitutionGroup(TransportationObject)

Road._setSubstitutionGroup(TransportationComplex)
