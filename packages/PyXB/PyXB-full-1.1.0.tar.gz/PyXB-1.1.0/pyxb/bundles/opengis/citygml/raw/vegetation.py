# ./pyxb/bundles/opengis/citygml/raw/vegetation.py
# PyXB bindings for NamespaceModule
# NSM:1e40e4767881f4d9d133f72750b30d5dfdd3345b
# Generated 2009-11-30 18:12:13.814897 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:2b976c86-de0e-11de-8a60-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.citygml.base
import pyxb.bundles.opengis.gml

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/vegetation/1.0', create_if_missing=True)
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
class SpeciesType (pyxb.binding.datatypes.string):

    """Type of a Species. The values of this type are defined in the XML file SpeciesType.xml, according to
                the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SpeciesType')
    _Documentation = u'Type of a Species. The values of this type are defined in the XML file SpeciesType.xml, according to\n                the dictionary concept of GML3. '
SpeciesType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'SpeciesType', SpeciesType)

# Atomic SimpleTypeDefinition
class PlantCoverClassType (pyxb.binding.datatypes.string):

    """Class of a PlantCover. The values of this type are defined in the XML file PlantCoverClassType.xml,
                according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PlantCoverClassType')
    _Documentation = u'Class of a PlantCover. The values of this type are defined in the XML file PlantCoverClassType.xml,\n                according to the dictionary concept of GML3. '
PlantCoverClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'PlantCoverClassType', PlantCoverClassType)

# Atomic SimpleTypeDefinition
class PlantCoverFunctionType (pyxb.binding.datatypes.string):

    """Function of a PlantCover. The values of this type are defined in the XML file
                PlantCoverFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PlantCoverFunctionType')
    _Documentation = u'Function of a PlantCover. The values of this type are defined in the XML file\n                PlantCoverFunctionType.xml, according to the dictionary concept of GML3. '
PlantCoverFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'PlantCoverFunctionType', PlantCoverFunctionType)

# Atomic SimpleTypeDefinition
class PlantClassType (pyxb.binding.datatypes.string):

    """Class of a SolitaryVegetationObject. The values of this type are defined in the XML file
                PlantClassType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PlantClassType')
    _Documentation = u'Class of a SolitaryVegetationObject. The values of this type are defined in the XML file\n                PlantClassType.xml, according to the dictionary concept of GML3. '
PlantClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'PlantClassType', PlantClassType)

