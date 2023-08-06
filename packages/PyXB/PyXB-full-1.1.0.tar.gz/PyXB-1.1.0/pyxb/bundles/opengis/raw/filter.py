# ./pyxb/bundles/opengis/raw/filter.py
# PyXB bindings for NamespaceModule
# NSM:5b31a14669a98cd6cc4f3673117954e87b7d869b
# Generated 2009-11-30 18:10:00.316910 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:dc6b2c38-de0d-11de-b41c-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
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
class SortOrderType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SortOrderType')
    _Documentation = None
SortOrderType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=SortOrderType, enum_prefix=None)
SortOrderType.DESC = SortOrderType._CF_enumeration.addEnumeration(unicode_value=u'DESC')
SortOrderType.ASC = SortOrderType._CF_enumeration.addEnumeration(unicode_value=u'ASC')
SortOrderType._InitializeFacetMap(SortOrderType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'SortOrderType', SortOrderType)

# Atomic SimpleTypeDefinition
class SpatialOperatorNameType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SpatialOperatorNameType')
    _Documentation = None
SpatialOperatorNameType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=SpatialOperatorNameType, enum_prefix=None)
SpatialOperatorNameType.BBOX = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'BBOX')
SpatialOperatorNameType.Equals = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'Equals')
SpatialOperatorNameType.Disjoint = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'Disjoint')
SpatialOperatorNameType.Intersects = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'Intersects')
SpatialOperatorNameType.Touches = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'Touches')
SpatialOperatorNameType.Crosses = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'Crosses')
SpatialOperatorNameType.Within = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'Within')
SpatialOperatorNameType.Contains = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'Contains')
SpatialOperatorNameType.Overlaps = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'Overlaps')
SpatialOperatorNameType.Beyond = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'Beyond')
SpatialOperatorNameType.DWithin = SpatialOperatorNameType._CF_enumeration.addEnumeration(unicode_value=u'DWithin')
SpatialOperatorNameType._InitializeFacetMap(SpatialOperatorNameType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'SpatialOperatorNameType', SpatialOperatorNameType)

# Atomic SimpleTypeDefinition
class ComparisonOperatorType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ComparisonOperatorType')
    _Documentation = None
ComparisonOperatorType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ComparisonOperatorType, enum_prefix=None)
ComparisonOperatorType.LessThan = ComparisonOperatorType._CF_enumeration.addEnumeration(unicode_value=u'LessThan')
ComparisonOperatorType.GreaterThan = ComparisonOperatorType._CF_enumeration.addEnumeration(unicode_value=u'GreaterThan')
ComparisonOperatorType.LessThanEqualTo = ComparisonOperatorType._CF_enumeration.addEnumeration(unicode_value=u'LessThanEqualTo')
ComparisonOperatorType.GreaterThanEqualTo = ComparisonOperatorType._CF_enumeration.addEnumeration(unicode_value=u'GreaterThanEqualTo')
ComparisonOperatorType.EqualTo = ComparisonOperatorType._CF_enumeration.addEnumeration(unicode_value=u'EqualTo')
ComparisonOperatorType.NotEqualTo = ComparisonOperatorType._CF_enumeration.addEnumeration(unicode_value=u'NotEqualTo')
ComparisonOperatorType.Like = ComparisonOperatorType._CF_enumeration.addEnumeration(unicode_value=u'Like')
ComparisonOperatorType.Between = ComparisonOperatorType._CF_enumeration.addEnumeration(unicode_value=u'Between')
ComparisonOperatorType.NullCheck = ComparisonOperatorType._CF_enumeration.addEnumeration(unicode_value=u'NullCheck')
ComparisonOperatorType._InitializeFacetMap(ComparisonOperatorType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'ComparisonOperatorType', ComparisonOperatorType)

# Atomic SimpleTypeDefinition
class GeometryOperandType (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'GeometryOperandType')
    _Documentation = None
GeometryOperandType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=GeometryOperandType, enum_prefix=None)
GeometryOperandType.gmlEnvelope = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Envelope')
GeometryOperandType.gmlPoint = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Point')
GeometryOperandType.gmlLineString = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:LineString')
GeometryOperandType.gmlPolygon = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Polygon')
GeometryOperandType.gmlArcByCenterPoint = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:ArcByCenterPoint')
GeometryOperandType.gmlCircleByCenterPoint = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:CircleByCenterPoint')
GeometryOperandType.gmlArc = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Arc')
GeometryOperandType.gmlCircle = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Circle')
GeometryOperandType.gmlArcByBulge = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:ArcByBulge')
GeometryOperandType.gmlBezier = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Bezier')
GeometryOperandType.gmlClothoid = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Clothoid')
GeometryOperandType.gmlCubicSpline = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:CubicSpline')
GeometryOperandType.gmlGeodesic = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Geodesic')
GeometryOperandType.gmlOffsetCurve = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:OffsetCurve')
GeometryOperandType.gmlTriangle = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Triangle')
GeometryOperandType.gmlPolyhedralSurface = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:PolyhedralSurface')
GeometryOperandType.gmlTriangulatedSurface = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:TriangulatedSurface')
GeometryOperandType.gmlTin = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Tin')
GeometryOperandType.gmlSolid = GeometryOperandType._CF_enumeration.addEnumeration(unicode_value=u'gml:Solid')
GeometryOperandType._InitializeFacetMap(GeometryOperandType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'GeometryOperandType', GeometryOperandType)

# Complex type CTD_ANON_1 with content type EMPTY
class CTD_ANON_1 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type ExpressionType with content type EMPTY
class ExpressionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExpressionType')
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ExpressionType', ExpressionType)


# Complex type PropertyNameType with content type MIXED
class PropertyNameType (ExpressionType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PropertyNameType')
    # Base type is ExpressionType

    _ElementMap = ExpressionType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExpressionType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PropertyNameType', PropertyNameType)


# Complex type LogicOpsType with content type EMPTY
class LogicOpsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LogicOpsType')
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'LogicOpsType', LogicOpsType)


# Complex type BinaryLogicOpType with content type ELEMENT_ONLY
class BinaryLogicOpType (LogicOpsType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BinaryLogicOpType')
    # Base type is LogicOpsType
    
    # Element {http://www.opengis.net/ogc}logicOps uses Python identifier logicOps
    __logicOps = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'logicOps'), 'logicOps', '__httpwww_opengis_netogc_BinaryLogicOpType_httpwww_opengis_netogclogicOps', True)

    
    logicOps = property(__logicOps.value, __logicOps.set, None, None)

    
    # Element {http://www.opengis.net/ogc}spatialOps uses Python identifier spatialOps
    __spatialOps = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'), 'spatialOps', '__httpwww_opengis_netogc_BinaryLogicOpType_httpwww_opengis_netogcspatialOps', True)

    
    spatialOps = property(__spatialOps.value, __spatialOps.set, None, None)

    
    # Element {http://www.opengis.net/ogc}comparisonOps uses Python identifier comparisonOps
    __comparisonOps = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'), 'comparisonOps', '__httpwww_opengis_netogc_BinaryLogicOpType_httpwww_opengis_netogccomparisonOps', True)

    
    comparisonOps = property(__comparisonOps.value, __comparisonOps.set, None, None)


    _ElementMap = LogicOpsType._ElementMap.copy()
    _ElementMap.update({
        __logicOps.name() : __logicOps,
        __spatialOps.name() : __spatialOps,
        __comparisonOps.name() : __comparisonOps
    })
    _AttributeMap = LogicOpsType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BinaryLogicOpType', BinaryLogicOpType)


