# ./pyxb/bundles/opengis/citygml/raw/base.py
# PyXB bindings for NamespaceModule
# NSM:258153f9602467400b4189ab02b751cb737afb6c
# Generated 2009-11-30 18:10:16.792989 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:e635e76c-de0d-11de-8b37-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.gml
import pyxb.bundles.opengis.misc.xlinks
import pyxb.bundles.opengis.misc.xAL

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0', create_if_missing=True)
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
class MimeTypeType (pyxb.binding.datatypes.string):

    """MIME type of a geometry in an external library file. MIME types are defined by the IETF (Internet
                Engineering Task Force). The values of this type are defined in the XML file MimeTypeType.xml, according to the
                dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MimeTypeType')
    _Documentation = u'MIME type of a geometry in an external library file. MIME types are defined by the IETF (Internet\n                Engineering Task Force). The values of this type are defined in the XML file MimeTypeType.xml, according to the\n                dictionary concept of GML3. '
MimeTypeType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'MimeTypeType', MimeTypeType)

# Atomic SimpleTypeDefinition
class doubleBetween0and1 (pyxb.binding.datatypes.double):

    """Type for values, which are greater or equal than 0 and less or equal than 1. Used for color
                encoding, for example. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'doubleBetween0and1')
    _Documentation = u'Type for values, which are greater or equal than 0 and less or equal than 1. Used for color\n                encoding, for example. '
doubleBetween0and1._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=doubleBetween0and1, value=pyxb.binding.datatypes.double(0.0))
doubleBetween0and1._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=doubleBetween0and1, value=pyxb.binding.datatypes.double(1.0))
doubleBetween0and1._InitializeFacetMap(doubleBetween0and1._CF_minInclusive,
   doubleBetween0and1._CF_maxInclusive)
Namespace.addCategoryObject('typeBinding', u'doubleBetween0and1', doubleBetween0and1)

# List SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class doubleBetween0and1List (pyxb.binding.basis.STD_list):

    """List for double values, which are greater or equal than 0 and less or equal than 1. Used for color
                encoding, for example. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'doubleBetween0and1List')
    _Documentation = u'List for double values, which are greater or equal than 0 and less or equal than 1. Used for color\n                encoding, for example. '

    _ItemType = doubleBetween0and1
doubleBetween0and1List._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'doubleBetween0and1List', doubleBetween0and1List)

# List SimpleTypeDefinition
# superclasses pyxb.bundles.opengis.gml.doubleList
class TransformationMatrix2x2Type (pyxb.binding.basis.STD_list):

    """Used for georeferencing. The Transformation matrix is a 2 by 2 matrix, thus it must be a list with 4
                items. The order the matrix element are represented is row-major, i. e. the first 2 elements represent the first
                row, the fifth to the eight element the second row,... """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransformationMatrix2x2Type')
    _Documentation = u'Used for georeferencing. The Transformation matrix is a 2 by 2 matrix, thus it must be a list with 4\n                items. The order the matrix element are represented is row-major, i. e. the first 2 elements represent the first\n                row, the fifth to the eight element the second row,... '

    _ItemType = pyxb.binding.datatypes.double
TransformationMatrix2x2Type._CF_length = pyxb.binding.facets.CF_length(value=pyxb.binding.datatypes.nonNegativeInteger(4L))
TransformationMatrix2x2Type._InitializeFacetMap(TransformationMatrix2x2Type._CF_length)
Namespace.addCategoryObject('typeBinding', u'TransformationMatrix2x2Type', TransformationMatrix2x2Type)

# Atomic SimpleTypeDefinition
class integerBetween0and4 (pyxb.binding.datatypes.integer):

    """Type for integer values, which are greater or equal than 0 and less or equal than 4. Used for
                encoding of the LOD number. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'integerBetween0and4')
    _Documentation = u'Type for integer values, which are greater or equal than 0 and less or equal than 4. Used for\n                encoding of the LOD number. '
integerBetween0and4._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=integerBetween0and4, value=pyxb.binding.datatypes.integer(0L))
integerBetween0and4._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=integerBetween0and4, value=pyxb.binding.datatypes.integer(4L))
integerBetween0and4._InitializeFacetMap(integerBetween0and4._CF_minInclusive,
   integerBetween0and4._CF_maxInclusive)
Namespace.addCategoryObject('typeBinding', u'integerBetween0and4', integerBetween0and4)

