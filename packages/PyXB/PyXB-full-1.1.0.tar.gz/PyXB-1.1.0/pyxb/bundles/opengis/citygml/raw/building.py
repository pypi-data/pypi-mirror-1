# ./pyxb/bundles/opengis/citygml/raw/building.py
# PyXB bindings for NamespaceModule
# NSM:1b4db361dcbc3199fe760558a815e57bc06d92f7
# Generated 2009-11-30 18:11:29.405101 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:10ed2f92-de0e-11de-bfcf-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.citygml.base
import pyxb.bundles.opengis.gml

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/building/1.0', create_if_missing=True)
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
class RoomClassType (pyxb.binding.datatypes.string):

    """Class of a room . The values of this type are defined in the XML file RoomClassType.xml, according
                to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoomClassType')
    _Documentation = u'Class of a room . The values of this type are defined in the XML file RoomClassType.xml, according\n                to the dictionary concept of GML3. '
RoomClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'RoomClassType', RoomClassType)

# Atomic SimpleTypeDefinition
class RoomUsageType (pyxb.binding.datatypes.string):

    """Actual Usage of a room. The values of this type are defined in the XML file RoomUsageType.xml,
                according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoomUsageType')
    _Documentation = u'Actual Usage of a room. The values of this type are defined in the XML file RoomUsageType.xml,\n                according to the dictionary concept of GML3. '
RoomUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'RoomUsageType', RoomUsageType)

# Atomic SimpleTypeDefinition
class BuildingInstallationFunctionType (pyxb.binding.datatypes.string):

    """Function of a building installation. The values of this type are defined in the XML file
                BuildingInstallationFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallationFunctionType')
    _Documentation = u'Function of a building installation. The values of this type are defined in the XML file\n                BuildingInstallationFunctionType.xml, according to the dictionary concept of GML3. '
BuildingInstallationFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingInstallationFunctionType', BuildingInstallationFunctionType)

# Atomic SimpleTypeDefinition
class BuildingClassType (pyxb.binding.datatypes.string):

    """ Class of a building. The values of this type are defined in the XML file BuildingClassType.xml,
                according to the dictionary concept of GML3."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingClassType')
    _Documentation = u' Class of a building. The values of this type are defined in the XML file BuildingClassType.xml,\n                according to the dictionary concept of GML3.'
BuildingClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingClassType', BuildingClassType)

# Atomic SimpleTypeDefinition
class IntBuildingInstallationClassType (pyxb.binding.datatypes.string):

    """Class of an interior building installation. The values of this type are defined in the XML file
                IntBuildingInstallationClassType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallationClassType')
    _Documentation = u'Class of an interior building installation. The values of this type are defined in the XML file\n                IntBuildingInstallationClassType.xml, according to the dictionary concept of GML3. '
IntBuildingInstallationClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'IntBuildingInstallationClassType', IntBuildingInstallationClassType)

# Atomic SimpleTypeDefinition
class BuildingFunctionType (pyxb.binding.datatypes.string):

    """ Intended function of a building. The values of this type are defined in the XML file
                BuildingFunctionType.xml, according to the dictionary concept of GML3. The values may be adopted from ALKIS, the
                german standard for cadastre modelling. If the cadastre models from other countries differ in the building
                functions, these values may be compiled in another codelist to be used with CityGML. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingFunctionType')
    _Documentation = u' Intended function of a building. The values of this type are defined in the XML file\n                BuildingFunctionType.xml, according to the dictionary concept of GML3. The values may be adopted from ALKIS, the\n                german standard for cadastre modelling. If the cadastre models from other countries differ in the building\n                functions, these values may be compiled in another codelist to be used with CityGML. '
BuildingFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingFunctionType', BuildingFunctionType)

# Atomic SimpleTypeDefinition
class IntBuildingInstallationUsageType (pyxb.binding.datatypes.string):

    """Actual Usage of an interior building installation. The values of this type are defined in the XML
                file IntBuildingInstallationUsageType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallationUsageType')
    _Documentation = u'Actual Usage of an interior building installation. The values of this type are defined in the XML\n                file IntBuildingInstallationUsageType.xml, according to the dictionary concept of GML3. '
IntBuildingInstallationUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'IntBuildingInstallationUsageType', IntBuildingInstallationUsageType)

# Atomic SimpleTypeDefinition
class RoofTypeType (pyxb.binding.datatypes.string):

    """Roof Types. The values of this type are defined in the XML file RoofTypeType.xml, according to the
                dictionary concept of GML3."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoofTypeType')
    _Documentation = u'Roof Types. The values of this type are defined in the XML file RoofTypeType.xml, according to the\n                dictionary concept of GML3.'
RoofTypeType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'RoofTypeType', RoofTypeType)

# Atomic SimpleTypeDefinition
class BuildingFurnitureFunctionType (pyxb.binding.datatypes.string):

    """ Function of a building furniture. The values of this type are defined in the XML file
                BuildingFurnitureFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingFurnitureFunctionType')
    _Documentation = u' Function of a building furniture. The values of this type are defined in the XML file\n                BuildingFurnitureFunctionType.xml, according to the dictionary concept of GML3. '
BuildingFurnitureFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingFurnitureFunctionType', BuildingFurnitureFunctionType)

# Atomic SimpleTypeDefinition
class RoomFunctionType (pyxb.binding.datatypes.string):

    """Function of a room. The values of this type are defined in the XML file RoomFunctionType.xml,
                according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoomFunctionType')
    _Documentation = u'Function of a room. The values of this type are defined in the XML file RoomFunctionType.xml,\n                according to the dictionary concept of GML3. '
RoomFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'RoomFunctionType', RoomFunctionType)

# Atomic SimpleTypeDefinition
class BuildingFurnitureClassType (pyxb.binding.datatypes.string):

    """ Class of a building furniture. The values of this type are defined in the XML file
                BuildingFurnitureClassType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingFurnitureClassType')
    _Documentation = u' Class of a building furniture. The values of this type are defined in the XML file\n                BuildingFurnitureClassType.xml, according to the dictionary concept of GML3. '
BuildingFurnitureClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingFurnitureClassType', BuildingFurnitureClassType)

# Atomic SimpleTypeDefinition
class BuildingInstallationUsageType (pyxb.binding.datatypes.string):

    """Actual usage of a building installation. The values of this type are defined in the XML file
                BuildingInstallationUsageType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallationUsageType')
    _Documentation = u'Actual usage of a building installation. The values of this type are defined in the XML file\n                BuildingInstallationUsageType.xml, according to the dictionary concept of GML3. '
BuildingInstallationUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingInstallationUsageType', BuildingInstallationUsageType)

# Atomic SimpleTypeDefinition
class IntBuildingInstallationFunctionType (pyxb.binding.datatypes.string):

    """Function of an interior building installation. The values of this type are defined in the XML file
                IntBuildingInstallationFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallationFunctionType')
    _Documentation = u'Function of an interior building installation. The values of this type are defined in the XML file\n                IntBuildingInstallationFunctionType.xml, according to the dictionary concept of GML3. '
IntBuildingInstallationFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'IntBuildingInstallationFunctionType', IntBuildingInstallationFunctionType)

# Atomic SimpleTypeDefinition
class BuildingUsageType (pyxb.binding.datatypes.string):

    """ Actual usage of a building. The values of this type are defined in the XML file
                BuildingUsageType.xml, according to the dictionary concept of GML3."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingUsageType')
    _Documentation = u' Actual usage of a building. The values of this type are defined in the XML file\n                BuildingUsageType.xml, according to the dictionary concept of GML3.'
BuildingUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingUsageType', BuildingUsageType)

# Atomic SimpleTypeDefinition
class BuildingInstallationClassType (pyxb.binding.datatypes.string):

    """Class of a building installation. The values of this type are defined in the XML file
                BuildingInstallationClassType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallationClassType')
    _Documentation = u'Class of a building installation. The values of this type are defined in the XML file\n                BuildingInstallationClassType.xml, according to the dictionary concept of GML3. '
BuildingInstallationClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingInstallationClassType', BuildingInstallationClassType)

# Atomic SimpleTypeDefinition
class BuildingFurnitureUsageType (pyxb.binding.datatypes.string):

    """ Actual Usage of a building Furniture. The values of this type are defined in the XML file
                BuildingFurnitureUsageType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingFurnitureUsageType')
    _Documentation = u' Actual Usage of a building Furniture. The values of this type are defined in the XML file\n                BuildingFurnitureUsageType.xml, according to the dictionary concept of GML3. '
BuildingFurnitureUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingFurnitureUsageType', BuildingFurnitureUsageType)

# Complex type RoomType with content type ELEMENT_ONLY
class RoomType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoomType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}interiorFurniture uses Python identifier interiorFurniture
    __interiorFurniture = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'), 'interiorFurniture', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0interiorFurniture', True)

    
    interiorFurniture = property(__interiorFurniture.value, __interiorFurniture.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfRoom uses Python identifier GenericApplicationPropertyOfRoom
    __GenericApplicationPropertyOfRoom = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'), 'GenericApplicationPropertyOfRoom', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfRoom', True)

    
    GenericApplicationPropertyOfRoom = property(__GenericApplicationPropertyOfRoom.value, __GenericApplicationPropertyOfRoom.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}roomInstallation uses Python identifier roomInstallation
    __roomInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'), 'roomInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0roomInstallation', True)

    
    roomInstallation = property(__roomInstallation.value, __roomInstallation.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4Solid uses Python identifier lod4Solid
    __lod4Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'), 'lod4Solid', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0lod4Solid', False)

    
    lod4Solid = property(__lod4Solid.value, __lod4Solid.set, None, None)

    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}boundedBy uses Python identifier boundedBy_
    __boundedBy_ = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'), 'boundedBy_', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0boundedBy', True)

    
    boundedBy_ = property(__boundedBy_.value, __boundedBy_.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __interiorFurniture.name() : __interiorFurniture,
        __GenericApplicationPropertyOfRoom.name() : __GenericApplicationPropertyOfRoom,
        __roomInstallation.name() : __roomInstallation,
        __class.name() : __class,
        __function.name() : __function,
        __usage.name() : __usage,
        __lod4Solid.name() : __lod4Solid,
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __boundedBy_.name() : __boundedBy_
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'RoomType', RoomType)


# Complex type InteriorFurniturePropertyType with content type ELEMENT_ONLY
class InteriorFurniturePropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InteriorFurniturePropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}BuildingFurniture uses Python identifier BuildingFurniture
    __BuildingFurniture = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingFurniture'), 'BuildingFurniture', '__httpwww_opengis_netcitygmlbuilding1_0_InteriorFurniturePropertyType_httpwww_opengis_netcitygmlbuilding1_0BuildingFurniture', False)

    
    BuildingFurniture = property(__BuildingFurniture.value, __BuildingFurniture.set, None, None)

    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __BuildingFurniture.name() : __BuildingFurniture
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'InteriorFurniturePropertyType', InteriorFurniturePropertyType)


# Complex type IntBuildingInstallationType with content type ELEMENT_ONLY
class IntBuildingInstallationType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallationType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4Geometry uses Python identifier lod4Geometry
    __lod4Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), 'lod4Geometry', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0lod4Geometry', False)

    
    lod4Geometry = property(__lod4Geometry.value, __lod4Geometry.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfIntBuildingInstallation uses Python identifier GenericApplicationPropertyOfIntBuildingInstallation
    __GenericApplicationPropertyOfIntBuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'), 'GenericApplicationPropertyOfIntBuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfIntBuildingInstallation', True)

    
    GenericApplicationPropertyOfIntBuildingInstallation = property(__GenericApplicationPropertyOfIntBuildingInstallation.value, __GenericApplicationPropertyOfIntBuildingInstallation.set, None, None)

    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod4Geometry.name() : __lod4Geometry,
        __class.name() : __class,
        __GenericApplicationPropertyOfIntBuildingInstallation.name() : __GenericApplicationPropertyOfIntBuildingInstallation,
        __function.name() : __function,
        __usage.name() : __usage
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'IntBuildingInstallationType', IntBuildingInstallationType)