# Complex type Scalar_CapabilitiesType with content type ELEMENT_ONLY
class Scalar_CapabilitiesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Scalar_CapabilitiesType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}ArithmeticOperators uses Python identifier ArithmeticOperators
    __ArithmeticOperators = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ArithmeticOperators'), 'ArithmeticOperators', '__httpwww_opengis_netogc_Scalar_CapabilitiesType_httpwww_opengis_netogcArithmeticOperators', False)

    
    ArithmeticOperators = property(__ArithmeticOperators.value, __ArithmeticOperators.set, None, None)

    
    # Element {http://www.opengis.net/ogc}LogicalOperators uses Python identifier LogicalOperators
    __LogicalOperators = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LogicalOperators'), 'LogicalOperators', '__httpwww_opengis_netogc_Scalar_CapabilitiesType_httpwww_opengis_netogcLogicalOperators', False)

    
    LogicalOperators = property(__LogicalOperators.value, __LogicalOperators.set, None, None)

    
    # Element {http://www.opengis.net/ogc}ComparisonOperators uses Python identifier ComparisonOperators
    __ComparisonOperators = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ComparisonOperators'), 'ComparisonOperators', '__httpwww_opengis_netogc_Scalar_CapabilitiesType_httpwww_opengis_netogcComparisonOperators', False)

    
    ComparisonOperators = property(__ComparisonOperators.value, __ComparisonOperators.set, None, None)


    _ElementMap = {
        __ArithmeticOperators.name() : __ArithmeticOperators,
        __LogicalOperators.name() : __LogicalOperators,
        __ComparisonOperators.name() : __ComparisonOperators
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Scalar_CapabilitiesType', Scalar_CapabilitiesType)


# Complex type ComparisonOpsType with content type EMPTY
class ComparisonOpsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ComparisonOpsType')
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ComparisonOpsType', ComparisonOpsType)


# Complex type SpatialOpsType with content type EMPTY
class SpatialOpsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SpatialOpsType')
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SpatialOpsType', SpatialOpsType)


# Complex type BinarySpatialOpType with content type ELEMENT_ONLY
class BinarySpatialOpType (SpatialOpsType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BinarySpatialOpType')
    # Base type is SpatialOpsType
    
    # Element {http://www.opengis.net/gml}_Geometry uses Python identifier Geometry
    __Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Geometry'), 'Geometry', '__httpwww_opengis_netogc_BinarySpatialOpType_httpwww_opengis_netgml_Geometry', False)

    
    Geometry = property(__Geometry.value, __Geometry.set, None, u'The "_Geometry" element is the abstract head of the substituition group for all geometry elements of GML 3. This \n\t\t\tincludes pre-defined and user-defined geometry elements. Any geometry element must be a direct or indirect extension/restriction \n\t\t\tof AbstractGeometryType and must be directly or indirectly in the substitution group of "_Geometry".')

    
    # Element {http://www.opengis.net/ogc}PropertyName uses Python identifier PropertyName
    __PropertyName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), 'PropertyName', '__httpwww_opengis_netogc_BinarySpatialOpType_httpwww_opengis_netogcPropertyName', False)

    
    PropertyName = property(__PropertyName.value, __PropertyName.set, None, None)

    
    # Element {http://www.opengis.net/gml}Envelope uses Python identifier Envelope
    __Envelope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'Envelope'), 'Envelope', '__httpwww_opengis_netogc_BinarySpatialOpType_httpwww_opengis_netgmlEnvelope', False)

    
    Envelope = property(__Envelope.value, __Envelope.set, None, None)


    _ElementMap = SpatialOpsType._ElementMap.copy()
    _ElementMap.update({
        __Geometry.name() : __Geometry,
        __PropertyName.name() : __PropertyName,
        __Envelope.name() : __Envelope
    })
    _AttributeMap = SpatialOpsType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BinarySpatialOpType', BinarySpatialOpType)


# Complex type UnaryLogicOpType with content type ELEMENT_ONLY
class UnaryLogicOpType (LogicOpsType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UnaryLogicOpType')
    # Base type is LogicOpsType
    
    # Element {http://www.opengis.net/ogc}comparisonOps uses Python identifier comparisonOps
    __comparisonOps = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'), 'comparisonOps', '__httpwww_opengis_netogc_UnaryLogicOpType_httpwww_opengis_netogccomparisonOps', False)

    
    comparisonOps = property(__comparisonOps.value, __comparisonOps.set, None, None)

    
    # Element {http://www.opengis.net/ogc}spatialOps uses Python identifier spatialOps
    __spatialOps = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'), 'spatialOps', '__httpwww_opengis_netogc_UnaryLogicOpType_httpwww_opengis_netogcspatialOps', False)

    
    spatialOps = property(__spatialOps.value, __spatialOps.set, None, None)

    
    # Element {http://www.opengis.net/ogc}logicOps uses Python identifier logicOps
    __logicOps = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'logicOps'), 'logicOps', '__httpwww_opengis_netogc_UnaryLogicOpType_httpwww_opengis_netogclogicOps', False)

    
    logicOps = property(__logicOps.value, __logicOps.set, None, None)


    _ElementMap = LogicOpsType._ElementMap.copy()
    _ElementMap.update({
        __comparisonOps.name() : __comparisonOps,
        __spatialOps.name() : __spatialOps,
        __logicOps.name() : __logicOps
    })
    _AttributeMap = LogicOpsType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'UnaryLogicOpType', UnaryLogicOpType)


# Complex type LiteralType with content type MIXED
class LiteralType (ExpressionType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LiteralType')
    # Base type is ExpressionType
    _HasWildcardElement = True

    _ElementMap = ExpressionType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExpressionType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LiteralType', LiteralType)


# Complex type AbstractIdType with content type EMPTY
class AbstractIdType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractIdType')
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AbstractIdType', AbstractIdType)


# Complex type FeatureIdType with content type EMPTY
class FeatureIdType (AbstractIdType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FeatureIdType')
    # Base type is AbstractIdType
    
    # Attribute fid uses Python identifier fid
    __fid = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'fid'), 'fid', '__httpwww_opengis_netogc_FeatureIdType_fid', pyxb.binding.datatypes.ID, required=True)
    
    fid = property(__fid.value, __fid.set, None, None)


    _ElementMap = AbstractIdType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = AbstractIdType._AttributeMap.copy()
    _AttributeMap.update({
        __fid.name() : __fid
    })
Namespace.addCategoryObject('typeBinding', u'FeatureIdType', FeatureIdType)