# List SimpleTypeDefinition
# superclasses pyxb.bundles.opengis.gml.doubleList
class TransformationMatrix3x4Type (pyxb.binding.basis.STD_list):

    """Used for texture parameterization. The Transformation matrix is a 3 by 4 matrix, thus it must be a
                list with 12 items. The order the matrix element are represented is row-major, i. e. the first 4 elements
                represent the first row, the fifth to the eight element the second row,... """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransformationMatrix3x4Type')
    _Documentation = u'Used for texture parameterization. The Transformation matrix is a 3 by 4 matrix, thus it must be a\n                list with 12 items. The order the matrix element are represented is row-major, i. e. the first 4 elements\n                represent the first row, the fifth to the eight element the second row,... '

    _ItemType = pyxb.binding.datatypes.double
TransformationMatrix3x4Type._CF_length = pyxb.binding.facets.CF_length(value=pyxb.binding.datatypes.nonNegativeInteger(12L))
TransformationMatrix3x4Type._InitializeFacetMap(TransformationMatrix3x4Type._CF_length)
Namespace.addCategoryObject('typeBinding', u'TransformationMatrix3x4Type', TransformationMatrix3x4Type)

# List SimpleTypeDefinition
# superclasses pyxb.bundles.opengis.gml.doubleList
class TransformationMatrix4x4Type (pyxb.binding.basis.STD_list):

    """Used for implicit geometries. The Transformation matrix is a 4 by 4 matrix, thus it must be a list
                with 16 items. The order the matrix element are represented is row-major, i. e. the first 4 elements represent the
                first row, the fifth to the eight element the second row,... """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransformationMatrix4x4Type')
    _Documentation = u'Used for implicit geometries. The Transformation matrix is a 4 by 4 matrix, thus it must be a list\n                with 16 items. The order the matrix element are represented is row-major, i. e. the first 4 elements represent the\n                first row, the fifth to the eight element the second row,... '

    _ItemType = pyxb.binding.datatypes.double
TransformationMatrix4x4Type._CF_length = pyxb.binding.facets.CF_length(value=pyxb.binding.datatypes.nonNegativeInteger(16L))
TransformationMatrix4x4Type._InitializeFacetMap(TransformationMatrix4x4Type._CF_length)
Namespace.addCategoryObject('typeBinding', u'TransformationMatrix4x4Type', TransformationMatrix4x4Type)