# Complex type AbstractBuildingType with content type ELEMENT_ONLY
class AbstractBuildingType (pyxb.bundles.opengis.citygml.base.AbstractSiteType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractBuildingType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractSiteType
    
    # Element {http://www.opengis.net/citygml/building/1.0}interiorBuildingInstallation uses Python identifier interiorBuildingInstallation
    __interiorBuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'), 'interiorBuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0interiorBuildingInstallation', True)

    
    interiorBuildingInstallation = property(__interiorBuildingInstallation.value, __interiorBuildingInstallation.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}boundedBy uses Python identifier boundedBy_
    __boundedBy_ = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'), 'boundedBy_', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0boundedBy', True)

    
    boundedBy_ = property(__boundedBy_.value, __boundedBy_.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3Solid uses Python identifier lod3Solid
    __lod3Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'), 'lod3Solid', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod3Solid', False)

    
    lod3Solid = property(__lod3Solid.value, __lod3Solid.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}yearOfDemolition uses Python identifier yearOfDemolition
    __yearOfDemolition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'), 'yearOfDemolition', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0yearOfDemolition', False)

    
    yearOfDemolition = property(__yearOfDemolition.value, __yearOfDemolition.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3TerrainIntersection uses Python identifier lod3TerrainIntersection
    __lod3TerrainIntersection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'), 'lod3TerrainIntersection', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod3TerrainIntersection', False)

    
    lod3TerrainIntersection = property(__lod3TerrainIntersection.value, __lod3TerrainIntersection.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4Solid uses Python identifier lod4Solid
    __lod4Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'), 'lod4Solid', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod4Solid', False)

    
    lod4Solid = property(__lod4Solid.value, __lod4Solid.set, None, None)

    
    # Element GenericApplicationPropertyOfSite ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfSite) inherited from {http://www.opengis.net/citygml/1.0}AbstractSiteType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4MultiCurve uses Python identifier lod4MultiCurve
    __lod4MultiCurve = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'), 'lod4MultiCurve', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod4MultiCurve', False)

    
    lod4MultiCurve = property(__lod4MultiCurve.value, __lod4MultiCurve.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4TerrainIntersection uses Python identifier lod4TerrainIntersection
    __lod4TerrainIntersection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'), 'lod4TerrainIntersection', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod4TerrainIntersection', False)

    
    lod4TerrainIntersection = property(__lod4TerrainIntersection.value, __lod4TerrainIntersection.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}interiorRoom uses Python identifier interiorRoom
    __interiorRoom = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'), 'interiorRoom', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0interiorRoom', True)

    
    interiorRoom = property(__interiorRoom.value, __interiorRoom.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}consistsOfBuildingPart uses Python identifier consistsOfBuildingPart
    __consistsOfBuildingPart = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'), 'consistsOfBuildingPart', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0consistsOfBuildingPart', True)

    
    consistsOfBuildingPart = property(__consistsOfBuildingPart.value, __consistsOfBuildingPart.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}address uses Python identifier address
    __address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'address'), 'address', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0address', True)

    
    address = property(__address.value, __address.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}yearOfConstruction uses Python identifier yearOfConstruction
    __yearOfConstruction = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'), 'yearOfConstruction', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0yearOfConstruction', False)

    
    yearOfConstruction = property(__yearOfConstruction.value, __yearOfConstruction.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}measuredHeight uses Python identifier measuredHeight
    __measuredHeight = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'), 'measuredHeight', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0measuredHeight', False)

    
    measuredHeight = property(__measuredHeight.value, __measuredHeight.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}storeysAboveGround uses Python identifier storeysAboveGround
    __storeysAboveGround = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'), 'storeysAboveGround', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0storeysAboveGround', False)

    
    storeysAboveGround = property(__storeysAboveGround.value, __storeysAboveGround.set, None, None)

    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}storeysBelowGround uses Python identifier storeysBelowGround
    __storeysBelowGround = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'), 'storeysBelowGround', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0storeysBelowGround', False)

    
    storeysBelowGround = property(__storeysBelowGround.value, __storeysBelowGround.set, None, None)

    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}storeyHeightsBelowGround uses Python identifier storeyHeightsBelowGround
    __storeyHeightsBelowGround = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'), 'storeyHeightsBelowGround', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0storeyHeightsBelowGround', False)

    
    storeyHeightsBelowGround = property(__storeyHeightsBelowGround.value, __storeyHeightsBelowGround.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod1Solid uses Python identifier lod1Solid
    __lod1Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'), 'lod1Solid', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod1Solid', False)

    
    lod1Solid = property(__lod1Solid.value, __lod1Solid.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod1MultiSurface uses Python identifier lod1MultiSurface
    __lod1MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), 'lod1MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod1MultiSurface', False)

    
    lod1MultiSurface = property(__lod1MultiSurface.value, __lod1MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}roofType uses Python identifier roofType
    __roofType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'roofType'), 'roofType', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0roofType', False)

    
    roofType = property(__roofType.value, __roofType.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod1TerrainIntersection uses Python identifier lod1TerrainIntersection
    __lod1TerrainIntersection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'), 'lod1TerrainIntersection', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod1TerrainIntersection', False)

    
    lod1TerrainIntersection = property(__lod1TerrainIntersection.value, __lod1TerrainIntersection.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3MultiCurve uses Python identifier lod3MultiCurve
    __lod3MultiCurve = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'), 'lod3MultiCurve', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod3MultiCurve', False)

    
    lod3MultiCurve = property(__lod3MultiCurve.value, __lod3MultiCurve.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}storeyHeightsAboveGround uses Python identifier storeyHeightsAboveGround
    __storeyHeightsAboveGround = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'), 'storeyHeightsAboveGround', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0storeyHeightsAboveGround', False)

    
    storeyHeightsAboveGround = property(__storeyHeightsAboveGround.value, __storeyHeightsAboveGround.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2Solid uses Python identifier lod2Solid
    __lod2Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'), 'lod2Solid', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod2Solid', False)

    
    lod2Solid = property(__lod2Solid.value, __lod2Solid.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfAbstractBuilding uses Python identifier GenericApplicationPropertyOfAbstractBuilding
    __GenericApplicationPropertyOfAbstractBuilding = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'), 'GenericApplicationPropertyOfAbstractBuilding', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfAbstractBuilding', True)

    
    GenericApplicationPropertyOfAbstractBuilding = property(__GenericApplicationPropertyOfAbstractBuilding.value, __GenericApplicationPropertyOfAbstractBuilding.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2MultiSurface uses Python identifier lod2MultiSurface
    __lod2MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), 'lod2MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod2MultiSurface', False)

    
    lod2MultiSurface = property(__lod2MultiSurface.value, __lod2MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2MultiCurve uses Python identifier lod2MultiCurve
    __lod2MultiCurve = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'), 'lod2MultiCurve', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod2MultiCurve', False)

    
    lod2MultiCurve = property(__lod2MultiCurve.value, __lod2MultiCurve.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2TerrainIntersection uses Python identifier lod2TerrainIntersection
    __lod2TerrainIntersection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'), 'lod2TerrainIntersection', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod2TerrainIntersection', False)

    
    lod2TerrainIntersection = property(__lod2TerrainIntersection.value, __lod2TerrainIntersection.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}outerBuildingInstallation uses Python identifier outerBuildingInstallation
    __outerBuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'), 'outerBuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0outerBuildingInstallation', True)

    
    outerBuildingInstallation = property(__outerBuildingInstallation.value, __outerBuildingInstallation.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractSiteType._ElementMap.copy()
    _ElementMap.update({
        __interiorBuildingInstallation.name() : __interiorBuildingInstallation,
        __boundedBy_.name() : __boundedBy_,
        __lod3Solid.name() : __lod3Solid,
        __lod3MultiSurface.name() : __lod3MultiSurface,
        __yearOfDemolition.name() : __yearOfDemolition,
        __lod3TerrainIntersection.name() : __lod3TerrainIntersection,
        __lod4Solid.name() : __lod4Solid,
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __lod4MultiCurve.name() : __lod4MultiCurve,
        __lod4TerrainIntersection.name() : __lod4TerrainIntersection,
        __interiorRoom.name() : __interiorRoom,
        __consistsOfBuildingPart.name() : __consistsOfBuildingPart,
        __class.name() : __class,
        __address.name() : __address,
        __function.name() : __function,
        __usage.name() : __usage,
        __yearOfConstruction.name() : __yearOfConstruction,
        __measuredHeight.name() : __measuredHeight,
        __storeysAboveGround.name() : __storeysAboveGround,
        __storeysBelowGround.name() : __storeysBelowGround,
        __storeyHeightsBelowGround.name() : __storeyHeightsBelowGround,
        __lod1Solid.name() : __lod1Solid,
        __lod1MultiSurface.name() : __lod1MultiSurface,
        __roofType.name() : __roofType,
        __lod1TerrainIntersection.name() : __lod1TerrainIntersection,
        __lod3MultiCurve.name() : __lod3MultiCurve,
        __storeyHeightsAboveGround.name() : __storeyHeightsAboveGround,
        __lod2Solid.name() : __lod2Solid,
        __GenericApplicationPropertyOfAbstractBuilding.name() : __GenericApplicationPropertyOfAbstractBuilding,
        __lod2MultiSurface.name() : __lod2MultiSurface,
        __lod2MultiCurve.name() : __lod2MultiCurve,
        __lod2TerrainIntersection.name() : __lod2TerrainIntersection,
        __outerBuildingInstallation.name() : __outerBuildingInstallation
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractSiteType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractBuildingType', AbstractBuildingType)


# Complex type BuildingPartType with content type ELEMENT_ONLY
class BuildingPartType (AbstractBuildingType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingPartType')
    # Base type is AbstractBuildingType
    
    # Element interiorBuildingInstallation ({http://www.opengis.net/citygml/building/1.0}interiorBuildingInstallation) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3Solid ({http://www.opengis.net/citygml/building/1.0}lod3Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element yearOfDemolition ({http://www.opengis.net/citygml/building/1.0}yearOfDemolition) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod3TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod3TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4Solid ({http://www.opengis.net/citygml/building/1.0}lod4Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfSite ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfSite) inherited from {http://www.opengis.net/citygml/1.0}AbstractSiteType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod4MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod4TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element interiorRoom ({http://www.opengis.net/citygml/building/1.0}interiorRoom) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element consistsOfBuildingPart ({http://www.opengis.net/citygml/building/1.0}consistsOfBuildingPart) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element class_ ({http://www.opengis.net/citygml/building/1.0}class) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element address ({http://www.opengis.net/citygml/building/1.0}address) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod1Solid ({http://www.opengis.net/citygml/building/1.0}lod1Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element function ({http://www.opengis.net/citygml/building/1.0}function) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element usage ({http://www.opengis.net/citygml/building/1.0}usage) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element yearOfConstruction ({http://www.opengis.net/citygml/building/1.0}yearOfConstruction) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element measuredHeight ({http://www.opengis.net/citygml/building/1.0}measuredHeight) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeysAboveGround ({http://www.opengis.net/citygml/building/1.0}storeysAboveGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element storeysBelowGround ({http://www.opengis.net/citygml/building/1.0}storeysBelowGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element storeyHeightsBelowGround ({http://www.opengis.net/citygml/building/1.0}storeyHeightsBelowGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBuildingPart uses Python identifier GenericApplicationPropertyOfBuildingPart
    __GenericApplicationPropertyOfBuildingPart = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'), 'GenericApplicationPropertyOfBuildingPart', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingPartType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfBuildingPart', True)

    
    GenericApplicationPropertyOfBuildingPart = property(__GenericApplicationPropertyOfBuildingPart.value, __GenericApplicationPropertyOfBuildingPart.set, None, None)

    
    # Element boundedBy_ ({http://www.opengis.net/citygml/building/1.0}boundedBy) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod1MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod1MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element roofType ({http://www.opengis.net/citygml/building/1.0}roofType) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod1TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod1TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod3MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod3MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeyHeightsAboveGround ({http://www.opengis.net/citygml/building/1.0}storeyHeightsAboveGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2Solid ({http://www.opengis.net/citygml/building/1.0}lod2Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfAbstractBuilding ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfAbstractBuilding) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod2MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod2TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element outerBuildingInstallation ({http://www.opengis.net/citygml/building/1.0}outerBuildingInstallation) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBuildingType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfBuildingPart.name() : __GenericApplicationPropertyOfBuildingPart
    })
    _AttributeMap = AbstractBuildingType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingPartType', BuildingPartType)


# Complex type AbstractBoundarySurfaceType with content type ELEMENT_ONLY
class AbstractBoundarySurfaceType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractBoundarySurfaceType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2MultiSurface uses Python identifier lod2MultiSurface
    __lod2MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), 'lod2MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBoundarySurfaceType_httpwww_opengis_netcitygmlbuilding1_0lod2MultiSurface', False)

    
    lod2MultiSurface = property(__lod2MultiSurface.value, __lod2MultiSurface.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBoundarySurfaceType_httpwww_opengis_netcitygmlbuilding1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBoundarySurfaceType_httpwww_opengis_netcitygmlbuilding1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}opening uses Python identifier opening
    __opening = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'opening'), 'opening', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBoundarySurfaceType_httpwww_opengis_netcitygmlbuilding1_0opening', True)

    
    opening = property(__opening.value, __opening.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface uses Python identifier GenericApplicationPropertyOfBoundarySurface
    __GenericApplicationPropertyOfBoundarySurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'), 'GenericApplicationPropertyOfBoundarySurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBoundarySurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfBoundarySurface', True)

    
    GenericApplicationPropertyOfBoundarySurface = property(__GenericApplicationPropertyOfBoundarySurface.value, __GenericApplicationPropertyOfBoundarySurface.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod2MultiSurface.name() : __lod2MultiSurface,
        __lod3MultiSurface.name() : __lod3MultiSurface,
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __opening.name() : __opening,
        __GenericApplicationPropertyOfBoundarySurface.name() : __GenericApplicationPropertyOfBoundarySurface
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractBoundarySurfaceType', AbstractBoundarySurfaceType)


# Complex type RoofSurfaceType with content type ELEMENT_ONLY
class RoofSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoofSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfRoofSurface uses Python identifier GenericApplicationPropertyOfRoofSurface
    __GenericApplicationPropertyOfRoofSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'), 'GenericApplicationPropertyOfRoofSurface', '__httpwww_opengis_netcitygmlbuilding1_0_RoofSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfRoofSurface', True)

    
    GenericApplicationPropertyOfRoofSurface = property(__GenericApplicationPropertyOfRoofSurface.value, __GenericApplicationPropertyOfRoofSurface.set, None, None)

    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfRoofSurface.name() : __GenericApplicationPropertyOfRoofSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'RoofSurfaceType', RoofSurfaceType)


# Complex type BuildingInstallationType with content type ELEMENT_ONLY
class BuildingInstallationType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallationType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2Geometry uses Python identifier lod2Geometry
    __lod2Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'), 'lod2Geometry', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0lod2Geometry', False)

    
    lod2Geometry = property(__lod2Geometry.value, __lod2Geometry.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3Geometry uses Python identifier lod3Geometry
    __lod3Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'), 'lod3Geometry', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0lod3Geometry', False)

    
    lod3Geometry = property(__lod3Geometry.value, __lod3Geometry.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4Geometry uses Python identifier lod4Geometry
    __lod4Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), 'lod4Geometry', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0lod4Geometry', False)

    
    lod4Geometry = property(__lod4Geometry.value, __lod4Geometry.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBuildingInstallation uses Python identifier GenericApplicationPropertyOfBuildingInstallation
    __GenericApplicationPropertyOfBuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'), 'GenericApplicationPropertyOfBuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfBuildingInstallation', True)

    
    GenericApplicationPropertyOfBuildingInstallation = property(__GenericApplicationPropertyOfBuildingInstallation.value, __GenericApplicationPropertyOfBuildingInstallation.set, None, None)

    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod2Geometry.name() : __lod2Geometry,
        __lod3Geometry.name() : __lod3Geometry,
        __lod4Geometry.name() : __lod4Geometry,
        __usage.name() : __usage,
        __GenericApplicationPropertyOfBuildingInstallation.name() : __GenericApplicationPropertyOfBuildingInstallation,
        __class.name() : __class,
        __function.name() : __function
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingInstallationType', BuildingInstallationType)


# Complex type BuildingFurnitureType with content type ELEMENT_ONLY
class BuildingFurnitureType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingFurnitureType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBuildingFurniture uses Python identifier GenericApplicationPropertyOfBuildingFurniture
    __GenericApplicationPropertyOfBuildingFurniture = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'), 'GenericApplicationPropertyOfBuildingFurniture', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfBuildingFurniture', True)

    
    GenericApplicationPropertyOfBuildingFurniture = property(__GenericApplicationPropertyOfBuildingFurniture.value, __GenericApplicationPropertyOfBuildingFurniture.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4Geometry uses Python identifier lod4Geometry
    __lod4Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), 'lod4Geometry', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0lod4Geometry', False)

    
    lod4Geometry = property(__lod4Geometry.value, __lod4Geometry.set, None, None)

    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4ImplicitRepresentation uses Python identifier lod4ImplicitRepresentation
    __lod4ImplicitRepresentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'), 'lod4ImplicitRepresentation', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0lod4ImplicitRepresentation', False)

    
    lod4ImplicitRepresentation = property(__lod4ImplicitRepresentation.value, __lod4ImplicitRepresentation.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __class.name() : __class,
        __GenericApplicationPropertyOfBuildingFurniture.name() : __GenericApplicationPropertyOfBuildingFurniture,
        __function.name() : __function,
        __lod4Geometry.name() : __lod4Geometry,
        __lod4ImplicitRepresentation.name() : __lod4ImplicitRepresentation,
        __usage.name() : __usage
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingFurnitureType', BuildingFurnitureType)


# Complex type GroundSurfaceType with content type ELEMENT_ONLY
class GroundSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'GroundSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfGroundSurface uses Python identifier GenericApplicationPropertyOfGroundSurface
    __GenericApplicationPropertyOfGroundSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'), 'GenericApplicationPropertyOfGroundSurface', '__httpwww_opengis_netcitygmlbuilding1_0_GroundSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfGroundSurface', True)

    
    GenericApplicationPropertyOfGroundSurface = property(__GenericApplicationPropertyOfGroundSurface.value, __GenericApplicationPropertyOfGroundSurface.set, None, None)

    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfGroundSurface.name() : __GenericApplicationPropertyOfGroundSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'GroundSurfaceType', GroundSurfaceType)