# Complex type ComparisonOperatorsType with content type ELEMENT_ONLY
class ComparisonOperatorsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ComparisonOperatorsType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}ComparisonOperator uses Python identifier ComparisonOperator
    __ComparisonOperator = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ComparisonOperator'), 'ComparisonOperator', '__httpwww_opengis_netogc_ComparisonOperatorsType_httpwww_opengis_netogcComparisonOperator', True)

    
    ComparisonOperator = property(__ComparisonOperator.value, __ComparisonOperator.set, None, None)


    _ElementMap = {
        __ComparisonOperator.name() : __ComparisonOperator
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ComparisonOperatorsType', ComparisonOperatorsType)


# Complex type BinaryOperatorType with content type ELEMENT_ONLY
class BinaryOperatorType (ExpressionType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BinaryOperatorType')
    # Base type is ExpressionType
    
    # Element {http://www.opengis.net/ogc}expression uses Python identifier expression
    __expression = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'expression'), 'expression', '__httpwww_opengis_netogc_BinaryOperatorType_httpwww_opengis_netogcexpression', True)

    
    expression = property(__expression.value, __expression.set, None, None)


    _ElementMap = ExpressionType._ElementMap.copy()
    _ElementMap.update({
        __expression.name() : __expression
    })
    _AttributeMap = ExpressionType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BinaryOperatorType', BinaryOperatorType)


# Complex type SpatialOperatorType with content type ELEMENT_ONLY
class SpatialOperatorType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SpatialOperatorType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}GeometryOperands uses Python identifier GeometryOperands
    __GeometryOperands = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'GeometryOperands'), 'GeometryOperands', '__httpwww_opengis_netogc_SpatialOperatorType_httpwww_opengis_netogcGeometryOperands', False)

    
    GeometryOperands = property(__GeometryOperands.value, __GeometryOperands.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netogc_SpatialOperatorType_name', SpatialOperatorNameType)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        __GeometryOperands.name() : __GeometryOperands
    }
    _AttributeMap = {
        __name.name() : __name
    }
Namespace.addCategoryObject('typeBinding', u'SpatialOperatorType', SpatialOperatorType)


# Complex type LowerBoundaryType with content type ELEMENT_ONLY
class LowerBoundaryType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LowerBoundaryType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}expression uses Python identifier expression
    __expression = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'expression'), 'expression', '__httpwww_opengis_netogc_LowerBoundaryType_httpwww_opengis_netogcexpression', False)

    
    expression = property(__expression.value, __expression.set, None, None)


    _ElementMap = {
        __expression.name() : __expression
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'LowerBoundaryType', LowerBoundaryType)


# Complex type SortPropertyType with content type ELEMENT_ONLY
class SortPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SortPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}SortOrder uses Python identifier SortOrder
    __SortOrder = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SortOrder'), 'SortOrder', '__httpwww_opengis_netogc_SortPropertyType_httpwww_opengis_netogcSortOrder', False)

    
    SortOrder = property(__SortOrder.value, __SortOrder.set, None, None)

    
    # Element {http://www.opengis.net/ogc}PropertyName uses Python identifier PropertyName
    __PropertyName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), 'PropertyName', '__httpwww_opengis_netogc_SortPropertyType_httpwww_opengis_netogcPropertyName', False)

    
    PropertyName = property(__PropertyName.value, __PropertyName.set, None, None)


    _ElementMap = {
        __SortOrder.name() : __SortOrder,
        __PropertyName.name() : __PropertyName
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SortPropertyType', SortPropertyType)


# Complex type DistanceType with content type EMPTY
class DistanceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DistanceType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute units uses Python identifier units
    __units = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'units'), 'units', '__httpwww_opengis_netogc_DistanceType_units', pyxb.binding.datatypes.string, required=True)
    
    units = property(__units.value, __units.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __units.name() : __units
    }
Namespace.addCategoryObject('typeBinding', u'DistanceType', DistanceType)


# Complex type GeometryOperandsType with content type ELEMENT_ONLY
class GeometryOperandsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'GeometryOperandsType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}GeometryOperand uses Python identifier GeometryOperand
    __GeometryOperand = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'GeometryOperand'), 'GeometryOperand', '__httpwww_opengis_netogc_GeometryOperandsType_httpwww_opengis_netogcGeometryOperand', True)

    
    GeometryOperand = property(__GeometryOperand.value, __GeometryOperand.set, None, None)


    _ElementMap = {
        __GeometryOperand.name() : __GeometryOperand
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'GeometryOperandsType', GeometryOperandsType)


# Complex type PropertyIsNullType with content type ELEMENT_ONLY
class PropertyIsNullType (ComparisonOpsType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PropertyIsNullType')
    # Base type is ComparisonOpsType
    
    # Element {http://www.opengis.net/ogc}PropertyName uses Python identifier PropertyName
    __PropertyName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), 'PropertyName', '__httpwww_opengis_netogc_PropertyIsNullType_httpwww_opengis_netogcPropertyName', False)

    
    PropertyName = property(__PropertyName.value, __PropertyName.set, None, None)


    _ElementMap = ComparisonOpsType._ElementMap.copy()
    _ElementMap.update({
        __PropertyName.name() : __PropertyName
    })
    _AttributeMap = ComparisonOpsType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PropertyIsNullType', PropertyIsNullType)


# Complex type CTD_ANON_2 with content type EMPTY
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type BinaryComparisonOpType with content type ELEMENT_ONLY
class BinaryComparisonOpType (ComparisonOpsType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BinaryComparisonOpType')
    # Base type is ComparisonOpsType
    
    # Element {http://www.opengis.net/ogc}expression uses Python identifier expression
    __expression = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'expression'), 'expression', '__httpwww_opengis_netogc_BinaryComparisonOpType_httpwww_opengis_netogcexpression', True)

    
    expression = property(__expression.value, __expression.set, None, None)

    
    # Attribute matchCase uses Python identifier matchCase
    __matchCase = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'matchCase'), 'matchCase', '__httpwww_opengis_netogc_BinaryComparisonOpType_matchCase', pyxb.binding.datatypes.boolean, unicode_default=u'true')
    
    matchCase = property(__matchCase.value, __matchCase.set, None, None)


    _ElementMap = ComparisonOpsType._ElementMap.copy()
    _ElementMap.update({
        __expression.name() : __expression
    })
    _AttributeMap = ComparisonOpsType._AttributeMap.copy()
    _AttributeMap.update({
        __matchCase.name() : __matchCase
    })
Namespace.addCategoryObject('typeBinding', u'BinaryComparisonOpType', BinaryComparisonOpType)