# Complex type GeneralizationRelationType with content type ELEMENT_ONLY
class GeneralizationRelationType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'GeneralizationRelationType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/citygml/1.0}_CityObject uses Python identifier CityObject
    __CityObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_CityObject'), 'CityObject', '__httpwww_opengis_netcitygml1_0_GeneralizationRelationType_httpwww_opengis_netcitygml1_0_CityObject', False)

    
    CityObject = property(__CityObject.value, __CityObject.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netcitygml1_0_GeneralizationRelationType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netcitygml1_0_GeneralizationRelationType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netcitygml1_0_GeneralizationRelationType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netcitygml1_0_GeneralizationRelationType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netcitygml1_0_GeneralizationRelationType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netcitygml1_0_GeneralizationRelationType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netcitygml1_0_GeneralizationRelationType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netcitygml1_0_GeneralizationRelationType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")


    _ElementMap = {
        __CityObject.name() : __CityObject
    }
    _AttributeMap = {
        __type.name() : __type,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __remoteSchema.name() : __remoteSchema,
        __href.name() : __href,
        __role.name() : __role,
        __actuate.name() : __actuate
    }
Namespace.addCategoryObject('typeBinding', u'GeneralizationRelationType', GeneralizationRelationType)


# Complex type AddressType with content type ELEMENT_ONLY
class AddressType (pyxb.bundles.opengis.gml.AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AddressType')
    # Base type is pyxb.bundles.opengis.gml.AbstractFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/1.0}multiPoint uses Python identifier multiPoint
    __multiPoint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'multiPoint'), 'multiPoint', '__httpwww_opengis_netcitygml1_0_AddressType_httpwww_opengis_netcitygml1_0multiPoint', False)

    
    multiPoint = property(__multiPoint.value, __multiPoint.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfAddress uses Python identifier GenericApplicationPropertyOfAddress
    __GenericApplicationPropertyOfAddress = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAddress'), 'GenericApplicationPropertyOfAddress', '__httpwww_opengis_netcitygml1_0_AddressType_httpwww_opengis_netcitygml1_0_GenericApplicationPropertyOfAddress', True)

    
    GenericApplicationPropertyOfAddress = property(__GenericApplicationPropertyOfAddress.value, __GenericApplicationPropertyOfAddress.set, None, None)

    
    # Element {http://www.opengis.net/citygml/1.0}xalAddress uses Python identifier xalAddress
    __xalAddress = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'xalAddress'), 'xalAddress', '__httpwww_opengis_netcitygml1_0_AddressType_httpwww_opengis_netcitygml1_0xalAddress', False)

    
    xalAddress = property(__xalAddress.value, __xalAddress.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        __multiPoint.name() : __multiPoint,
        __GenericApplicationPropertyOfAddress.name() : __GenericApplicationPropertyOfAddress,
        __xalAddress.name() : __xalAddress
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AddressType', AddressType)


# Complex type CityModelType with content type ELEMENT_ONLY
class CityModelType (pyxb.bundles.opengis.gml.AbstractFeatureCollectionType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CityModelType')
    # Base type is pyxb.bundles.opengis.gml.AbstractFeatureCollectionType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element featureMembers ({http://www.opengis.net/gml}featureMembers) inherited from {http://www.opengis.net/gml}AbstractFeatureCollectionType
    
    # Element featureMember ({http://www.opengis.net/gml}featureMember) inherited from {http://www.opengis.net/gml}AbstractFeatureCollectionType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityModel uses Python identifier GenericApplicationPropertyOfCityModel
    __GenericApplicationPropertyOfCityModel = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityModel'), 'GenericApplicationPropertyOfCityModel', '__httpwww_opengis_netcitygml1_0_CityModelType_httpwww_opengis_netcitygml1_0_GenericApplicationPropertyOfCityModel', True)

    
    GenericApplicationPropertyOfCityModel = property(__GenericApplicationPropertyOfCityModel.value, __GenericApplicationPropertyOfCityModel.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractFeatureCollectionType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfCityModel.name() : __GenericApplicationPropertyOfCityModel
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractFeatureCollectionType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'CityModelType', CityModelType)


# Complex type AbstractCityObjectType with content type ELEMENT_ONLY
class AbstractCityObjectType (pyxb.bundles.opengis.gml.AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractCityObjectType')
    # Base type is pyxb.bundles.opengis.gml.AbstractFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/1.0}creationDate uses Python identifier creationDate
    __creationDate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'creationDate'), 'creationDate', '__httpwww_opengis_netcitygml1_0_AbstractCityObjectType_httpwww_opengis_netcitygml1_0creationDate', False)

    
    creationDate = property(__creationDate.value, __creationDate.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/1.0}terminationDate uses Python identifier terminationDate
    __terminationDate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'), 'terminationDate', '__httpwww_opengis_netcitygml1_0_AbstractCityObjectType_httpwww_opengis_netcitygml1_0terminationDate', False)

    
    terminationDate = property(__terminationDate.value, __terminationDate.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/1.0}externalReference uses Python identifier externalReference
    __externalReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'externalReference'), 'externalReference', '__httpwww_opengis_netcitygml1_0_AbstractCityObjectType_httpwww_opengis_netcitygml1_0externalReference', True)

    
    externalReference = property(__externalReference.value, __externalReference.set, None, None)

    
    # Element {http://www.opengis.net/citygml/1.0}generalizesTo uses Python identifier generalizesTo
    __generalizesTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'), 'generalizesTo', '__httpwww_opengis_netcitygml1_0_AbstractCityObjectType_httpwww_opengis_netcitygml1_0generalizesTo', True)

    
    generalizesTo = property(__generalizesTo.value, __generalizesTo.set, None, None)

    
    # Element {http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject uses Python identifier GenericApplicationPropertyOfCityObject
    __GenericApplicationPropertyOfCityObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'), 'GenericApplicationPropertyOfCityObject', '__httpwww_opengis_netcitygml1_0_AbstractCityObjectType_httpwww_opengis_netcitygml1_0_GenericApplicationPropertyOfCityObject', True)

    
    GenericApplicationPropertyOfCityObject = property(__GenericApplicationPropertyOfCityObject.value, __GenericApplicationPropertyOfCityObject.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        __creationDate.name() : __creationDate,
        __terminationDate.name() : __terminationDate,
        __externalReference.name() : __externalReference,
        __generalizesTo.name() : __generalizesTo,
        __GenericApplicationPropertyOfCityObject.name() : __GenericApplicationPropertyOfCityObject
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractCityObjectType', AbstractCityObjectType)


# Complex type ImplicitGeometryType with content type ELEMENT_ONLY
class ImplicitGeometryType (pyxb.bundles.opengis.gml.AbstractGMLType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ImplicitGeometryType')
    # Base type is pyxb.bundles.opengis.gml.AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/1.0}mimeType uses Python identifier mimeType
    __mimeType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'mimeType'), 'mimeType', '__httpwww_opengis_netcitygml1_0_ImplicitGeometryType_httpwww_opengis_netcitygml1_0mimeType', False)

    
    mimeType = property(__mimeType.value, __mimeType.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/1.0}transformationMatrix uses Python identifier transformationMatrix
    __transformationMatrix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'transformationMatrix'), 'transformationMatrix', '__httpwww_opengis_netcitygml1_0_ImplicitGeometryType_httpwww_opengis_netcitygml1_0transformationMatrix', False)

    
    transformationMatrix = property(__transformationMatrix.value, __transformationMatrix.set, None, None)

    
    # Element {http://www.opengis.net/citygml/1.0}libraryObject uses Python identifier libraryObject
    __libraryObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'libraryObject'), 'libraryObject', '__httpwww_opengis_netcitygml1_0_ImplicitGeometryType_httpwww_opengis_netcitygml1_0libraryObject', False)

    
    libraryObject = property(__libraryObject.value, __libraryObject.set, None, None)

    
    # Element {http://www.opengis.net/citygml/1.0}relativeGMLGeometry uses Python identifier relativeGMLGeometry
    __relativeGMLGeometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'relativeGMLGeometry'), 'relativeGMLGeometry', '__httpwww_opengis_netcitygml1_0_ImplicitGeometryType_httpwww_opengis_netcitygml1_0relativeGMLGeometry', False)

    
    relativeGMLGeometry = property(__relativeGMLGeometry.value, __relativeGMLGeometry.set, None, None)

    
    # Element {http://www.opengis.net/citygml/1.0}referencePoint uses Python identifier referencePoint
    __referencePoint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'referencePoint'), 'referencePoint', '__httpwww_opengis_netcitygml1_0_ImplicitGeometryType_httpwww_opengis_netcitygml1_0referencePoint', False)

    
    referencePoint = property(__referencePoint.value, __referencePoint.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractGMLType._ElementMap.copy()
    _ElementMap.update({
        __mimeType.name() : __mimeType,
        __transformationMatrix.name() : __transformationMatrix,
        __libraryObject.name() : __libraryObject,
        __relativeGMLGeometry.name() : __relativeGMLGeometry,
        __referencePoint.name() : __referencePoint
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractGMLType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ImplicitGeometryType', ImplicitGeometryType)


# Complex type ImplicitRepresentationPropertyType with content type ELEMENT_ONLY
class ImplicitRepresentationPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ImplicitRepresentationPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/1.0}ImplicitGeometry uses Python identifier ImplicitGeometry
    __ImplicitGeometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ImplicitGeometry'), 'ImplicitGeometry', '__httpwww_opengis_netcitygml1_0_ImplicitRepresentationPropertyType_httpwww_opengis_netcitygml1_0ImplicitGeometry', False)

    
    ImplicitGeometry = property(__ImplicitGeometry.value, __ImplicitGeometry.set, None, None)

    
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
        __ImplicitGeometry.name() : __ImplicitGeometry
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ImplicitRepresentationPropertyType', ImplicitRepresentationPropertyType)


# Complex type AbstractSiteType with content type ELEMENT_ONLY
class AbstractSiteType (AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractSiteType')
    # Base type is AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfSite uses Python identifier GenericApplicationPropertyOfSite
    __GenericApplicationPropertyOfSite = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSite'), 'GenericApplicationPropertyOfSite', '__httpwww_opengis_netcitygml1_0_AbstractSiteType_httpwww_opengis_netcitygml1_0_GenericApplicationPropertyOfSite', True)

    
    GenericApplicationPropertyOfSite = property(__GenericApplicationPropertyOfSite.value, __GenericApplicationPropertyOfSite.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfSite.name() : __GenericApplicationPropertyOfSite
    })
    _AttributeMap = AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractSiteType', AbstractSiteType)


# Complex type xalAddressPropertyType with content type ELEMENT_ONLY
class xalAddressPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'xalAddressPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails uses Python identifier AddressDetails
    __AddressDetails = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails'), 'AddressDetails', '__httpwww_opengis_netcitygml1_0_xalAddressPropertyType_urnoasisnamestcciqxsdschemaxAL2_0AddressDetails', False)

    
    AddressDetails = property(__AddressDetails.value, __AddressDetails.set, None, u'This container defines the details of the address. Can define multiple addresses including tracking address history')


    _ElementMap = {
        __AddressDetails.name() : __AddressDetails
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'xalAddressPropertyType', xalAddressPropertyType)


# Complex type AddressPropertyType with content type ELEMENT_ONLY
class AddressPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AddressPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/1.0}Address uses Python identifier Address
    __Address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Address'), 'Address', '__httpwww_opengis_netcitygml1_0_AddressPropertyType_httpwww_opengis_netcitygml1_0Address', False)

    
    Address = property(__Address.value, __Address.set, None, None)

    
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
        __Address.name() : __Address
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AddressPropertyType', AddressPropertyType)


# Complex type ExternalReferenceType with content type ELEMENT_ONLY
class ExternalReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExternalReferenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/citygml/1.0}externalObject uses Python identifier externalObject
    __externalObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'externalObject'), 'externalObject', '__httpwww_opengis_netcitygml1_0_ExternalReferenceType_httpwww_opengis_netcitygml1_0externalObject', False)

    
    externalObject = property(__externalObject.value, __externalObject.set, None, None)

    
    # Element {http://www.opengis.net/citygml/1.0}informationSystem uses Python identifier informationSystem
    __informationSystem = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'informationSystem'), 'informationSystem', '__httpwww_opengis_netcitygml1_0_ExternalReferenceType_httpwww_opengis_netcitygml1_0informationSystem', False)

    
    informationSystem = property(__informationSystem.value, __informationSystem.set, None, None)


    _ElementMap = {
        __externalObject.name() : __externalObject,
        __informationSystem.name() : __informationSystem
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ExternalReferenceType', ExternalReferenceType)


# Complex type ExternalObjectReferenceType with content type ELEMENT_ONLY
class ExternalObjectReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExternalObjectReferenceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/citygml/1.0}name uses Python identifier name
    __name = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'name'), 'name', '__httpwww_opengis_netcitygml1_0_ExternalObjectReferenceType_httpwww_opengis_netcitygml1_0name', False)

    
    name = property(__name.value, __name.set, None, None)

    
    # Element {http://www.opengis.net/citygml/1.0}uri uses Python identifier uri
    __uri = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'uri'), 'uri', '__httpwww_opengis_netcitygml1_0_ExternalObjectReferenceType_httpwww_opengis_netcitygml1_0uri', False)

    
    uri = property(__uri.value, __uri.set, None, None)


    _ElementMap = {
        __name.name() : __name,
        __uri.name() : __uri
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ExternalObjectReferenceType', ExternalObjectReferenceType)


Address = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Address'), AddressType)
Namespace.addCategoryObject('elementBinding', Address.name().localName(), Address)

GenericApplicationPropertyOfAddress = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAddress'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfAddress.name().localName(), GenericApplicationPropertyOfAddress)

CityModel = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CityModel'), CityModelType)
Namespace.addCategoryObject('elementBinding', CityModel.name().localName(), CityModel)

cityObjectMember = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'cityObjectMember'), pyxb.bundles.opengis.gml.FeaturePropertyType)
Namespace.addCategoryObject('elementBinding', cityObjectMember.name().localName(), cityObjectMember)