# Complex type InteriorRoomPropertyType with content type ELEMENT_ONLY
class InteriorRoomPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InteriorRoomPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}Room uses Python identifier Room
    __Room = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Room'), 'Room', '__httpwww_opengis_netcitygmlbuilding1_0_InteriorRoomPropertyType_httpwww_opengis_netcitygmlbuilding1_0Room', False)

    
    Room = property(__Room.value, __Room.set, None, None)

    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __Room.name() : __Room
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'InteriorRoomPropertyType', InteriorRoomPropertyType)


# Complex type FloorSurfaceType with content type ELEMENT_ONLY
class FloorSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FloorSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfFloorSurface uses Python identifier GenericApplicationPropertyOfFloorSurface
    __GenericApplicationPropertyOfFloorSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'), 'GenericApplicationPropertyOfFloorSurface', '__httpwww_opengis_netcitygmlbuilding1_0_FloorSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfFloorSurface', True)

    
    GenericApplicationPropertyOfFloorSurface = property(__GenericApplicationPropertyOfFloorSurface.value, __GenericApplicationPropertyOfFloorSurface.set, None, None)

    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfFloorSurface.name() : __GenericApplicationPropertyOfFloorSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'FloorSurfaceType', FloorSurfaceType)


# Complex type BoundarySurfacePropertyType with content type ELEMENT_ONLY
class BoundarySurfacePropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BoundarySurfacePropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_BoundarySurface uses Python identifier BoundarySurface
    __BoundarySurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_BoundarySurface'), 'BoundarySurface', '__httpwww_opengis_netcitygmlbuilding1_0_BoundarySurfacePropertyType_httpwww_opengis_netcitygmlbuilding1_0_BoundarySurface', False)

    
    BoundarySurface = property(__BoundarySurface.value, __BoundarySurface.set, None, None)

    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __BoundarySurface.name() : __BoundarySurface
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BoundarySurfacePropertyType', BoundarySurfacePropertyType)