# Complex type CTD_ANON_3 with content type ELEMENT_ONLY
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}Id_Capabilities uses Python identifier Id_Capabilities
    __Id_Capabilities = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Id_Capabilities'), 'Id_Capabilities', '__httpwww_opengis_netogc_CTD_ANON_3_httpwww_opengis_netogcId_Capabilities', False)

    
    Id_Capabilities = property(__Id_Capabilities.value, __Id_Capabilities.set, None, None)

    
    # Element {http://www.opengis.net/ogc}Spatial_Capabilities uses Python identifier Spatial_Capabilities
    __Spatial_Capabilities = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Spatial_Capabilities'), 'Spatial_Capabilities', '__httpwww_opengis_netogc_CTD_ANON_3_httpwww_opengis_netogcSpatial_Capabilities', False)

    
    Spatial_Capabilities = property(__Spatial_Capabilities.value, __Spatial_Capabilities.set, None, None)

    
    # Element {http://www.opengis.net/ogc}Scalar_Capabilities uses Python identifier Scalar_Capabilities
    __Scalar_Capabilities = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Scalar_Capabilities'), 'Scalar_Capabilities', '__httpwww_opengis_netogc_CTD_ANON_3_httpwww_opengis_netogcScalar_Capabilities', False)

    
    Scalar_Capabilities = property(__Scalar_Capabilities.value, __Scalar_Capabilities.set, None, None)


    _ElementMap = {
        __Id_Capabilities.name() : __Id_Capabilities,
        __Spatial_Capabilities.name() : __Spatial_Capabilities,
        __Scalar_Capabilities.name() : __Scalar_Capabilities
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_4 with content type EMPTY
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type DistanceBufferType with content type ELEMENT_ONLY
class DistanceBufferType (SpatialOpsType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DistanceBufferType')
    # Base type is SpatialOpsType
    
    # Element {http://www.opengis.net/ogc}Distance uses Python identifier Distance
    __Distance = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Distance'), 'Distance', '__httpwww_opengis_netogc_DistanceBufferType_httpwww_opengis_netogcDistance', False)

    
    Distance = property(__Distance.value, __Distance.set, None, None)

    
    # Element {http://www.opengis.net/ogc}PropertyName uses Python identifier PropertyName
    __PropertyName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), 'PropertyName', '__httpwww_opengis_netogc_DistanceBufferType_httpwww_opengis_netogcPropertyName', False)

    
    PropertyName = property(__PropertyName.value, __PropertyName.set, None, None)

    
    # Element {http://www.opengis.net/gml}_Geometry uses Python identifier Geometry
    __Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Geometry'), 'Geometry', '__httpwww_opengis_netogc_DistanceBufferType_httpwww_opengis_netgml_Geometry', False)

    
    Geometry = property(__Geometry.value, __Geometry.set, None, u'The "_Geometry" element is the abstract head of the substituition group for all geometry elements of GML 3. This \n\t\t\tincludes pre-defined and user-defined geometry elements. Any geometry element must be a direct or indirect extension/restriction \n\t\t\tof AbstractGeometryType and must be directly or indirectly in the substitution group of "_Geometry".')


    _ElementMap = SpatialOpsType._ElementMap.copy()
    _ElementMap.update({
        __Distance.name() : __Distance,
        __PropertyName.name() : __PropertyName,
        __Geometry.name() : __Geometry
    })
    _AttributeMap = SpatialOpsType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'DistanceBufferType', DistanceBufferType)


# Complex type PropertyIsLikeType with content type ELEMENT_ONLY
class PropertyIsLikeType (ComparisonOpsType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PropertyIsLikeType')
    # Base type is ComparisonOpsType
    
    # Element {http://www.opengis.net/ogc}Literal uses Python identifier Literal
    __Literal = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Literal'), 'Literal', '__httpwww_opengis_netogc_PropertyIsLikeType_httpwww_opengis_netogcLiteral', False)

    
    Literal = property(__Literal.value, __Literal.set, None, None)

    
    # Element {http://www.opengis.net/ogc}PropertyName uses Python identifier PropertyName
    __PropertyName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), 'PropertyName', '__httpwww_opengis_netogc_PropertyIsLikeType_httpwww_opengis_netogcPropertyName', False)

    
    PropertyName = property(__PropertyName.value, __PropertyName.set, None, None)

    
    # Attribute singleChar uses Python identifier singleChar
    __singleChar = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'singleChar'), 'singleChar', '__httpwww_opengis_netogc_PropertyIsLikeType_singleChar', pyxb.binding.datatypes.string, required=True)
    
    singleChar = property(__singleChar.value, __singleChar.set, None, None)

    
    # Attribute escapeChar uses Python identifier escapeChar
    __escapeChar = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'escapeChar'), 'escapeChar', '__httpwww_opengis_netogc_PropertyIsLikeType_escapeChar', pyxb.binding.datatypes.string, required=True)
    
    escapeChar = property(__escapeChar.value, __escapeChar.set, None, None)

    
    # Attribute wildCard uses Python identifier wildCard
    __wildCard = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'wildCard'), 'wildCard', '__httpwww_opengis_netogc_PropertyIsLikeType_wildCard', pyxb.binding.datatypes.string, required=True)
    
    wildCard = property(__wildCard.value, __wildCard.set, None, None)


    _ElementMap = ComparisonOpsType._ElementMap.copy()
    _ElementMap.update({
        __Literal.name() : __Literal,
        __PropertyName.name() : __PropertyName
    })
    _AttributeMap = ComparisonOpsType._AttributeMap.copy()
    _AttributeMap.update({
        __singleChar.name() : __singleChar,
        __escapeChar.name() : __escapeChar,
        __wildCard.name() : __wildCard
    })
Namespace.addCategoryObject('typeBinding', u'PropertyIsLikeType', PropertyIsLikeType)


# Complex type BBOXType with content type ELEMENT_ONLY
class BBOXType (SpatialOpsType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BBOXType')
    # Base type is SpatialOpsType
    
    # Element {http://www.opengis.net/gml}Envelope uses Python identifier Envelope
    __Envelope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'Envelope'), 'Envelope', '__httpwww_opengis_netogc_BBOXType_httpwww_opengis_netgmlEnvelope', False)

    
    Envelope = property(__Envelope.value, __Envelope.set, None, None)

    
    # Element {http://www.opengis.net/ogc}PropertyName uses Python identifier PropertyName
    __PropertyName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), 'PropertyName', '__httpwww_opengis_netogc_BBOXType_httpwww_opengis_netogcPropertyName', False)

    
    PropertyName = property(__PropertyName.value, __PropertyName.set, None, None)


    _ElementMap = SpatialOpsType._ElementMap.copy()
    _ElementMap.update({
        __Envelope.name() : __Envelope,
        __PropertyName.name() : __PropertyName
    })
    _AttributeMap = SpatialOpsType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BBOXType', BBOXType)


# Complex type FunctionsType with content type ELEMENT_ONLY
class FunctionsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FunctionsType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}FunctionNames uses Python identifier FunctionNames
    __FunctionNames = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FunctionNames'), 'FunctionNames', '__httpwww_opengis_netogc_FunctionsType_httpwww_opengis_netogcFunctionNames', False)

    
    FunctionNames = property(__FunctionNames.value, __FunctionNames.set, None, None)


    _ElementMap = {
        __FunctionNames.name() : __FunctionNames
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'FunctionsType', FunctionsType)