GenericApplicationPropertyOfCityObject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfCityObject.name().localName(), GenericApplicationPropertyOfCityObject)

CityObject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_CityObject'), AbstractCityObjectType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', CityObject.name().localName(), CityObject)

ImplicitGeometry = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ImplicitGeometry'), ImplicitGeometryType)
Namespace.addCategoryObject('elementBinding', ImplicitGeometry.name().localName(), ImplicitGeometry)

Site = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Site'), AbstractSiteType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', Site.name().localName(), Site)

GenericApplicationPropertyOfSite = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSite'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfSite.name().localName(), GenericApplicationPropertyOfSite)

GenericApplicationPropertyOfCityModel = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityModel'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfCityModel.name().localName(), GenericApplicationPropertyOfCityModel)



GeneralizationRelationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_CityObject'), AbstractCityObjectType, abstract=pyxb.binding.datatypes.boolean(1), scope=GeneralizationRelationType))
GeneralizationRelationType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=GeneralizationRelationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_CityObject'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



AddressType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'multiPoint'), pyxb.bundles.opengis.gml.MultiPointPropertyType, scope=AddressType))

AddressType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAddress'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AddressType))

AddressType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'xalAddress'), xalAddressPropertyType, scope=AddressType))
AddressType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'xalAddress'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAddress'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'multiPoint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAddress'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'xalAddress'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'xalAddress'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'xalAddress'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AddressType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
})



CityModelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityModel'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=CityModelType))
CityModelType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'featureMembers'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'featureMember'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityModel'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'featureMembers'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'featureMember'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityModel'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityModel'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'featureMembers'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'featureMember'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityModel'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'featureMembers'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'featureMember'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CityModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityModel'))),
    ])
})



AbstractCityObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'creationDate'), pyxb.binding.datatypes.date, scope=AbstractCityObjectType))

AbstractCityObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'), pyxb.binding.datatypes.date, scope=AbstractCityObjectType))

AbstractCityObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'externalReference'), ExternalReferenceType, scope=AbstractCityObjectType))

AbstractCityObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'), GeneralizationRelationType, scope=AbstractCityObjectType))

AbstractCityObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractCityObjectType))
AbstractCityObjectType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'creationDate'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'creationDate'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'creationDate'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractCityObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'creationDate'))),
    ])
})



ImplicitGeometryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'mimeType'), MimeTypeType, scope=ImplicitGeometryType))

ImplicitGeometryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'transformationMatrix'), TransformationMatrix4x4Type, scope=ImplicitGeometryType))

ImplicitGeometryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'libraryObject'), pyxb.binding.datatypes.anyURI, scope=ImplicitGeometryType))

ImplicitGeometryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'relativeGMLGeometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=ImplicitGeometryType))

ImplicitGeometryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'referencePoint'), pyxb.bundles.opengis.gml.PointPropertyType, scope=ImplicitGeometryType))
ImplicitGeometryType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'transformationMatrix'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'libraryObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relativeGMLGeometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'referencePoint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mimeType'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'libraryObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'transformationMatrix'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relativeGMLGeometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'referencePoint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mimeType'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'referencePoint'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'libraryObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'referencePoint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relativeGMLGeometry'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'referencePoint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relativeGMLGeometry'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'transformationMatrix'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'libraryObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'relativeGMLGeometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ImplicitGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'referencePoint'))),
    ])
})



ImplicitRepresentationPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ImplicitGeometry'), ImplicitGeometryType, scope=ImplicitRepresentationPropertyType))
ImplicitRepresentationPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ImplicitRepresentationPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ImplicitGeometry'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



AbstractSiteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSite'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractSiteType))
AbstractSiteType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'creationDate'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'creationDate'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSite'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'creationDate'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminationDate'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSite'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'creationDate'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSite'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObject'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'generalizesTo'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractSiteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSite'))),
    ])
})



xalAddressPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails'), pyxb.bundles.opengis.misc.xAL.AddressDetails_, scope=xalAddressPropertyType, documentation=u'This container defines the details of the address. Can define multiple addresses including tracking address history'))
xalAddressPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=xalAddressPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



AddressPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Address'), AddressType, scope=AddressPropertyType))
AddressPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Address'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



ExternalReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'externalObject'), ExternalObjectReferenceType, scope=ExternalReferenceType))

ExternalReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'informationSystem'), pyxb.binding.datatypes.anyURI, scope=ExternalReferenceType))
ExternalReferenceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ExternalReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'informationSystem'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ExternalReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalObject'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ExternalReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'externalObject'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



ExternalObjectReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'name'), pyxb.binding.datatypes.string, scope=ExternalObjectReferenceType))

ExternalObjectReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'uri'), pyxb.binding.datatypes.anyURI, scope=ExternalObjectReferenceType))
ExternalObjectReferenceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ExternalObjectReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ExternalObjectReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'uri'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})

Address._setSubstitutionGroup(pyxb.bundles.opengis.gml.Feature)

CityModel._setSubstitutionGroup(pyxb.bundles.opengis.gml.FeatureCollection)

cityObjectMember._setSubstitutionGroup(pyxb.bundles.opengis.gml.featureMember)

CityObject._setSubstitutionGroup(pyxb.bundles.opengis.gml.Feature)

ImplicitGeometry._setSubstitutionGroup(pyxb.bundles.opengis.gml.GML)

Site._setSubstitutionGroup(CityObject)
