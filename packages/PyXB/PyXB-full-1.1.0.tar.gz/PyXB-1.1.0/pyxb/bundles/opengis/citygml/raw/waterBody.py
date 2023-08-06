# ./pyxb/bundles/opengis/citygml/raw/waterBody.py
# PyXB bindings for NamespaceModule
# NSM:e6f47025eea7290cf896f4408cff6d132fffbd8a
# Generated 2009-11-30 18:12:18.395034 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:2e4f3c1a-de0e-11de-a683-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.citygml.base
import pyxb.bundles.opengis.gml

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/waterbody/1.0', create_if_missing=True)
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
class WaterBodyUsageType (pyxb.binding.datatypes.string):

    """Actual usage of a water body. The values of this type are defined in the XML file
                WaterBodyUsageType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WaterBodyUsageType')
    _Documentation = u'Actual usage of a water body. The values of this type are defined in the XML file\n                WaterBodyUsageType.xml, according to the dictionary concept of GML3. '
WaterBodyUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'WaterBodyUsageType', WaterBodyUsageType)

# Atomic SimpleTypeDefinition
class WaterLevelType (pyxb.binding.datatypes.string):

    """Type for the specification of the level of a water surface. The optional attribute waterLevel of a
                WaterSurface can be used to describe the water level, for which the given 3D surface geometry was acquired. This
                is especially important, when the water body is influenced by the tide. The values of this type are defined in the
                XML file WaterLevelType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WaterLevelType')
    _Documentation = u'Type for the specification of the level of a water surface. The optional attribute waterLevel of a\n                WaterSurface can be used to describe the water level, for which the given 3D surface geometry was acquired. This\n                is especially important, when the water body is influenced by the tide. The values of this type are defined in the\n                XML file WaterLevelType.xml, according to the dictionary concept of GML3. '
WaterLevelType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'WaterLevelType', WaterLevelType)

# Atomic SimpleTypeDefinition
class WaterBodyFunctionType (pyxb.binding.datatypes.string):

    """Function of a Water Body. The values of this type are defined in the XML file
                WaterBodyFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WaterBodyFunctionType')
    _Documentation = u'Function of a Water Body. The values of this type are defined in the XML file\n                WaterBodyFunctionType.xml, according to the dictionary concept of GML3. '
WaterBodyFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'WaterBodyFunctionType', WaterBodyFunctionType)

# Atomic SimpleTypeDefinition
class WaterBodyClassType (pyxb.binding.datatypes.string):

    """Class of a Water Body. The values of this type are defined in the XML file WaterBodyClassType.xml,
                according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WaterBodyClassType')
    _Documentation = u'Class of a Water Body. The values of this type are defined in the XML file WaterBodyClassType.xml,\n                according to the dictionary concept of GML3. '
WaterBodyClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'WaterBodyClassType', WaterBodyClassType)