# Complex type Spatial_CapabilitiesType with content type ELEMENT_ONLY
class Spatial_CapabilitiesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Spatial_CapabilitiesType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}SpatialOperators uses Python identifier SpatialOperators
    __SpatialOperators = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SpatialOperators'), 'SpatialOperators', '__httpwww_opengis_netogc_Spatial_CapabilitiesType_httpwww_opengis_netogcSpatialOperators', False)

    
    SpatialOperators = property(__SpatialOperators.value, __SpatialOperators.set, None, None)

    
    # Element {http://www.opengis.net/ogc}GeometryOperands uses Python identifier GeometryOperands
    __GeometryOperands = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'GeometryOperands'), 'GeometryOperands', '__httpwww_opengis_netogc_Spatial_CapabilitiesType_httpwww_opengis_netogcGeometryOperands', False)

    
    GeometryOperands = property(__GeometryOperands.value, __GeometryOperands.set, None, None)


    _ElementMap = {
        __SpatialOperators.name() : __SpatialOperators,
        __GeometryOperands.name() : __GeometryOperands
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Spatial_CapabilitiesType', Spatial_CapabilitiesType)


# Complex type FunctionNameType with content type SIMPLE
class FunctionNameType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FunctionNameType')
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute nArgs uses Python identifier nArgs
    __nArgs = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'nArgs'), 'nArgs', '__httpwww_opengis_netogc_FunctionNameType_nArgs', pyxb.binding.datatypes.string, required=True)
    
    nArgs = property(__nArgs.value, __nArgs.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __nArgs.name() : __nArgs
    }
Namespace.addCategoryObject('typeBinding', u'FunctionNameType', FunctionNameType)


# Complex type Id_CapabilitiesType with content type ELEMENT_ONLY
class Id_CapabilitiesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Id_CapabilitiesType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}FID uses Python identifier FID
    __FID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FID'), 'FID', '__httpwww_opengis_netogc_Id_CapabilitiesType_httpwww_opengis_netogcFID', True)

    
    FID = property(__FID.value, __FID.set, None, None)

    
    # Element {http://www.opengis.net/ogc}EID uses Python identifier EID
    __EID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EID'), 'EID', '__httpwww_opengis_netogc_Id_CapabilitiesType_httpwww_opengis_netogcEID', True)

    
    EID = property(__EID.value, __EID.set, None, None)


    _ElementMap = {
        __FID.name() : __FID,
        __EID.name() : __EID
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Id_CapabilitiesType', Id_CapabilitiesType)


# Complex type FunctionType with content type ELEMENT_ONLY
class FunctionType (ExpressionType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FunctionType')
    # Base type is ExpressionType
    
    # Element {http://www.opengis.net/ogc}expression uses Python identifier expression
    __expression = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'expression'), 'expression', '__httpwww_opengis_netogc_FunctionType_httpwww_opengis_netogcexpression', True)

    
    expression = property(__expression.value, __expression.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netogc_FunctionType_name', pyxb.binding.datatypes.string, required=True)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = ExpressionType._ElementMap.copy()
    _ElementMap.update({
        __expression.name() : __expression
    })
    _AttributeMap = ExpressionType._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'FunctionType', FunctionType)


# Complex type FilterType with content type ELEMENT_ONLY
class FilterType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FilterType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}spatialOps uses Python identifier spatialOps
    __spatialOps = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'), 'spatialOps', '__httpwww_opengis_netogc_FilterType_httpwww_opengis_netogcspatialOps', False)

    
    spatialOps = property(__spatialOps.value, __spatialOps.set, None, None)

    
    # Element {http://www.opengis.net/ogc}comparisonOps uses Python identifier comparisonOps
    __comparisonOps = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'), 'comparisonOps', '__httpwww_opengis_netogc_FilterType_httpwww_opengis_netogccomparisonOps', False)

    
    comparisonOps = property(__comparisonOps.value, __comparisonOps.set, None, None)

    
    # Element {http://www.opengis.net/ogc}_Id uses Python identifier Id
    __Id = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_Id'), 'Id', '__httpwww_opengis_netogc_FilterType_httpwww_opengis_netogc_Id', True)

    
    Id = property(__Id.value, __Id.set, None, None)

    
    # Element {http://www.opengis.net/ogc}logicOps uses Python identifier logicOps
    __logicOps = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'logicOps'), 'logicOps', '__httpwww_opengis_netogc_FilterType_httpwww_opengis_netogclogicOps', False)

    
    logicOps = property(__logicOps.value, __logicOps.set, None, None)


    _ElementMap = {
        __spatialOps.name() : __spatialOps,
        __comparisonOps.name() : __comparisonOps,
        __Id.name() : __Id,
        __logicOps.name() : __logicOps
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'FilterType', FilterType)


# Complex type FunctionNamesType with content type ELEMENT_ONLY
class FunctionNamesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FunctionNamesType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}FunctionName uses Python identifier FunctionName
    __FunctionName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FunctionName'), 'FunctionName', '__httpwww_opengis_netogc_FunctionNamesType_httpwww_opengis_netogcFunctionName', True)

    
    FunctionName = property(__FunctionName.value, __FunctionName.set, None, None)


    _ElementMap = {
        __FunctionName.name() : __FunctionName
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'FunctionNamesType', FunctionNamesType)


# Complex type SpatialOperatorsType with content type ELEMENT_ONLY
class SpatialOperatorsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SpatialOperatorsType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}SpatialOperator uses Python identifier SpatialOperator
    __SpatialOperator = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SpatialOperator'), 'SpatialOperator', '__httpwww_opengis_netogc_SpatialOperatorsType_httpwww_opengis_netogcSpatialOperator', True)

    
    SpatialOperator = property(__SpatialOperator.value, __SpatialOperator.set, None, None)


    _ElementMap = {
        __SpatialOperator.name() : __SpatialOperator
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SpatialOperatorsType', SpatialOperatorsType)


# Complex type CTD_ANON_5 with content type EMPTY
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type GmlObjectIdType with content type EMPTY
class GmlObjectIdType (AbstractIdType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'GmlObjectIdType')
    # Base type is AbstractIdType
    
    # Attribute {http://www.opengis.net/gml}id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'id'), 'id', '__httpwww_opengis_netogc_GmlObjectIdType_httpwww_opengis_netgmlid', pyxb.binding.datatypes.ID, required=True)
    
    id = property(__id.value, __id.set, None, u'Database handle for the object.  It is of XML type ID, so is constrained to be unique in the XML document within which it occurs.  An external identifier for the object in the form of a URI may be constructed using standard XML and XPointer methods.  This is done by concatenating the URI for the document, a fragment separator, and the value of the id attribute.')


    _ElementMap = AbstractIdType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = AbstractIdType._AttributeMap.copy()
    _AttributeMap.update({
        __id.name() : __id
    })
Namespace.addCategoryObject('typeBinding', u'GmlObjectIdType', GmlObjectIdType)


# Complex type SortByType with content type ELEMENT_ONLY
class SortByType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SortByType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}SortProperty uses Python identifier SortProperty
    __SortProperty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SortProperty'), 'SortProperty', '__httpwww_opengis_netogc_SortByType_httpwww_opengis_netogcSortProperty', True)

    
    SortProperty = property(__SortProperty.value, __SortProperty.set, None, None)


    _ElementMap = {
        __SortProperty.name() : __SortProperty
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SortByType', SortByType)


# Complex type UpperBoundaryType with content type ELEMENT_ONLY
class UpperBoundaryType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UpperBoundaryType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}expression uses Python identifier expression
    __expression = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'expression'), 'expression', '__httpwww_opengis_netogc_UpperBoundaryType_httpwww_opengis_netogcexpression', False)

    
    expression = property(__expression.value, __expression.set, None, None)


    _ElementMap = {
        __expression.name() : __expression
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'UpperBoundaryType', UpperBoundaryType)