# Complex type OpeningPropertyType with content type ELEMENT_ONLY
class OpeningPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'OpeningPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_Opening uses Python identifier Opening
    __Opening = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_Opening'), 'Opening', '__httpwww_opengis_netcitygmlbuilding1_0_OpeningPropertyType_httpwww_opengis_netcitygmlbuilding1_0_Opening', False)

    
    Opening = property(__Opening.value, __Opening.set, None, None)

    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __Opening.name() : __Opening
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'OpeningPropertyType', OpeningPropertyType)


# Complex type AbstractOpeningType with content type ELEMENT_ONLY
class AbstractOpeningType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractOpeningType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractOpeningType_httpwww_opengis_netcitygmlbuilding1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractOpeningType_httpwww_opengis_netcitygmlbuilding1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfOpening uses Python identifier GenericApplicationPropertyOfOpening
    __GenericApplicationPropertyOfOpening = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'), 'GenericApplicationPropertyOfOpening', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractOpeningType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfOpening', True)

    
    GenericApplicationPropertyOfOpening = property(__GenericApplicationPropertyOfOpening.value, __GenericApplicationPropertyOfOpening.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod3MultiSurface.name() : __lod3MultiSurface,
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __GenericApplicationPropertyOfOpening.name() : __GenericApplicationPropertyOfOpening
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractOpeningType', AbstractOpeningType)


# Complex type BuildingInstallationPropertyType with content type ELEMENT_ONLY
class BuildingInstallationPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallationPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}BuildingInstallation uses Python identifier BuildingInstallation
    __BuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallation'), 'BuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationPropertyType_httpwww_opengis_netcitygmlbuilding1_0BuildingInstallation', False)

    
    BuildingInstallation = property(__BuildingInstallation.value, __BuildingInstallation.set, None, None)

    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __BuildingInstallation.name() : __BuildingInstallation
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingInstallationPropertyType', BuildingInstallationPropertyType)


# Complex type DoorType with content type ELEMENT_ONLY
class DoorType (AbstractOpeningType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DoorType')
    # Base type is AbstractOpeningType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}address uses Python identifier address
    __address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'address'), 'address', '__httpwww_opengis_netcitygmlbuilding1_0_DoorType_httpwww_opengis_netcitygmlbuilding1_0address', True)

    
    address = property(__address.value, __address.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfDoor uses Python identifier GenericApplicationPropertyOfDoor
    __GenericApplicationPropertyOfDoor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'), 'GenericApplicationPropertyOfDoor', '__httpwww_opengis_netcitygmlbuilding1_0_DoorType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfDoor', True)

    
    GenericApplicationPropertyOfDoor = property(__GenericApplicationPropertyOfDoor.value, __GenericApplicationPropertyOfDoor.set, None, None)

    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfOpening ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfOpening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractOpeningType._ElementMap.copy()
    _ElementMap.update({
        __address.name() : __address,
        __GenericApplicationPropertyOfDoor.name() : __GenericApplicationPropertyOfDoor
    })
    _AttributeMap = AbstractOpeningType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'DoorType', DoorType)


# Complex type IntBuildingInstallationPropertyType with content type ELEMENT_ONLY
class IntBuildingInstallationPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallationPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}IntBuildingInstallation uses Python identifier IntBuildingInstallation
    __IntBuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallation'), 'IntBuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationPropertyType_httpwww_opengis_netcitygmlbuilding1_0IntBuildingInstallation', False)

    
    IntBuildingInstallation = property(__IntBuildingInstallation.value, __IntBuildingInstallation.set, None, None)

    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __IntBuildingInstallation.name() : __IntBuildingInstallation
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'IntBuildingInstallationPropertyType', IntBuildingInstallationPropertyType)