# Complex type AbstractWaterBoundarySurfaceType with content type ELEMENT_ONLY
class AbstractWaterBoundarySurfaceType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractWaterBoundarySurfaceType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}_GenericApplicationPropertyOfWaterBoundarySurface uses Python identifier GenericApplicationPropertyOfWaterBoundarySurface
    __GenericApplicationPropertyOfWaterBoundarySurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'), 'GenericApplicationPropertyOfWaterBoundarySurface', '__httpwww_opengis_netcitygmlwaterbody1_0_AbstractWaterBoundarySurfaceType_httpwww_opengis_netcitygmlwaterbody1_0_GenericApplicationPropertyOfWaterBoundarySurface', True)

    
    GenericApplicationPropertyOfWaterBoundarySurface = property(__GenericApplicationPropertyOfWaterBoundarySurface.value, __GenericApplicationPropertyOfWaterBoundarySurface.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod3Surface uses Python identifier lod3Surface
    __lod3Surface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'), 'lod3Surface', '__httpwww_opengis_netcitygmlwaterbody1_0_AbstractWaterBoundarySurfaceType_httpwww_opengis_netcitygmlwaterbody1_0lod3Surface', False)

    
    lod3Surface = property(__lod3Surface.value, __lod3Surface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod4Surface uses Python identifier lod4Surface
    __lod4Surface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'), 'lod4Surface', '__httpwww_opengis_netcitygmlwaterbody1_0_AbstractWaterBoundarySurfaceType_httpwww_opengis_netcitygmlwaterbody1_0lod4Surface', False)

    
    lod4Surface = property(__lod4Surface.value, __lod4Surface.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod2Surface uses Python identifier lod2Surface
    __lod2Surface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'), 'lod2Surface', '__httpwww_opengis_netcitygmlwaterbody1_0_AbstractWaterBoundarySurfaceType_httpwww_opengis_netcitygmlwaterbody1_0lod2Surface', False)

    
    lod2Surface = property(__lod2Surface.value, __lod2Surface.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfWaterBoundarySurface.name() : __GenericApplicationPropertyOfWaterBoundarySurface,
        __lod3Surface.name() : __lod3Surface,
        __lod4Surface.name() : __lod4Surface,
        __lod2Surface.name() : __lod2Surface
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractWaterBoundarySurfaceType', AbstractWaterBoundarySurfaceType)


# Complex type WaterGroundSurfaceType with content type ELEMENT_ONLY
class WaterGroundSurfaceType (AbstractWaterBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WaterGroundSurfaceType')
    # Base type is AbstractWaterBoundarySurfaceType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod3Surface ({http://www.opengis.net/citygml/waterbody/1.0}lod3Surface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfWaterBoundarySurface ({http://www.opengis.net/citygml/waterbody/1.0}_GenericApplicationPropertyOfWaterBoundarySurface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}_GenericApplicationPropertyOfWaterGroundSurface uses Python identifier GenericApplicationPropertyOfWaterGroundSurface
    __GenericApplicationPropertyOfWaterGroundSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'), 'GenericApplicationPropertyOfWaterGroundSurface', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterGroundSurfaceType_httpwww_opengis_netcitygmlwaterbody1_0_GenericApplicationPropertyOfWaterGroundSurface', True)

    
    GenericApplicationPropertyOfWaterGroundSurface = property(__GenericApplicationPropertyOfWaterGroundSurface.value, __GenericApplicationPropertyOfWaterGroundSurface.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod4Surface ({http://www.opengis.net/citygml/waterbody/1.0}lod4Surface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod2Surface ({http://www.opengis.net/citygml/waterbody/1.0}lod2Surface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractWaterBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfWaterGroundSurface.name() : __GenericApplicationPropertyOfWaterGroundSurface
    })
    _AttributeMap = AbstractWaterBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'WaterGroundSurfaceType', WaterGroundSurfaceType)


# Complex type AbstractWaterObjectType with content type ELEMENT_ONLY
class AbstractWaterObjectType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractWaterObjectType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}_GenericApplicationPropertyOfWaterObject uses Python identifier GenericApplicationPropertyOfWaterObject
    __GenericApplicationPropertyOfWaterObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'), 'GenericApplicationPropertyOfWaterObject', '__httpwww_opengis_netcitygmlwaterbody1_0_AbstractWaterObjectType_httpwww_opengis_netcitygmlwaterbody1_0_GenericApplicationPropertyOfWaterObject', True)

    
    GenericApplicationPropertyOfWaterObject = property(__GenericApplicationPropertyOfWaterObject.value, __GenericApplicationPropertyOfWaterObject.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfWaterObject.name() : __GenericApplicationPropertyOfWaterObject
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractWaterObjectType', AbstractWaterObjectType)


# Complex type WaterClosureSurfaceType with content type ELEMENT_ONLY
class WaterClosureSurfaceType (AbstractWaterBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WaterClosureSurfaceType')
    # Base type is AbstractWaterBoundarySurfaceType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod3Surface ({http://www.opengis.net/citygml/waterbody/1.0}lod3Surface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfWaterBoundarySurface ({http://www.opengis.net/citygml/waterbody/1.0}_GenericApplicationPropertyOfWaterBoundarySurface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod4Surface ({http://www.opengis.net/citygml/waterbody/1.0}lod4Surface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}_GenericApplicationPropertyOfWaterClosureSurface uses Python identifier GenericApplicationPropertyOfWaterClosureSurface
    __GenericApplicationPropertyOfWaterClosureSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'), 'GenericApplicationPropertyOfWaterClosureSurface', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterClosureSurfaceType_httpwww_opengis_netcitygmlwaterbody1_0_GenericApplicationPropertyOfWaterClosureSurface', True)

    
    GenericApplicationPropertyOfWaterClosureSurface = property(__GenericApplicationPropertyOfWaterClosureSurface.value, __GenericApplicationPropertyOfWaterClosureSurface.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod2Surface ({http://www.opengis.net/citygml/waterbody/1.0}lod2Surface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractWaterBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfWaterClosureSurface.name() : __GenericApplicationPropertyOfWaterClosureSurface
    })
    _AttributeMap = AbstractWaterBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'WaterClosureSurfaceType', WaterClosureSurfaceType)


# Complex type WaterSurfaceType with content type ELEMENT_ONLY
class WaterSurfaceType (AbstractWaterBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WaterSurfaceType')
    # Base type is AbstractWaterBoundarySurfaceType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfWaterBoundarySurface ({http://www.opengis.net/citygml/waterbody/1.0}_GenericApplicationPropertyOfWaterBoundarySurface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3Surface ({http://www.opengis.net/citygml/waterbody/1.0}lod3Surface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Element lod4Surface ({http://www.opengis.net/citygml/waterbody/1.0}lod4Surface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}_GenericApplicationPropertyOfWaterSurface uses Python identifier GenericApplicationPropertyOfWaterSurface
    __GenericApplicationPropertyOfWaterSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'), 'GenericApplicationPropertyOfWaterSurface', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterSurfaceType_httpwww_opengis_netcitygmlwaterbody1_0_GenericApplicationPropertyOfWaterSurface', True)

    
    GenericApplicationPropertyOfWaterSurface = property(__GenericApplicationPropertyOfWaterSurface.value, __GenericApplicationPropertyOfWaterSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}waterLevel uses Python identifier waterLevel
    __waterLevel = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'), 'waterLevel', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterSurfaceType_httpwww_opengis_netcitygmlwaterbody1_0waterLevel', False)

    
    waterLevel = property(__waterLevel.value, __waterLevel.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod2Surface ({http://www.opengis.net/citygml/waterbody/1.0}lod2Surface) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterBoundarySurfaceType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractWaterBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfWaterSurface.name() : __GenericApplicationPropertyOfWaterSurface,
        __waterLevel.name() : __waterLevel
    })
    _AttributeMap = AbstractWaterBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'WaterSurfaceType', WaterSurfaceType)


# Complex type BoundedByWaterSurfacePropertyType with content type ELEMENT_ONLY
class BoundedByWaterSurfacePropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BoundedByWaterSurfacePropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}_WaterBoundarySurface uses Python identifier WaterBoundarySurface
    __WaterBoundarySurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_WaterBoundarySurface'), 'WaterBoundarySurface', '__httpwww_opengis_netcitygmlwaterbody1_0_BoundedByWaterSurfacePropertyType_httpwww_opengis_netcitygmlwaterbody1_0_WaterBoundarySurface', False)

    
    WaterBoundarySurface = property(__WaterBoundarySurface.value, __WaterBoundarySurface.set, None, None)

    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __WaterBoundarySurface.name() : __WaterBoundarySurface
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BoundedByWaterSurfacePropertyType', BoundedByWaterSurfacePropertyType)


# Complex type WaterBodyType with content type ELEMENT_ONLY
class WaterBodyType (AbstractWaterObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WaterBodyType')
    # Base type is AbstractWaterObjectType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod0MultiCurve uses Python identifier lod0MultiCurve
    __lod0MultiCurve = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiCurve'), 'lod0MultiCurve', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0lod0MultiCurve', False)

    
    lod0MultiCurve = property(__lod0MultiCurve.value, __lod0MultiCurve.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod1MultiSurface uses Python identifier lod1MultiSurface
    __lod1MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), 'lod1MultiSurface', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0lod1MultiSurface', False)

    
    lod1MultiSurface = property(__lod1MultiSurface.value, __lod1MultiSurface.set, None, None)

    
    # Element GenericApplicationPropertyOfWaterObject ({http://www.opengis.net/citygml/waterbody/1.0}_GenericApplicationPropertyOfWaterObject) inherited from {http://www.opengis.net/citygml/waterbody/1.0}AbstractWaterObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod1MultiCurve uses Python identifier lod1MultiCurve
    __lod1MultiCurve = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'), 'lod1MultiCurve', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0lod1MultiCurve', False)

    
    lod1MultiCurve = property(__lod1MultiCurve.value, __lod1MultiCurve.set, None, None)

    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}_GenericApplicationPropertyOfWaterBody uses Python identifier GenericApplicationPropertyOfWaterBody
    __GenericApplicationPropertyOfWaterBody = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'), 'GenericApplicationPropertyOfWaterBody', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0_GenericApplicationPropertyOfWaterBody', True)

    
    GenericApplicationPropertyOfWaterBody = property(__GenericApplicationPropertyOfWaterBody.value, __GenericApplicationPropertyOfWaterBody.set, None, None)

    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod2Solid uses Python identifier lod2Solid
    __lod2Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'), 'lod2Solid', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0lod2Solid', False)

    
    lod2Solid = property(__lod2Solid.value, __lod2Solid.set, None, None)

    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod3Solid uses Python identifier lod3Solid
    __lod3Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'), 'lod3Solid', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0lod3Solid', False)

    
    lod3Solid = property(__lod3Solid.value, __lod3Solid.set, None, None)

    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod4Solid uses Python identifier lod4Solid
    __lod4Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'), 'lod4Solid', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0lod4Solid', False)

    
    lod4Solid = property(__lod4Solid.value, __lod4Solid.set, None, None)

    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod0MultiSurface uses Python identifier lod0MultiSurface
    __lod0MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'), 'lod0MultiSurface', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0lod0MultiSurface', False)

    
    lod0MultiSurface = property(__lod0MultiSurface.value, __lod0MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}boundedBy uses Python identifier boundedBy_
    __boundedBy_ = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'), 'boundedBy_', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0boundedBy', True)

    
    boundedBy_ = property(__boundedBy_.value, __boundedBy_.set, None, None)

    
    # Element {http://www.opengis.net/citygml/waterbody/1.0}lod1Solid uses Python identifier lod1Solid
    __lod1Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'), 'lod1Solid', '__httpwww_opengis_netcitygmlwaterbody1_0_WaterBodyType_httpwww_opengis_netcitygmlwaterbody1_0lod1Solid', False)

    
    lod1Solid = property(__lod1Solid.value, __lod1Solid.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractWaterObjectType._ElementMap.copy()
    _ElementMap.update({
        __usage.name() : __usage,
        __lod0MultiCurve.name() : __lod0MultiCurve,
        __class.name() : __class,
        __function.name() : __function,
        __lod1MultiSurface.name() : __lod1MultiSurface,
        __lod1MultiCurve.name() : __lod1MultiCurve,
        __GenericApplicationPropertyOfWaterBody.name() : __GenericApplicationPropertyOfWaterBody,
        __lod2Solid.name() : __lod2Solid,
        __lod3Solid.name() : __lod3Solid,
        __lod4Solid.name() : __lod4Solid,
        __lod0MultiSurface.name() : __lod0MultiSurface,
        __boundedBy_.name() : __boundedBy_,
        __lod1Solid.name() : __lod1Solid
    })
    _AttributeMap = AbstractWaterObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'WaterBodyType', WaterBodyType)


WaterGroundSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WaterGroundSurface'), WaterGroundSurfaceType)
Namespace.addCategoryObject('elementBinding', WaterGroundSurface.name().localName(), WaterGroundSurface)

GenericApplicationPropertyOfWaterObject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfWaterObject.name().localName(), GenericApplicationPropertyOfWaterObject)

WaterBoundarySurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_WaterBoundarySurface'), AbstractWaterBoundarySurfaceType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', WaterBoundarySurface.name().localName(), WaterBoundarySurface)

GenericApplicationPropertyOfWaterBoundarySurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfWaterBoundarySurface.name().localName(), GenericApplicationPropertyOfWaterBoundarySurface)

WaterObject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_WaterObject'), AbstractWaterObjectType)
Namespace.addCategoryObject('elementBinding', WaterObject.name().localName(), WaterObject)

GenericApplicationPropertyOfWaterSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfWaterSurface.name().localName(), GenericApplicationPropertyOfWaterSurface)

GenericApplicationPropertyOfWaterGroundSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfWaterGroundSurface.name().localName(), GenericApplicationPropertyOfWaterGroundSurface)

WaterClosureSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WaterClosureSurface'), WaterClosureSurfaceType)
Namespace.addCategoryObject('elementBinding', WaterClosureSurface.name().localName(), WaterClosureSurface)

WaterSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WaterSurface'), WaterSurfaceType)
Namespace.addCategoryObject('elementBinding', WaterSurface.name().localName(), WaterSurface)

GenericApplicationPropertyOfWaterClosureSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfWaterClosureSurface.name().localName(), GenericApplicationPropertyOfWaterClosureSurface)

WaterBody = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WaterBody'), WaterBodyType)
Namespace.addCategoryObject('elementBinding', WaterBody.name().localName(), WaterBody)

GenericApplicationPropertyOfWaterBody = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfWaterBody.name().localName(), GenericApplicationPropertyOfWaterBody)



AbstractWaterBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractWaterBoundarySurfaceType))

AbstractWaterBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'), pyxb.bundles.opengis.gml.SurfacePropertyType, scope=AbstractWaterBoundarySurfaceType))

AbstractWaterBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'), pyxb.bundles.opengis.gml.SurfacePropertyType, scope=AbstractWaterBoundarySurfaceType))

AbstractWaterBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'), pyxb.bundles.opengis.gml.SurfacePropertyType, scope=AbstractWaterBoundarySurfaceType))
AbstractWaterBoundarySurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractWaterBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
    ])
})



WaterGroundSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=WaterGroundSurfaceType))
WaterGroundSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterGroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterGroundSurface'))),
    ])
})



AbstractWaterObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractWaterObjectType))
AbstractWaterObjectType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractWaterObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
})



WaterClosureSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=WaterClosureSurfaceType))
WaterClosureSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterClosureSurface'))),
    ])
})



WaterSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=WaterSurfaceType))

WaterSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'), WaterLevelType, scope=WaterSurfaceType))
WaterSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Surface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'waterLevel'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Surface'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterSurface'))),
    ])
})



BoundedByWaterSurfacePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_WaterBoundarySurface'), AbstractWaterBoundarySurfaceType, abstract=pyxb.binding.datatypes.boolean(1), scope=BoundedByWaterSurfacePropertyType))
BoundedByWaterSurfacePropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BoundedByWaterSurfacePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_WaterBoundarySurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), WaterBodyUsageType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiCurve'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), WaterBodyClassType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), WaterBodyFunctionType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'), BoundedByWaterSurfacePropertyType, scope=WaterBodyType))

WaterBodyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=WaterBodyType))
WaterBodyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
    , 16 : pyxb.binding.content.ContentModelState(state=16, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWaterBody'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WaterBodyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiCurve'))),
    ])
})

WaterGroundSurface._setSubstitutionGroup(WaterBoundarySurface)

WaterBoundarySurface._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

WaterObject._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

WaterClosureSurface._setSubstitutionGroup(WaterBoundarySurface)

WaterSurface._setSubstitutionGroup(WaterBoundarySurface)

WaterBody._setSubstitutionGroup(WaterObject)