# Complex type PropertyIsBetweenType with content type ELEMENT_ONLY
class PropertyIsBetweenType (ComparisonOpsType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PropertyIsBetweenType')
    # Base type is ComparisonOpsType
    
    # Element {http://www.opengis.net/ogc}UpperBoundary uses Python identifier UpperBoundary
    __UpperBoundary = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'UpperBoundary'), 'UpperBoundary', '__httpwww_opengis_netogc_PropertyIsBetweenType_httpwww_opengis_netogcUpperBoundary', False)

    
    UpperBoundary = property(__UpperBoundary.value, __UpperBoundary.set, None, None)

    
    # Element {http://www.opengis.net/ogc}expression uses Python identifier expression
    __expression = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'expression'), 'expression', '__httpwww_opengis_netogc_PropertyIsBetweenType_httpwww_opengis_netogcexpression', False)

    
    expression = property(__expression.value, __expression.set, None, None)

    
    # Element {http://www.opengis.net/ogc}LowerBoundary uses Python identifier LowerBoundary
    __LowerBoundary = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LowerBoundary'), 'LowerBoundary', '__httpwww_opengis_netogc_PropertyIsBetweenType_httpwww_opengis_netogcLowerBoundary', False)

    
    LowerBoundary = property(__LowerBoundary.value, __LowerBoundary.set, None, None)


    _ElementMap = ComparisonOpsType._ElementMap.copy()
    _ElementMap.update({
        __UpperBoundary.name() : __UpperBoundary,
        __expression.name() : __expression,
        __LowerBoundary.name() : __LowerBoundary
    })
    _AttributeMap = ComparisonOpsType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PropertyIsBetweenType', PropertyIsBetweenType)


# Complex type ArithmeticOperatorsType with content type ELEMENT_ONLY
class ArithmeticOperatorsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ArithmeticOperatorsType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/ogc}Functions uses Python identifier Functions
    __Functions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Functions'), 'Functions', '__httpwww_opengis_netogc_ArithmeticOperatorsType_httpwww_opengis_netogcFunctions', True)

    
    Functions = property(__Functions.value, __Functions.set, None, None)

    
    # Element {http://www.opengis.net/ogc}SimpleArithmetic uses Python identifier SimpleArithmetic
    __SimpleArithmetic = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SimpleArithmetic'), 'SimpleArithmetic', '__httpwww_opengis_netogc_ArithmeticOperatorsType_httpwww_opengis_netogcSimpleArithmetic', True)

    
    SimpleArithmetic = property(__SimpleArithmetic.value, __SimpleArithmetic.set, None, None)


    _ElementMap = {
        __Functions.name() : __Functions,
        __SimpleArithmetic.name() : __SimpleArithmetic
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ArithmeticOperatorsType', ArithmeticOperatorsType)


And = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'And'), BinaryLogicOpType)
Namespace.addCategoryObject('elementBinding', And.name().localName(), And)

Touches = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Touches'), BinarySpatialOpType)
Namespace.addCategoryObject('elementBinding', Touches.name().localName(), Touches)

Not = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Not'), UnaryLogicOpType)
Namespace.addCategoryObject('elementBinding', Not.name().localName(), Not)

Literal = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Literal'), LiteralType)
Namespace.addCategoryObject('elementBinding', Literal.name().localName(), Literal)

FeatureId = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FeatureId'), FeatureIdType)
Namespace.addCategoryObject('elementBinding', FeatureId.name().localName(), FeatureId)

Add = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Add'), BinaryOperatorType)
Namespace.addCategoryObject('elementBinding', Add.name().localName(), Add)

PropertyIsNull = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyIsNull'), PropertyIsNullType)
Namespace.addCategoryObject('elementBinding', PropertyIsNull.name().localName(), PropertyIsNull)

Equals = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Equals'), BinarySpatialOpType)
Namespace.addCategoryObject('elementBinding', Equals.name().localName(), Equals)

SimpleArithmetic = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SimpleArithmetic'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', SimpleArithmetic.name().localName(), SimpleArithmetic)

logicOps = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'logicOps'), LogicOpsType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', logicOps.name().localName(), logicOps)

PropertyIsNotEqualTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyIsNotEqualTo'), BinaryComparisonOpType)
Namespace.addCategoryObject('elementBinding', PropertyIsNotEqualTo.name().localName(), PropertyIsNotEqualTo)

Filter_Capabilities = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Filter_Capabilities'), CTD_ANON_3)
Namespace.addCategoryObject('elementBinding', Filter_Capabilities.name().localName(), Filter_Capabilities)

Disjoint = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Disjoint'), BinarySpatialOpType)
Namespace.addCategoryObject('elementBinding', Disjoint.name().localName(), Disjoint)

EID = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EID'), CTD_ANON_4)
Namespace.addCategoryObject('elementBinding', EID.name().localName(), EID)

Id = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Id'), AbstractIdType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', Id.name().localName(), Id)

Beyond = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Beyond'), DistanceBufferType)
Namespace.addCategoryObject('elementBinding', Beyond.name().localName(), Beyond)

Sub = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Sub'), BinaryOperatorType)
Namespace.addCategoryObject('elementBinding', Sub.name().localName(), Sub)

PropertyIsGreaterThan = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyIsGreaterThan'), BinaryComparisonOpType)
Namespace.addCategoryObject('elementBinding', PropertyIsGreaterThan.name().localName(), PropertyIsGreaterThan)

PropertyIsEqualTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyIsEqualTo'), BinaryComparisonOpType)
Namespace.addCategoryObject('elementBinding', PropertyIsEqualTo.name().localName(), PropertyIsEqualTo)

PropertyIsLessThan = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyIsLessThan'), BinaryComparisonOpType)
Namespace.addCategoryObject('elementBinding', PropertyIsLessThan.name().localName(), PropertyIsLessThan)

PropertyIsLike = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyIsLike'), PropertyIsLikeType)
Namespace.addCategoryObject('elementBinding', PropertyIsLike.name().localName(), PropertyIsLike)

spatialOps = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'), SpatialOpsType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', spatialOps.name().localName(), spatialOps)

Contains = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Contains'), BinarySpatialOpType)
Namespace.addCategoryObject('elementBinding', Contains.name().localName(), Contains)

BBOX = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BBOX'), BBOXType)
Namespace.addCategoryObject('elementBinding', BBOX.name().localName(), BBOX)

Mul = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Mul'), BinaryOperatorType)
Namespace.addCategoryObject('elementBinding', Mul.name().localName(), Mul)

Function = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Function'), FunctionType)
Namespace.addCategoryObject('elementBinding', Function.name().localName(), Function)

Filter = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Filter'), FilterType)
Namespace.addCategoryObject('elementBinding', Filter.name().localName(), Filter)