# Complex type WindowType with content type ELEMENT_ONLY
class WindowType (AbstractOpeningType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WindowType')
    # Base type is AbstractOpeningType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfWindow uses Python identifier GenericApplicationPropertyOfWindow
    __GenericApplicationPropertyOfWindow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'), 'GenericApplicationPropertyOfWindow', '__httpwww_opengis_netcitygmlbuilding1_0_WindowType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfWindow', True)

    
    GenericApplicationPropertyOfWindow = property(__GenericApplicationPropertyOfWindow.value, __GenericApplicationPropertyOfWindow.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfOpening ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfOpening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractOpeningType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfWindow.name() : __GenericApplicationPropertyOfWindow
    })
    _AttributeMap = AbstractOpeningType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'WindowType', WindowType)


# Complex type ClosureSurfaceType with content type ELEMENT_ONLY
class ClosureSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ClosureSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfClosureSurface uses Python identifier GenericApplicationPropertyOfClosureSurface
    __GenericApplicationPropertyOfClosureSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'), 'GenericApplicationPropertyOfClosureSurface', '__httpwww_opengis_netcitygmlbuilding1_0_ClosureSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfClosureSurface', True)

    
    GenericApplicationPropertyOfClosureSurface = property(__GenericApplicationPropertyOfClosureSurface.value, __GenericApplicationPropertyOfClosureSurface.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfClosureSurface.name() : __GenericApplicationPropertyOfClosureSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ClosureSurfaceType', ClosureSurfaceType)


# Complex type WallSurfaceType with content type ELEMENT_ONLY
class WallSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WallSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfWallSurface uses Python identifier GenericApplicationPropertyOfWallSurface
    __GenericApplicationPropertyOfWallSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'), 'GenericApplicationPropertyOfWallSurface', '__httpwww_opengis_netcitygmlbuilding1_0_WallSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfWallSurface', True)

    
    GenericApplicationPropertyOfWallSurface = property(__GenericApplicationPropertyOfWallSurface.value, __GenericApplicationPropertyOfWallSurface.set, None, None)

    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfWallSurface.name() : __GenericApplicationPropertyOfWallSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'WallSurfaceType', WallSurfaceType)


# Complex type InteriorWallSurfaceType with content type ELEMENT_ONLY
class InteriorWallSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InteriorWallSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfInteriorWallSurface uses Python identifier GenericApplicationPropertyOfInteriorWallSurface
    __GenericApplicationPropertyOfInteriorWallSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'), 'GenericApplicationPropertyOfInteriorWallSurface', '__httpwww_opengis_netcitygmlbuilding1_0_InteriorWallSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfInteriorWallSurface', True)

    
    GenericApplicationPropertyOfInteriorWallSurface = property(__GenericApplicationPropertyOfInteriorWallSurface.value, __GenericApplicationPropertyOfInteriorWallSurface.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfInteriorWallSurface.name() : __GenericApplicationPropertyOfInteriorWallSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'InteriorWallSurfaceType', InteriorWallSurfaceType)


# Complex type BuildingType with content type ELEMENT_ONLY
class BuildingType (AbstractBuildingType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingType')
    # Base type is AbstractBuildingType
    
    # Element interiorBuildingInstallation ({http://www.opengis.net/citygml/building/1.0}interiorBuildingInstallation) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3Solid ({http://www.opengis.net/citygml/building/1.0}lod3Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element yearOfDemolition ({http://www.opengis.net/citygml/building/1.0}yearOfDemolition) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod3TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod3TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4Solid ({http://www.opengis.net/citygml/building/1.0}lod4Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfSite ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfSite) inherited from {http://www.opengis.net/citygml/1.0}AbstractSiteType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod4MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod4TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element interiorRoom ({http://www.opengis.net/citygml/building/1.0}interiorRoom) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element consistsOfBuildingPart ({http://www.opengis.net/citygml/building/1.0}consistsOfBuildingPart) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element class_ ({http://www.opengis.net/citygml/building/1.0}class) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element address ({http://www.opengis.net/citygml/building/1.0}address) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element function ({http://www.opengis.net/citygml/building/1.0}function) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element usage ({http://www.opengis.net/citygml/building/1.0}usage) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element yearOfConstruction ({http://www.opengis.net/citygml/building/1.0}yearOfConstruction) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element measuredHeight ({http://www.opengis.net/citygml/building/1.0}measuredHeight) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeysAboveGround ({http://www.opengis.net/citygml/building/1.0}storeysAboveGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element storeysBelowGround ({http://www.opengis.net/citygml/building/1.0}storeysBelowGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element storeyHeightsBelowGround ({http://www.opengis.net/citygml/building/1.0}storeyHeightsBelowGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBuilding uses Python identifier GenericApplicationPropertyOfBuilding
    __GenericApplicationPropertyOfBuilding = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'), 'GenericApplicationPropertyOfBuilding', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfBuilding', True)

    
    GenericApplicationPropertyOfBuilding = property(__GenericApplicationPropertyOfBuilding.value, __GenericApplicationPropertyOfBuilding.set, None, None)

    
    # Element lod1Solid ({http://www.opengis.net/citygml/building/1.0}lod1Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element boundedBy_ ({http://www.opengis.net/citygml/building/1.0}boundedBy) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod1MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod1MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element roofType ({http://www.opengis.net/citygml/building/1.0}roofType) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod1TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod1TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod3MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod3MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeyHeightsAboveGround ({http://www.opengis.net/citygml/building/1.0}storeyHeightsAboveGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2Solid ({http://www.opengis.net/citygml/building/1.0}lod2Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfAbstractBuilding ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfAbstractBuilding) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod2MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod2TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element outerBuildingInstallation ({http://www.opengis.net/citygml/building/1.0}outerBuildingInstallation) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBuildingType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfBuilding.name() : __GenericApplicationPropertyOfBuilding
    })
    _AttributeMap = AbstractBuildingType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingType', BuildingType)


# Complex type CeilingSurfaceType with content type ELEMENT_ONLY
class CeilingSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CeilingSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfCeilingSurface uses Python identifier GenericApplicationPropertyOfCeilingSurface
    __GenericApplicationPropertyOfCeilingSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'), 'GenericApplicationPropertyOfCeilingSurface', '__httpwww_opengis_netcitygmlbuilding1_0_CeilingSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfCeilingSurface', True)

    
    GenericApplicationPropertyOfCeilingSurface = property(__GenericApplicationPropertyOfCeilingSurface.value, __GenericApplicationPropertyOfCeilingSurface.set, None, None)

    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfCeilingSurface.name() : __GenericApplicationPropertyOfCeilingSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'CeilingSurfaceType', CeilingSurfaceType)


# Complex type BuildingPartPropertyType with content type ELEMENT_ONLY
class BuildingPartPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingPartPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}BuildingPart uses Python identifier BuildingPart
    __BuildingPart = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingPart'), 'BuildingPart', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingPartPropertyType_httpwww_opengis_netcitygmlbuilding1_0BuildingPart', False)

    
    BuildingPart = property(__BuildingPart.value, __BuildingPart.set, None, None)

    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __BuildingPart.name() : __BuildingPart
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingPartPropertyType', BuildingPartPropertyType)


GenericApplicationPropertyOfGroundSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfGroundSurface.name().localName(), GenericApplicationPropertyOfGroundSurface)

GenericApplicationPropertyOfAbstractBuilding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfAbstractBuilding.name().localName(), GenericApplicationPropertyOfAbstractBuilding)

IntBuildingInstallation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallation'), IntBuildingInstallationType)
Namespace.addCategoryObject('elementBinding', IntBuildingInstallation.name().localName(), IntBuildingInstallation)

RoofSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RoofSurface'), RoofSurfaceType)
Namespace.addCategoryObject('elementBinding', RoofSurface.name().localName(), RoofSurface)

GenericApplicationPropertyOfBuildingPart = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBuildingPart.name().localName(), GenericApplicationPropertyOfBuildingPart)

BuildingFurniture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingFurniture'), BuildingFurnitureType)
Namespace.addCategoryObject('elementBinding', BuildingFurniture.name().localName(), BuildingFurniture)

GenericApplicationPropertyOfOpening = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfOpening.name().localName(), GenericApplicationPropertyOfOpening)

GenericApplicationPropertyOfRoofSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfRoofSurface.name().localName(), GenericApplicationPropertyOfRoofSurface)

GenericApplicationPropertyOfBuildingInstallation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBuildingInstallation.name().localName(), GenericApplicationPropertyOfBuildingInstallation)

GenericApplicationPropertyOfDoor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfDoor.name().localName(), GenericApplicationPropertyOfDoor)

GroundSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GroundSurface'), GroundSurfaceType)
Namespace.addCategoryObject('elementBinding', GroundSurface.name().localName(), GroundSurface)

FloorSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FloorSurface'), FloorSurfaceType)
Namespace.addCategoryObject('elementBinding', FloorSurface.name().localName(), FloorSurface)

GenericApplicationPropertyOfCeilingSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfCeilingSurface.name().localName(), GenericApplicationPropertyOfCeilingSurface)

BuildingPart = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingPart'), BuildingPartType)
Namespace.addCategoryObject('elementBinding', BuildingPart.name().localName(), BuildingPart)

GenericApplicationPropertyOfFloorSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfFloorSurface.name().localName(), GenericApplicationPropertyOfFloorSurface)

Opening = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Opening'), AbstractOpeningType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', Opening.name().localName(), Opening)

GenericApplicationPropertyOfBoundarySurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBoundarySurface.name().localName(), GenericApplicationPropertyOfBoundarySurface)

GenericApplicationPropertyOfWindow = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfWindow.name().localName(), GenericApplicationPropertyOfWindow)

GenericApplicationPropertyOfWallSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfWallSurface.name().localName(), GenericApplicationPropertyOfWallSurface)

Door = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Door'), DoorType)
Namespace.addCategoryObject('elementBinding', Door.name().localName(), Door)

GenericApplicationPropertyOfClosureSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfClosureSurface.name().localName(), GenericApplicationPropertyOfClosureSurface)

AbstractBuilding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_AbstractBuilding'), AbstractBuildingType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractBuilding.name().localName(), AbstractBuilding)

GenericApplicationPropertyOfInteriorWallSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfInteriorWallSurface.name().localName(), GenericApplicationPropertyOfInteriorWallSurface)

GenericApplicationPropertyOfRoom = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfRoom.name().localName(), GenericApplicationPropertyOfRoom)

GenericApplicationPropertyOfBuilding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBuilding.name().localName(), GenericApplicationPropertyOfBuilding)

BoundarySurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_BoundarySurface'), AbstractBoundarySurfaceType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', BoundarySurface.name().localName(), BoundarySurface)

Window = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Window'), WindowType)
Namespace.addCategoryObject('elementBinding', Window.name().localName(), Window)

BuildingInstallation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallation'), BuildingInstallationType)
Namespace.addCategoryObject('elementBinding', BuildingInstallation.name().localName(), BuildingInstallation)

ClosureSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ClosureSurface'), ClosureSurfaceType)
Namespace.addCategoryObject('elementBinding', ClosureSurface.name().localName(), ClosureSurface)

WallSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WallSurface'), WallSurfaceType)
Namespace.addCategoryObject('elementBinding', WallSurface.name().localName(), WallSurface)

InteriorWallSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InteriorWallSurface'), InteriorWallSurfaceType)
Namespace.addCategoryObject('elementBinding', InteriorWallSurface.name().localName(), InteriorWallSurface)

GenericApplicationPropertyOfIntBuildingInstallation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfIntBuildingInstallation.name().localName(), GenericApplicationPropertyOfIntBuildingInstallation)

Room = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Room'), RoomType)
Namespace.addCategoryObject('elementBinding', Room.name().localName(), Room)

Building = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Building'), BuildingType)
Namespace.addCategoryObject('elementBinding', Building.name().localName(), Building)

CeilingSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CeilingSurface'), CeilingSurfaceType)
Namespace.addCategoryObject('elementBinding', CeilingSurface.name().localName(), CeilingSurface)

GenericApplicationPropertyOfBuildingFurniture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBuildingFurniture.name().localName(), GenericApplicationPropertyOfBuildingFurniture)



RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'), InteriorFurniturePropertyType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'), IntBuildingInstallationPropertyType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), RoomClassType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), RoomFunctionType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), RoomUsageType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'), BoundarySurfacePropertyType, scope=RoomType))
RoomType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
    ])
})



InteriorFurniturePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingFurniture'), BuildingFurnitureType, scope=InteriorFurniturePropertyType))
InteriorFurniturePropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=InteriorFurniturePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingFurniture'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



IntBuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=IntBuildingInstallationType))

IntBuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), IntBuildingInstallationClassType, scope=IntBuildingInstallationType))

IntBuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=IntBuildingInstallationType))

IntBuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), IntBuildingInstallationFunctionType, scope=IntBuildingInstallationType))

IntBuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), IntBuildingInstallationUsageType, scope=IntBuildingInstallationType))
IntBuildingInstallationType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'))),
    ])
})



AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'), IntBuildingInstallationPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'), BoundarySurfacePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'), pyxb.binding.datatypes.gYear, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'), InteriorRoomPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'), BuildingPartPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), BuildingClassType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), pyxb.bundles.opengis.citygml.base.AddressPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), BuildingFunctionType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), BuildingUsageType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'), pyxb.binding.datatypes.gYear, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'), pyxb.bundles.opengis.gml.LengthType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'), pyxb.binding.datatypes.nonNegativeInteger, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'), pyxb.binding.datatypes.nonNegativeInteger, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'), pyxb.bundles.opengis.gml.MeasureOrNullListType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'roofType'), RoofTypeType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'), pyxb.bundles.opengis.gml.MeasureOrNullListType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'), BuildingInstallationPropertyType, scope=AbstractBuildingType))
AbstractBuildingType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 16 : pyxb.binding.content.ContentModelState(state=16, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 17 : pyxb.binding.content.ContentModelState(state=17, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 18 : pyxb.binding.content.ContentModelState(state=18, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 19 : pyxb.binding.content.ContentModelState(state=19, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 20 : pyxb.binding.content.ContentModelState(state=20, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 21 : pyxb.binding.content.ContentModelState(state=21, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
    ])
    , 22 : pyxb.binding.content.ContentModelState(state=22, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
    ])
    , 23 : pyxb.binding.content.ContentModelState(state=23, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
    ])
    , 24 : pyxb.binding.content.ContentModelState(state=24, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 25 : pyxb.binding.content.ContentModelState(state=25, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 26 : pyxb.binding.content.ContentModelState(state=26, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 27 : pyxb.binding.content.ContentModelState(state=27, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
    ])
    , 28 : pyxb.binding.content.ContentModelState(state=28, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 29 : pyxb.binding.content.ContentModelState(state=29, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 30 : pyxb.binding.content.ContentModelState(state=30, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 31 : pyxb.binding.content.ContentModelState(state=31, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
})



BuildingPartType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BuildingPartType))
BuildingPartType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 16 : pyxb.binding.content.ContentModelState(state=16, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 17 : pyxb.binding.content.ContentModelState(state=17, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 18 : pyxb.binding.content.ContentModelState(state=18, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 19 : pyxb.binding.content.ContentModelState(state=19, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 20 : pyxb.binding.content.ContentModelState(state=20, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 21 : pyxb.binding.content.ContentModelState(state=21, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
    ])
    , 22 : pyxb.binding.content.ContentModelState(state=22, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
    ])
    , 23 : pyxb.binding.content.ContentModelState(state=23, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 24 : pyxb.binding.content.ContentModelState(state=24, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 25 : pyxb.binding.content.ContentModelState(state=25, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 26 : pyxb.binding.content.ContentModelState(state=26, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 27 : pyxb.binding.content.ContentModelState(state=27, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
    ])
    , 28 : pyxb.binding.content.ContentModelState(state=28, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 29 : pyxb.binding.content.ContentModelState(state=29, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 30 : pyxb.binding.content.ContentModelState(state=30, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 31 : pyxb.binding.content.ContentModelState(state=31, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
    ])
    , 32 : pyxb.binding.content.ContentModelState(state=32, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
})



AbstractBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBoundarySurfaceType))

AbstractBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBoundarySurfaceType))

AbstractBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBoundarySurfaceType))

AbstractBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'opening'), OpeningPropertyType, scope=AbstractBoundarySurfaceType))

AbstractBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractBoundarySurfaceType))
AbstractBoundarySurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
})



RoofSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=RoofSurfaceType))
RoofSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
})



BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), BuildingInstallationUsageType, scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), BuildingInstallationClassType, scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), BuildingInstallationFunctionType, scope=BuildingInstallationType))
BuildingInstallationType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
})



BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), BuildingFurnitureClassType, scope=BuildingFurnitureType))

BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BuildingFurnitureType))

BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), BuildingFurnitureFunctionType, scope=BuildingFurnitureType))

BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=BuildingFurnitureType))

BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'), pyxb.bundles.opengis.citygml.base.ImplicitRepresentationPropertyType, scope=BuildingFurnitureType))

BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), BuildingFurnitureUsageType, scope=BuildingFurnitureType))
BuildingFurnitureType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
    ])
})



GroundSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=GroundSurfaceType))
GroundSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
})



InteriorRoomPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Room'), RoomType, scope=InteriorRoomPropertyType))
InteriorRoomPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=InteriorRoomPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Room'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



FloorSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=FloorSurfaceType))
FloorSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
})



BoundarySurfacePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_BoundarySurface'), AbstractBoundarySurfaceType, abstract=pyxb.binding.datatypes.boolean(1), scope=BoundarySurfacePropertyType))
BoundarySurfacePropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BoundarySurfacePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_BoundarySurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



OpeningPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Opening'), AbstractOpeningType, abstract=pyxb.binding.datatypes.boolean(1), scope=OpeningPropertyType))
OpeningPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=OpeningPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_Opening'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



AbstractOpeningType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractOpeningType))

AbstractOpeningType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractOpeningType))

AbstractOpeningType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractOpeningType))
AbstractOpeningType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
})



BuildingInstallationPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallation'), BuildingInstallationType, scope=BuildingInstallationPropertyType))
BuildingInstallationPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingInstallationPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



DoorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), pyxb.bundles.opengis.citygml.base.AddressPropertyType, scope=DoorType))

DoorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=DoorType))
DoorType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'))),
    ])
})



IntBuildingInstallationPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallation'), IntBuildingInstallationType, scope=IntBuildingInstallationPropertyType))
IntBuildingInstallationPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IntBuildingInstallationPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



WindowType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=WindowType))
WindowType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'))),
    ])
})



ClosureSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ClosureSurfaceType))
ClosureSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'))),
    ])
})



WallSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=WallSurfaceType))
WallSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
})



InteriorWallSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=InteriorWallSurfaceType))
InteriorWallSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
})



BuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BuildingType))
BuildingType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 16 : pyxb.binding.content.ContentModelState(state=16, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=24, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 17 : pyxb.binding.content.ContentModelState(state=17, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 18 : pyxb.binding.content.ContentModelState(state=18, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 19 : pyxb.binding.content.ContentModelState(state=19, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
    ])
    , 20 : pyxb.binding.content.ContentModelState(state=20, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 21 : pyxb.binding.content.ContentModelState(state=21, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 22 : pyxb.binding.content.ContentModelState(state=22, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
    ])
    , 23 : pyxb.binding.content.ContentModelState(state=23, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
    ])
    , 24 : pyxb.binding.content.ContentModelState(state=24, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function'))),
        pyxb.binding.content.ContentModelTransition(next_state=21, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=31, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 25 : pyxb.binding.content.ContentModelState(state=25, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 26 : pyxb.binding.content.ContentModelState(state=26, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 27 : pyxb.binding.content.ContentModelState(state=27, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
    ])
    , 28 : pyxb.binding.content.ContentModelState(state=28, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
    ])
    , 29 : pyxb.binding.content.ContentModelState(state=29, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 30 : pyxb.binding.content.ContentModelState(state=30, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 31 : pyxb.binding.content.ContentModelState(state=31, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=30, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType'))),
        pyxb.binding.content.ContentModelTransition(next_state=32, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
    , 32 : pyxb.binding.content.ContentModelState(state=32, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=28, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=26, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=23, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=22, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=29, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=25, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=27, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'))),
    ])
})



CeilingSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=CeilingSurfaceType))
CeilingSurfaceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening'))),
    ])
})



BuildingPartPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingPart'), BuildingPartType, scope=BuildingPartPropertyType))
BuildingPartPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BuildingPartPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingPart'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})

IntBuildingInstallation._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

RoofSurface._setSubstitutionGroup(BoundarySurface)

BuildingFurniture._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

GroundSurface._setSubstitutionGroup(BoundarySurface)

FloorSurface._setSubstitutionGroup(BoundarySurface)

BuildingPart._setSubstitutionGroup(AbstractBuilding)

Opening._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

Door._setSubstitutionGroup(Opening)

AbstractBuilding._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.Site)

BoundarySurface._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

Window._setSubstitutionGroup(Opening)

BuildingInstallation._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

ClosureSurface._setSubstitutionGroup(BoundarySurface)

WallSurface._setSubstitutionGroup(BoundarySurface)

InteriorWallSurface._setSubstitutionGroup(BoundarySurface)

Room._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

Building._setSubstitutionGroup(AbstractBuilding)

CeilingSurface._setSubstitutionGroup(BoundarySurface)