# Atomic SimpleTypeDefinition
class PlantFunctionType (pyxb.binding.datatypes.string):

    """Function of a PlantType. The values of this type are defined in the XML file PlantFunctionType.xml,
                according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PlantFunctionType')
    _Documentation = u'Function of a PlantType. The values of this type are defined in the XML file PlantFunctionType.xml,\n                according to the dictionary concept of GML3. '
PlantFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'PlantFunctionType', PlantFunctionType)

# Complex type AbstractVegetationObjectType with content type ELEMENT_ONLY
class AbstractVegetationObjectType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractVegetationObjectType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}_GenericApplicationPropertyOfVegetationObject uses Python identifier GenericApplicationPropertyOfVegetationObject
    __GenericApplicationPropertyOfVegetationObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'), 'GenericApplicationPropertyOfVegetationObject', '__httpwww_opengis_netcitygmlvegetation1_0_AbstractVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0_GenericApplicationPropertyOfVegetationObject', True)

    
    GenericApplicationPropertyOfVegetationObject = property(__GenericApplicationPropertyOfVegetationObject.value, __GenericApplicationPropertyOfVegetationObject.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfVegetationObject.name() : __GenericApplicationPropertyOfVegetationObject
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractVegetationObjectType', AbstractVegetationObjectType)


# Complex type SolitaryVegetationObjectType with content type ELEMENT_ONLY
class SolitaryVegetationObjectType (AbstractVegetationObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SolitaryVegetationObjectType')
    # Base type is AbstractVegetationObjectType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}species uses Python identifier species
    __species = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'species'), 'species', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0species', False)

    
    species = property(__species.value, __species.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}trunkDiameter uses Python identifier trunkDiameter
    __trunkDiameter = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'), 'trunkDiameter', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0trunkDiameter', False)

    
    trunkDiameter = property(__trunkDiameter.value, __trunkDiameter.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}crownDiameter uses Python identifier crownDiameter
    __crownDiameter = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'), 'crownDiameter', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0crownDiameter', False)

    
    crownDiameter = property(__crownDiameter.value, __crownDiameter.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}height uses Python identifier height
    __height = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'height'), 'height', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0height', False)

    
    height = property(__height.value, __height.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod1Geometry uses Python identifier lod1Geometry
    __lod1Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'), 'lod1Geometry', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0lod1Geometry', False)

    
    lod1Geometry = property(__lod1Geometry.value, __lod1Geometry.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod2Geometry uses Python identifier lod2Geometry
    __lod2Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'), 'lod2Geometry', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0lod2Geometry', False)

    
    lod2Geometry = property(__lod2Geometry.value, __lod2Geometry.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod3Geometry uses Python identifier lod3Geometry
    __lod3Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'), 'lod3Geometry', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0lod3Geometry', False)

    
    lod3Geometry = property(__lod3Geometry.value, __lod3Geometry.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod4Geometry uses Python identifier lod4Geometry
    __lod4Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), 'lod4Geometry', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0lod4Geometry', False)

    
    lod4Geometry = property(__lod4Geometry.value, __lod4Geometry.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod2ImplicitRepresentation uses Python identifier lod2ImplicitRepresentation
    __lod2ImplicitRepresentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'), 'lod2ImplicitRepresentation', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0lod2ImplicitRepresentation', False)

    
    lod2ImplicitRepresentation = property(__lod2ImplicitRepresentation.value, __lod2ImplicitRepresentation.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod3ImplicitRepresentation uses Python identifier lod3ImplicitRepresentation
    __lod3ImplicitRepresentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'), 'lod3ImplicitRepresentation', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0lod3ImplicitRepresentation', False)

    
    lod3ImplicitRepresentation = property(__lod3ImplicitRepresentation.value, __lod3ImplicitRepresentation.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod4ImplicitRepresentation uses Python identifier lod4ImplicitRepresentation
    __lod4ImplicitRepresentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'), 'lod4ImplicitRepresentation', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0lod4ImplicitRepresentation', False)

    
    lod4ImplicitRepresentation = property(__lod4ImplicitRepresentation.value, __lod4ImplicitRepresentation.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}_GenericApplicationPropertyOfSolitaryVegetationObject uses Python identifier GenericApplicationPropertyOfSolitaryVegetationObject
    __GenericApplicationPropertyOfSolitaryVegetationObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'), 'GenericApplicationPropertyOfSolitaryVegetationObject', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0_GenericApplicationPropertyOfSolitaryVegetationObject', True)

    
    GenericApplicationPropertyOfSolitaryVegetationObject = property(__GenericApplicationPropertyOfSolitaryVegetationObject.value, __GenericApplicationPropertyOfSolitaryVegetationObject.set, None, None)

    
    # Element GenericApplicationPropertyOfVegetationObject ({http://www.opengis.net/citygml/vegetation/1.0}_GenericApplicationPropertyOfVegetationObject) inherited from {http://www.opengis.net/citygml/vegetation/1.0}AbstractVegetationObjectType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod1ImplicitRepresentation uses Python identifier lod1ImplicitRepresentation
    __lod1ImplicitRepresentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'), 'lod1ImplicitRepresentation', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0lod1ImplicitRepresentation', False)

    
    lod1ImplicitRepresentation = property(__lod1ImplicitRepresentation.value, __lod1ImplicitRepresentation.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlvegetation1_0_SolitaryVegetationObjectType_httpwww_opengis_netcitygmlvegetation1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractVegetationObjectType._ElementMap.copy()
    _ElementMap.update({
        __species.name() : __species,
        __trunkDiameter.name() : __trunkDiameter,
        __crownDiameter.name() : __crownDiameter,
        __height.name() : __height,
        __lod1Geometry.name() : __lod1Geometry,
        __lod2Geometry.name() : __lod2Geometry,
        __lod3Geometry.name() : __lod3Geometry,
        __lod4Geometry.name() : __lod4Geometry,
        __lod2ImplicitRepresentation.name() : __lod2ImplicitRepresentation,
        __lod3ImplicitRepresentation.name() : __lod3ImplicitRepresentation,
        __lod4ImplicitRepresentation.name() : __lod4ImplicitRepresentation,
        __function.name() : __function,
        __GenericApplicationPropertyOfSolitaryVegetationObject.name() : __GenericApplicationPropertyOfSolitaryVegetationObject,
        __lod1ImplicitRepresentation.name() : __lod1ImplicitRepresentation,
        __class.name() : __class
    })
    _AttributeMap = AbstractVegetationObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SolitaryVegetationObjectType', SolitaryVegetationObjectType)


# Complex type PlantCoverType with content type ELEMENT_ONLY
class PlantCoverType (AbstractVegetationObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PlantCoverType')
    # Base type is AbstractVegetationObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}_GenericApplicationPropertyOfPlantCover uses Python identifier GenericApplicationPropertyOfPlantCover
    __GenericApplicationPropertyOfPlantCover = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'), 'GenericApplicationPropertyOfPlantCover', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0_GenericApplicationPropertyOfPlantCover', True)

    
    GenericApplicationPropertyOfPlantCover = property(__GenericApplicationPropertyOfPlantCover.value, __GenericApplicationPropertyOfPlantCover.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfVegetationObject ({http://www.opengis.net/citygml/vegetation/1.0}_GenericApplicationPropertyOfVegetationObject) inherited from {http://www.opengis.net/citygml/vegetation/1.0}AbstractVegetationObjectType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}averageHeight uses Python identifier averageHeight
    __averageHeight = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'averageHeight'), 'averageHeight', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0averageHeight', False)

    
    averageHeight = property(__averageHeight.value, __averageHeight.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod1MultiSurface uses Python identifier lod1MultiSurface
    __lod1MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), 'lod1MultiSurface', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0lod1MultiSurface', False)

    
    lod1MultiSurface = property(__lod1MultiSurface.value, __lod1MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod2MultiSurface uses Python identifier lod2MultiSurface
    __lod2MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), 'lod2MultiSurface', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0lod2MultiSurface', False)

    
    lod2MultiSurface = property(__lod2MultiSurface.value, __lod2MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod1MultiSolid uses Python identifier lod1MultiSolid
    __lod1MultiSolid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'), 'lod1MultiSolid', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0lod1MultiSolid', False)

    
    lod1MultiSolid = property(__lod1MultiSolid.value, __lod1MultiSolid.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod2MultiSolid uses Python identifier lod2MultiSolid
    __lod2MultiSolid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'), 'lod2MultiSolid', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0lod2MultiSolid', False)

    
    lod2MultiSolid = property(__lod2MultiSolid.value, __lod2MultiSolid.set, None, None)

    
    # Element {http://www.opengis.net/citygml/vegetation/1.0}lod3MultiSolid uses Python identifier lod3MultiSolid
    __lod3MultiSolid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'), 'lod3MultiSolid', '__httpwww_opengis_netcitygmlvegetation1_0_PlantCoverType_httpwww_opengis_netcitygmlvegetation1_0lod3MultiSolid', False)

    
    lod3MultiSolid = property(__lod3MultiSolid.value, __lod3MultiSolid.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractVegetationObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __GenericApplicationPropertyOfPlantCover.name() : __GenericApplicationPropertyOfPlantCover,
        __class.name() : __class,
        __function.name() : __function,
        __averageHeight.name() : __averageHeight,
        __lod1MultiSurface.name() : __lod1MultiSurface,
        __lod2MultiSurface.name() : __lod2MultiSurface,
        __lod3MultiSurface.name() : __lod3MultiSurface,
        __lod1MultiSolid.name() : __lod1MultiSolid,
        __lod2MultiSolid.name() : __lod2MultiSolid,
        __lod3MultiSolid.name() : __lod3MultiSolid
    })
    _AttributeMap = AbstractVegetationObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PlantCoverType', PlantCoverType)


SolitaryVegetationObject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SolitaryVegetationObject'), SolitaryVegetationObjectType)
Namespace.addCategoryObject('elementBinding', SolitaryVegetationObject.name().localName(), SolitaryVegetationObject)

GenericApplicationPropertyOfSolitaryVegetationObject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfSolitaryVegetationObject.name().localName(), GenericApplicationPropertyOfSolitaryVegetationObject)

GenericApplicationPropertyOfVegetationObject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfVegetationObject.name().localName(), GenericApplicationPropertyOfVegetationObject)

PlantCover = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PlantCover'), PlantCoverType)
Namespace.addCategoryObject('elementBinding', PlantCover.name().localName(), PlantCover)

GenericApplicationPropertyOfPlantCover = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfPlantCover.name().localName(), GenericApplicationPropertyOfPlantCover)

VegetationObject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_VegetationObject'), AbstractVegetationObjectType)
Namespace.addCategoryObject('elementBinding', VegetationObject.name().localName(), VegetationObject)



AbstractVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractVegetationObjectType))
AbstractVegetationObjectType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
})



SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'species'), SpeciesType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'), pyxb.bundles.opengis.gml.LengthType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'), pyxb.bundles.opengis.gml.LengthType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'height'), pyxb.bundles.opengis.gml.LengthType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'), pyxb.bundles.opengis.citygml.base.ImplicitRepresentationPropertyType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'), pyxb.bundles.opengis.citygml.base.ImplicitRepresentationPropertyType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'), pyxb.bundles.opengis.citygml.base.ImplicitRepresentationPropertyType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), PlantFunctionType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'), pyxb.bundles.opengis.citygml.base.ImplicitRepresentationPropertyType, scope=SolitaryVegetationObjectType))

SolitaryVegetationObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), PlantClassType, scope=SolitaryVegetationObjectType))
SolitaryVegetationObjectType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'species'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'height'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'species'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'height'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'species'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'height'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'species'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'height'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'species'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'height'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'height'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'species'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'height'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'species'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'height'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
    ])
    , 16 : pyxb.binding.content.ContentModelState(state=16, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'species'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'crownDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'trunkDiameter'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'height'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
    ])
    , 17 : pyxb.binding.content.ContentModelState(state=17, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
    ])
    , 18 : pyxb.binding.content.ContentModelState(state=18, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
    ])
    , 19 : pyxb.binding.content.ContentModelState(state=19, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
    ])
    , 20 : pyxb.binding.content.ContentModelState(state=20, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SolitaryVegetationObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSolitaryVegetationObject'))),
    ])
})



PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=PlantCoverType))

PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=PlantCoverType))

PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), PlantCoverClassType, scope=PlantCoverType))

PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), PlantCoverFunctionType, scope=PlantCoverType))

PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'averageHeight'), pyxb.bundles.opengis.gml.LengthType, scope=PlantCoverType))

PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=PlantCoverType))

PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=PlantCoverType))

PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=PlantCoverType))

PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'), pyxb.bundles.opengis.gml.MultiSolidPropertyType, scope=PlantCoverType))

PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'), pyxb.bundles.opengis.gml.MultiSolidPropertyType, scope=PlantCoverType))

PlantCoverType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'), pyxb.bundles.opengis.gml.MultiSolidPropertyType, scope=PlantCoverType))
PlantCoverType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'averageHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'averageHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'averageHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'averageHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'averageHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'averageHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'averageHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'averageHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfVegetationObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
    ])
    , 16 : pyxb.binding.content.ContentModelState(state=16, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSolid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfPlantCover'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PlantCoverType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSolid'))),
    ])
})

SolitaryVegetationObject._setSubstitutionGroup(VegetationObject)

PlantCover._setSubstitutionGroup(VegetationObject)

VegetationObject._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)