Within = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Within'), BinarySpatialOpType)
Namespace.addCategoryObject('elementBinding', Within.name().localName(), Within)

comparisonOps = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'), ComparisonOpsType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', comparisonOps.name().localName(), comparisonOps)

PropertyIsGreaterThanOrEqualTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyIsGreaterThanOrEqualTo'), BinaryComparisonOpType)
Namespace.addCategoryObject('elementBinding', PropertyIsGreaterThanOrEqualTo.name().localName(), PropertyIsGreaterThanOrEqualTo)

LogicalOperators = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LogicalOperators'), CTD_ANON_1)
Namespace.addCategoryObject('elementBinding', LogicalOperators.name().localName(), LogicalOperators)

DWithin = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DWithin'), DistanceBufferType)
Namespace.addCategoryObject('elementBinding', DWithin.name().localName(), DWithin)

Div = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Div'), BinaryOperatorType)
Namespace.addCategoryObject('elementBinding', Div.name().localName(), Div)

Intersects = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Intersects'), BinarySpatialOpType)
Namespace.addCategoryObject('elementBinding', Intersects.name().localName(), Intersects)

Overlaps = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Overlaps'), BinarySpatialOpType)
Namespace.addCategoryObject('elementBinding', Overlaps.name().localName(), Overlaps)

Or = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Or'), BinaryLogicOpType)
Namespace.addCategoryObject('elementBinding', Or.name().localName(), Or)

PropertyName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), PropertyNameType)
Namespace.addCategoryObject('elementBinding', PropertyName.name().localName(), PropertyName)

FID = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FID'), CTD_ANON_5)
Namespace.addCategoryObject('elementBinding', FID.name().localName(), FID)

GmlObjectId = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GmlObjectId'), GmlObjectIdType)
Namespace.addCategoryObject('elementBinding', GmlObjectId.name().localName(), GmlObjectId)

Crosses = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Crosses'), BinarySpatialOpType)
Namespace.addCategoryObject('elementBinding', Crosses.name().localName(), Crosses)

SortBy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SortBy'), SortByType)
Namespace.addCategoryObject('elementBinding', SortBy.name().localName(), SortBy)

expression = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'expression'), ExpressionType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', expression.name().localName(), expression)

PropertyIsLessThanOrEqualTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyIsLessThanOrEqualTo'), BinaryComparisonOpType)
Namespace.addCategoryObject('elementBinding', PropertyIsLessThanOrEqualTo.name().localName(), PropertyIsLessThanOrEqualTo)

PropertyIsBetween = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyIsBetween'), PropertyIsBetweenType)
Namespace.addCategoryObject('elementBinding', PropertyIsBetween.name().localName(), PropertyIsBetween)


PropertyNameType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



BinaryLogicOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'logicOps'), LogicOpsType, abstract=pyxb.binding.datatypes.boolean(1), scope=BinaryLogicOpType))

BinaryLogicOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'), SpatialOpsType, abstract=pyxb.binding.datatypes.boolean(1), scope=BinaryLogicOpType))

BinaryLogicOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'), ComparisonOpsType, abstract=pyxb.binding.datatypes.boolean(1), scope=BinaryLogicOpType))
BinaryLogicOpType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BinaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BinaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BinaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'logicOps'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'logicOps'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'logicOps'))),
    ])
})



Scalar_CapabilitiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ArithmeticOperators'), ArithmeticOperatorsType, scope=Scalar_CapabilitiesType))

Scalar_CapabilitiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LogicalOperators'), CTD_ANON_1, scope=Scalar_CapabilitiesType))

Scalar_CapabilitiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ComparisonOperators'), ComparisonOperatorsType, scope=Scalar_CapabilitiesType))
Scalar_CapabilitiesType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Scalar_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LogicalOperators'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Scalar_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ArithmeticOperators'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=Scalar_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ComparisonOperators'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Scalar_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ArithmeticOperators'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=Scalar_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ComparisonOperators'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Scalar_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ArithmeticOperators'))),
    ])
})



BinarySpatialOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Geometry'), pyxb.bundles.opengis.gml.AbstractGeometryType, abstract=pyxb.binding.datatypes.boolean(1), scope=BinarySpatialOpType, documentation=u'The "_Geometry" element is the abstract head of the substituition group for all geometry elements of GML 3. This \n\t\t\tincludes pre-defined and user-defined geometry elements. Any geometry element must be a direct or indirect extension/restriction \n\t\t\tof AbstractGeometryType and must be directly or indirectly in the substitution group of "_Geometry".'))

BinarySpatialOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), PropertyNameType, scope=BinarySpatialOpType))

BinarySpatialOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'Envelope'), pyxb.bundles.opengis.gml.EnvelopeType, scope=BinarySpatialOpType))
BinarySpatialOpType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BinarySpatialOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinarySpatialOpType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Geometry'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinarySpatialOpType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'Envelope'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



UnaryLogicOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'), ComparisonOpsType, abstract=pyxb.binding.datatypes.boolean(1), scope=UnaryLogicOpType))

UnaryLogicOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'), SpatialOpsType, abstract=pyxb.binding.datatypes.boolean(1), scope=UnaryLogicOpType))

UnaryLogicOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'logicOps'), LogicOpsType, abstract=pyxb.binding.datatypes.boolean(1), scope=UnaryLogicOpType))
UnaryLogicOpType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=UnaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=UnaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'logicOps'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=UnaryLogicOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


LiteralType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



ComparisonOperatorsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ComparisonOperator'), ComparisonOperatorType, scope=ComparisonOperatorsType))
ComparisonOperatorsType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComparisonOperatorsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ComparisonOperator'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComparisonOperatorsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ComparisonOperator'))),
    ])
})



BinaryOperatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'expression'), ExpressionType, abstract=pyxb.binding.datatypes.boolean(1), scope=BinaryOperatorType))
BinaryOperatorType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BinaryOperatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'expression'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinaryOperatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'expression'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



SpatialOperatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GeometryOperands'), GeometryOperandsType, scope=SpatialOperatorType))
SpatialOperatorType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpatialOperatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GeometryOperands'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



LowerBoundaryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'expression'), ExpressionType, abstract=pyxb.binding.datatypes.boolean(1), scope=LowerBoundaryType))
LowerBoundaryType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LowerBoundaryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'expression'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



SortPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SortOrder'), SortOrderType, scope=SortPropertyType))

SortPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), PropertyNameType, scope=SortPropertyType))
SortPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SortPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SortPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SortOrder'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



GeometryOperandsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GeometryOperand'), GeometryOperandType, scope=GeometryOperandsType))
GeometryOperandsType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=GeometryOperandsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GeometryOperand'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=GeometryOperandsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GeometryOperand'))),
    ])
})



PropertyIsNullType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), PropertyNameType, scope=PropertyIsNullType))
PropertyIsNullType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PropertyIsNullType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



BinaryComparisonOpType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'expression'), ExpressionType, abstract=pyxb.binding.datatypes.boolean(1), scope=BinaryComparisonOpType))
BinaryComparisonOpType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BinaryComparisonOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'expression'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BinaryComparisonOpType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'expression'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Id_Capabilities'), Id_CapabilitiesType, scope=CTD_ANON_3))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Spatial_Capabilities'), Spatial_CapabilitiesType, scope=CTD_ANON_3))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Scalar_Capabilities'), Scalar_CapabilitiesType, scope=CTD_ANON_3))
CTD_ANON_3._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Spatial_Capabilities'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Scalar_Capabilities'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Id_Capabilities'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
    ])
})



DistanceBufferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Distance'), DistanceType, scope=DistanceBufferType))

DistanceBufferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), PropertyNameType, scope=DistanceBufferType))

DistanceBufferType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Geometry'), pyxb.bundles.opengis.gml.AbstractGeometryType, abstract=pyxb.binding.datatypes.boolean(1), scope=DistanceBufferType, documentation=u'The "_Geometry" element is the abstract head of the substituition group for all geometry elements of GML 3. This \n\t\t\tincludes pre-defined and user-defined geometry elements. Any geometry element must be a direct or indirect extension/restriction \n\t\t\tof AbstractGeometryType and must be directly or indirectly in the substitution group of "_Geometry".'))
DistanceBufferType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DistanceBufferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DistanceBufferType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Geometry'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DistanceBufferType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Distance'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
    ])
})



PropertyIsLikeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Literal'), LiteralType, scope=PropertyIsLikeType))

PropertyIsLikeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), PropertyNameType, scope=PropertyIsLikeType))
PropertyIsLikeType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PropertyIsLikeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PropertyIsLikeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Literal'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



BBOXType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'Envelope'), pyxb.bundles.opengis.gml.EnvelopeType, scope=BBOXType))

BBOXType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'), PropertyNameType, scope=BBOXType))
BBOXType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=BBOXType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PropertyName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=BBOXType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'Envelope'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



FunctionsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FunctionNames'), FunctionNamesType, scope=FunctionsType))
FunctionsType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=FunctionsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FunctionNames'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



Spatial_CapabilitiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SpatialOperators'), SpatialOperatorsType, scope=Spatial_CapabilitiesType))

Spatial_CapabilitiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GeometryOperands'), GeometryOperandsType, scope=Spatial_CapabilitiesType))
Spatial_CapabilitiesType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Spatial_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GeometryOperands'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Spatial_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SpatialOperators'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



Id_CapabilitiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FID'), CTD_ANON_5, scope=Id_CapabilitiesType))

Id_CapabilitiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EID'), CTD_ANON_4, scope=Id_CapabilitiesType))
Id_CapabilitiesType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Id_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EID'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Id_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FID'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Id_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EID'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Id_CapabilitiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FID'))),
    ])
})



FunctionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'expression'), ExpressionType, abstract=pyxb.binding.datatypes.boolean(1), scope=FunctionType))
FunctionType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=FunctionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'expression'))),
    ])
})



FilterType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'), SpatialOpsType, abstract=pyxb.binding.datatypes.boolean(1), scope=FilterType))

FilterType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'), ComparisonOpsType, abstract=pyxb.binding.datatypes.boolean(1), scope=FilterType))

FilterType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Id'), AbstractIdType, abstract=pyxb.binding.datatypes.boolean(1), scope=FilterType))

FilterType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'logicOps'), LogicOpsType, abstract=pyxb.binding.datatypes.boolean(1), scope=FilterType))
FilterType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=FilterType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialOps'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=FilterType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_Id'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=FilterType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'logicOps'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=FilterType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'comparisonOps'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=FilterType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_Id'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



FunctionNamesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FunctionName'), FunctionNameType, scope=FunctionNamesType))
FunctionNamesType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=FunctionNamesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FunctionName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=FunctionNamesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FunctionName'))),
    ])
})



SpatialOperatorsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SpatialOperator'), SpatialOperatorType, scope=SpatialOperatorsType))
SpatialOperatorsType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpatialOperatorsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SpatialOperator'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SpatialOperatorsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SpatialOperator'))),
    ])
})



SortByType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SortProperty'), SortPropertyType, scope=SortByType))
SortByType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SortByType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SortProperty'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SortByType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SortProperty'))),
    ])
})



UpperBoundaryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'expression'), ExpressionType, abstract=pyxb.binding.datatypes.boolean(1), scope=UpperBoundaryType))
UpperBoundaryType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=UpperBoundaryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'expression'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



PropertyIsBetweenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UpperBoundary'), UpperBoundaryType, scope=PropertyIsBetweenType))

PropertyIsBetweenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'expression'), ExpressionType, abstract=pyxb.binding.datatypes.boolean(1), scope=PropertyIsBetweenType))

PropertyIsBetweenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LowerBoundary'), LowerBoundaryType, scope=PropertyIsBetweenType))
PropertyIsBetweenType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PropertyIsBetweenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'expression'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PropertyIsBetweenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LowerBoundary'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PropertyIsBetweenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'UpperBoundary'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
    ])
})



ArithmeticOperatorsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Functions'), FunctionsType, scope=ArithmeticOperatorsType))

ArithmeticOperatorsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SimpleArithmetic'), CTD_ANON_2, scope=ArithmeticOperatorsType))
ArithmeticOperatorsType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ArithmeticOperatorsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SimpleArithmetic'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ArithmeticOperatorsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Functions'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ArithmeticOperatorsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SimpleArithmetic'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ArithmeticOperatorsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Functions'))),
    ])
})

And._setSubstitutionGroup(logicOps)

Touches._setSubstitutionGroup(spatialOps)

Not._setSubstitutionGroup(logicOps)

Literal._setSubstitutionGroup(expression)

FeatureId._setSubstitutionGroup(Id)

Add._setSubstitutionGroup(expression)

PropertyIsNull._setSubstitutionGroup(comparisonOps)

Equals._setSubstitutionGroup(spatialOps)

PropertyIsNotEqualTo._setSubstitutionGroup(comparisonOps)

Disjoint._setSubstitutionGroup(spatialOps)

Beyond._setSubstitutionGroup(spatialOps)

Sub._setSubstitutionGroup(expression)

PropertyIsGreaterThan._setSubstitutionGroup(comparisonOps)

PropertyIsEqualTo._setSubstitutionGroup(comparisonOps)

PropertyIsLessThan._setSubstitutionGroup(comparisonOps)

PropertyIsLike._setSubstitutionGroup(comparisonOps)

Contains._setSubstitutionGroup(spatialOps)

BBOX._setSubstitutionGroup(spatialOps)

Mul._setSubstitutionGroup(expression)

Function._setSubstitutionGroup(expression)

Within._setSubstitutionGroup(spatialOps)

PropertyIsGreaterThanOrEqualTo._setSubstitutionGroup(comparisonOps)

DWithin._setSubstitutionGroup(spatialOps)

Div._setSubstitutionGroup(expression)

Intersects._setSubstitutionGroup(spatialOps)

Overlaps._setSubstitutionGroup(spatialOps)

Or._setSubstitutionGroup(logicOps)

PropertyName._setSubstitutionGroup(expression)

GmlObjectId._setSubstitutionGroup(Id)

Crosses._setSubstitutionGroup(spatialOps)

PropertyIsLessThanOrEqualTo._setSubstitutionGroup(comparisonOps)

PropertyIsBetween._setSubstitutionGroup(comparisonOps)
