# ./pyxb/bundles/opengis/raw/_nsgroup_.py
# PyXB bindings for NamespaceGroupModule
# NGM:d16379a067651cb41378191b4775061fa96b7ead
# Incorporated namespaces:
#  http://www.w3.org/2001/SMIL20/ smil20
#  http://www.w3.org/2001/SMIL20/Language smil20lang

import pyxb
import pyxb.binding
import pyxb.utils.utility

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:d19fe820-de0d-11de-8fc5-001cc05930fc')

# Import bindings for schemas in group
import pyxb.binding.datatypes
import pyxb.binding.xml_

_Namespace_smil20 = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/SMIL20/', create_if_missing=True)
_Namespace_smil20.configureCategories(['typeBinding', 'elementBinding'])
_Namespace_smil20lang = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/SMIL20/Language', create_if_missing=True)
_Namespace_smil20lang.configureCategories(['typeBinding', 'elementBinding'])

# Atomic SimpleTypeDefinition
class STD_ANON_1 (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_1._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_1, enum_prefix=None)
STD_ANON_1.discrete = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'discrete')
STD_ANON_1.linear = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'linear')
STD_ANON_1.paced = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'paced')
STD_ANON_1._InitializeFacetMap(STD_ANON_1._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_2 (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_2._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_2, enum_prefix=None)
STD_ANON_2.none = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'none')
STD_ANON_2.sum = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'sum')
STD_ANON_2._InitializeFacetMap(STD_ANON_2._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_3 (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_3._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_3, enum_prefix=None)
STD_ANON_3.replace = STD_ANON_3._CF_enumeration.addEnumeration(unicode_value=u'replace')
STD_ANON_3.sum = STD_ANON_3._CF_enumeration.addEnumeration(unicode_value=u'sum')
STD_ANON_3._InitializeFacetMap(STD_ANON_3._CF_enumeration)

# Atomic SimpleTypeDefinition
class fillDefaultType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'fillDefaultType')
    _Documentation = None
fillDefaultType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=fillDefaultType, enum_prefix=None)
fillDefaultType.remove = fillDefaultType._CF_enumeration.addEnumeration(unicode_value=u'remove')
fillDefaultType.freeze = fillDefaultType._CF_enumeration.addEnumeration(unicode_value=u'freeze')
fillDefaultType.hold = fillDefaultType._CF_enumeration.addEnumeration(unicode_value=u'hold')
fillDefaultType.auto = fillDefaultType._CF_enumeration.addEnumeration(unicode_value=u'auto')
fillDefaultType.inherit = fillDefaultType._CF_enumeration.addEnumeration(unicode_value=u'inherit')
fillDefaultType.transition = fillDefaultType._CF_enumeration.addEnumeration(unicode_value=u'transition')
fillDefaultType._InitializeFacetMap(fillDefaultType._CF_enumeration)
_Namespace_smil20.addCategoryObject('typeBinding', u'fillDefaultType', fillDefaultType)

# Atomic SimpleTypeDefinition
class restartTimingType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'restartTimingType')
    _Documentation = None
restartTimingType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=restartTimingType, enum_prefix=None)
restartTimingType.never = restartTimingType._CF_enumeration.addEnumeration(unicode_value=u'never')
restartTimingType.always = restartTimingType._CF_enumeration.addEnumeration(unicode_value=u'always')
restartTimingType.whenNotActive = restartTimingType._CF_enumeration.addEnumeration(unicode_value=u'whenNotActive')
restartTimingType.default = restartTimingType._CF_enumeration.addEnumeration(unicode_value=u'default')
restartTimingType._InitializeFacetMap(restartTimingType._CF_enumeration)
_Namespace_smil20.addCategoryObject('typeBinding', u'restartTimingType', restartTimingType)

# Atomic SimpleTypeDefinition
class syncBehaviorDefaultType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'syncBehaviorDefaultType')
    _Documentation = None
syncBehaviorDefaultType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=syncBehaviorDefaultType, enum_prefix=None)
syncBehaviorDefaultType.canSlip = syncBehaviorDefaultType._CF_enumeration.addEnumeration(unicode_value=u'canSlip')
syncBehaviorDefaultType.locked = syncBehaviorDefaultType._CF_enumeration.addEnumeration(unicode_value=u'locked')
syncBehaviorDefaultType.independent = syncBehaviorDefaultType._CF_enumeration.addEnumeration(unicode_value=u'independent')
syncBehaviorDefaultType.inherit = syncBehaviorDefaultType._CF_enumeration.addEnumeration(unicode_value=u'inherit')
syncBehaviorDefaultType._InitializeFacetMap(syncBehaviorDefaultType._CF_enumeration)
_Namespace_smil20.addCategoryObject('typeBinding', u'syncBehaviorDefaultType', syncBehaviorDefaultType)

# Atomic SimpleTypeDefinition
class syncBehaviorType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'syncBehaviorType')
    _Documentation = None
syncBehaviorType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=syncBehaviorType, enum_prefix=None)
syncBehaviorType.canSlip = syncBehaviorType._CF_enumeration.addEnumeration(unicode_value=u'canSlip')
syncBehaviorType.locked = syncBehaviorType._CF_enumeration.addEnumeration(unicode_value=u'locked')
syncBehaviorType.independent = syncBehaviorType._CF_enumeration.addEnumeration(unicode_value=u'independent')
syncBehaviorType.default = syncBehaviorType._CF_enumeration.addEnumeration(unicode_value=u'default')
syncBehaviorType._InitializeFacetMap(syncBehaviorType._CF_enumeration)
_Namespace_smil20.addCategoryObject('typeBinding', u'syncBehaviorType', syncBehaviorType)

# Atomic SimpleTypeDefinition
class restartDefaultType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'restartDefaultType')
    _Documentation = None
restartDefaultType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=restartDefaultType, enum_prefix=None)
restartDefaultType.never = restartDefaultType._CF_enumeration.addEnumeration(unicode_value=u'never')
restartDefaultType.always = restartDefaultType._CF_enumeration.addEnumeration(unicode_value=u'always')
restartDefaultType.whenNotActive = restartDefaultType._CF_enumeration.addEnumeration(unicode_value=u'whenNotActive')
restartDefaultType.inherit = restartDefaultType._CF_enumeration.addEnumeration(unicode_value=u'inherit')
restartDefaultType._InitializeFacetMap(restartDefaultType._CF_enumeration)
_Namespace_smil20.addCategoryObject('typeBinding', u'restartDefaultType', restartDefaultType)

# Atomic SimpleTypeDefinition
class fillTimingAttrsType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'fillTimingAttrsType')
    _Documentation = None
fillTimingAttrsType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=fillTimingAttrsType, enum_prefix=None)
fillTimingAttrsType.remove = fillTimingAttrsType._CF_enumeration.addEnumeration(unicode_value=u'remove')
fillTimingAttrsType.freeze = fillTimingAttrsType._CF_enumeration.addEnumeration(unicode_value=u'freeze')
fillTimingAttrsType.hold = fillTimingAttrsType._CF_enumeration.addEnumeration(unicode_value=u'hold')
fillTimingAttrsType.auto = fillTimingAttrsType._CF_enumeration.addEnumeration(unicode_value=u'auto')
fillTimingAttrsType.default = fillTimingAttrsType._CF_enumeration.addEnumeration(unicode_value=u'default')
fillTimingAttrsType.transition = fillTimingAttrsType._CF_enumeration.addEnumeration(unicode_value=u'transition')
fillTimingAttrsType._InitializeFacetMap(fillTimingAttrsType._CF_enumeration)
_Namespace_smil20.addCategoryObject('typeBinding', u'fillTimingAttrsType', fillTimingAttrsType)

# Atomic SimpleTypeDefinition
class STD_ANON_4 (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_4._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_4, enum_prefix=None)
STD_ANON_4.XML = STD_ANON_4._CF_enumeration.addEnumeration(unicode_value=u'XML')
STD_ANON_4.CSS = STD_ANON_4._CF_enumeration.addEnumeration(unicode_value=u'CSS')
STD_ANON_4.auto = STD_ANON_4._CF_enumeration.addEnumeration(unicode_value=u'auto')
STD_ANON_4._InitializeFacetMap(STD_ANON_4._CF_enumeration)

# Atomic SimpleTypeDefinition
class nonNegativeDecimalType (pyxb.binding.datatypes.decimal):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'nonNegativeDecimalType')
    _Documentation = None
nonNegativeDecimalType._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=nonNegativeDecimalType, value=pyxb.binding.datatypes.decimal(0.0))
nonNegativeDecimalType._InitializeFacetMap(nonNegativeDecimalType._CF_minInclusive)
_Namespace_smil20.addCategoryObject('typeBinding', u'nonNegativeDecimalType', nonNegativeDecimalType)

# Complex type animateMotionPrototype with content type EMPTY
class animateMotionPrototype (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'animateMotionPrototype')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute additive uses Python identifier additive
    __additive = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'additive'), 'additive', '__httpwww_w3_org2001SMIL20_animateMotionPrototype_additive', STD_ANON_3, unicode_default=u'replace')
    
    additive = property(__additive.value, __additive.set, None, None)

    
    # Attribute by uses Python identifier by
    __by = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'by'), 'by', '__httpwww_w3_org2001SMIL20_animateMotionPrototype_by', pyxb.binding.datatypes.string)
    
    by = property(__by.value, __by.set, None, None)

    
    # Attribute accumulate uses Python identifier accumulate
    __accumulate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'accumulate'), 'accumulate', '__httpwww_w3_org2001SMIL20_animateMotionPrototype_accumulate', STD_ANON_2, unicode_default=u'none')
    
    accumulate = property(__accumulate.value, __accumulate.set, None, None)

    
    # Attribute origin uses Python identifier origin
    __origin = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'origin'), 'origin', '__httpwww_w3_org2001SMIL20_animateMotionPrototype_origin', pyxb.binding.datatypes.string)
    
    origin = property(__origin.value, __origin.set, None, None)

    
    # Attribute to uses Python identifier to
    __to = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'to'), 'to', '__httpwww_w3_org2001SMIL20_animateMotionPrototype_to', pyxb.binding.datatypes.string)
    
    to = property(__to.value, __to.set, None, None)

    
    # Attribute from uses Python identifier from_
    __from = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'from'), 'from_', '__httpwww_w3_org2001SMIL20_animateMotionPrototype_from', pyxb.binding.datatypes.string)
    
    from_ = property(__from.value, __from.set, None, None)

    
    # Attribute values uses Python identifier values
    __values = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'values'), 'values', '__httpwww_w3_org2001SMIL20_animateMotionPrototype_values', pyxb.binding.datatypes.string)
    
    values = property(__values.value, __values.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __additive.name() : __additive,
        __by.name() : __by,
        __accumulate.name() : __accumulate,
        __origin.name() : __origin,
        __to.name() : __to,
        __from.name() : __from,
        __values.name() : __values
    }
_Namespace_smil20.addCategoryObject('typeBinding', u'animateMotionPrototype', animateMotionPrototype)


# Complex type animateMotionType with content type ELEMENT_ONLY
class animateMotionType (animateMotionPrototype):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20lang, u'animateMotionType')
    # Base type is animateMotionPrototype
    
    # Attribute by inherited from {http://www.w3.org/2001/SMIL20/}animateMotionPrototype
    
    # Attribute calcMode uses Python identifier calcMode
    __calcMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'calcMode'), 'calcMode', '__httpwww_w3_org2001SMIL20Language_animateMotionType_calcMode', STD_ANON_1, unicode_default=u'linear')
    
    calcMode = property(__calcMode.value, __calcMode.set, None, None)

    
    # Attribute accumulate inherited from {http://www.w3.org/2001/SMIL20/}animateMotionPrototype
    
    # Attribute class uses Python identifier class_
    __class = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'class'), 'class_', '__httpwww_w3_org2001SMIL20Language_animateMotionType_class', pyxb.binding.datatypes.string)
    
    class_ = property(__class.value, __class.set, None, None)

    
    # Attribute longdesc uses Python identifier longdesc
    __longdesc = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'longdesc'), 'longdesc', '__httpwww_w3_org2001SMIL20Language_animateMotionType_longdesc', pyxb.binding.datatypes.anyURI)
    
    longdesc = property(__longdesc.value, __longdesc.set, None, None)

    
    # Attribute fillDefault uses Python identifier fillDefault
    __fillDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'fillDefault'), 'fillDefault', '__httpwww_w3_org2001SMIL20Language_animateMotionType_fillDefault', fillDefaultType, unicode_default=u'inherit')
    
    fillDefault = property(__fillDefault.value, __fillDefault.set, None, None)

    
    # Attribute restart uses Python identifier restart
    __restart = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'restart'), 'restart', '__httpwww_w3_org2001SMIL20Language_animateMotionType_restart', restartTimingType, unicode_default=u'default')
    
    restart = property(__restart.value, __restart.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_w3_org2001SMIL20Language_animateMotionType_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute origin inherited from {http://www.w3.org/2001/SMIL20/}animateMotionPrototype
    
    # Attribute syncBehavior uses Python identifier syncBehavior
    __syncBehavior = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncBehavior'), 'syncBehavior', '__httpwww_w3_org2001SMIL20Language_animateMotionType_syncBehavior', syncBehaviorType, unicode_default=u'default')
    
    syncBehavior = property(__syncBehavior.value, __syncBehavior.set, None, None)

    
    # Attribute syncTolerance uses Python identifier syncTolerance
    __syncTolerance = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncTolerance'), 'syncTolerance', '__httpwww_w3_org2001SMIL20Language_animateMotionType_syncTolerance', pyxb.binding.datatypes.string)
    
    syncTolerance = property(__syncTolerance.value, __syncTolerance.set, None, None)

    
    # Attribute fill uses Python identifier fill
    __fill = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'fill'), 'fill', '__httpwww_w3_org2001SMIL20Language_animateMotionType_fill', fillTimingAttrsType, unicode_default=u'default')
    
    fill = property(__fill.value, __fill.set, None, None)

    
    # Attribute syncBehaviorDefault uses Python identifier syncBehaviorDefault
    __syncBehaviorDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncBehaviorDefault'), 'syncBehaviorDefault', '__httpwww_w3_org2001SMIL20Language_animateMotionType_syncBehaviorDefault', syncBehaviorDefaultType, unicode_default=u'inherit')
    
    syncBehaviorDefault = property(__syncBehaviorDefault.value, __syncBehaviorDefault.set, None, None)

    
    # Attribute syncToleranceDefault uses Python identifier syncToleranceDefault
    __syncToleranceDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncToleranceDefault'), 'syncToleranceDefault', '__httpwww_w3_org2001SMIL20Language_animateMotionType_syncToleranceDefault', pyxb.binding.datatypes.string, unicode_default=u'inherit')
    
    syncToleranceDefault = property(__syncToleranceDefault.value, __syncToleranceDefault.set, None, None)

    
    # Attribute {http://www.w3.org/XML/1998/namespace}lang uses Python identifier lang
    __lang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.XML, 'lang'), 'lang', '__httpwww_w3_org2001SMIL20Language_animateMotionType_httpwww_w3_orgXML1998namespacelang', pyxb.binding.xml_.STD_ANON_lang)
    
    lang = property(__lang.value, __lang.set, None, u'In due course, we should install the relevant ISO 2- and 3-letter\n                codes as the enumerated possible values . . .')

    
    # Attribute alt uses Python identifier alt
    __alt = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'alt'), 'alt', '__httpwww_w3_org2001SMIL20Language_animateMotionType_alt', pyxb.binding.datatypes.string)
    
    alt = property(__alt.value, __alt.set, None, None)

    
    # Attribute additive inherited from {http://www.w3.org/2001/SMIL20/}animateMotionPrototype
    
    # Attribute skip-content uses Python identifier skip_content
    __skip_content = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'skip-content'), 'skip_content', '__httpwww_w3_org2001SMIL20Language_animateMotionType_skip_content', pyxb.binding.datatypes.boolean, unicode_default=u'true')
    
    skip_content = property(__skip_content.value, __skip_content.set, None, None)

    
    # Attribute to inherited from {http://www.w3.org/2001/SMIL20/}animateMotionPrototype
    
    # Attribute restartDefault uses Python identifier restartDefault
    __restartDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'restartDefault'), 'restartDefault', '__httpwww_w3_org2001SMIL20Language_animateMotionType_restartDefault', restartDefaultType, unicode_default=u'inherit')
    
    restartDefault = property(__restartDefault.value, __restartDefault.set, None, None)

    
    # Attribute from_ inherited from {http://www.w3.org/2001/SMIL20/}animateMotionPrototype
    
    # Attribute targetElement uses Python identifier targetElement
    __targetElement = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetElement'), 'targetElement', '__httpwww_w3_org2001SMIL20Language_animateMotionType_targetElement', pyxb.binding.datatypes.IDREF)
    
    targetElement = property(__targetElement.value, __targetElement.set, None, None)

    
    # Attribute values inherited from {http://www.w3.org/2001/SMIL20/}animateMotionPrototype
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = animateMotionPrototype._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = animateMotionPrototype._AttributeMap.copy()
    _AttributeMap.update({
        __calcMode.name() : __calcMode,
        __class.name() : __class,
        __longdesc.name() : __longdesc,
        __fillDefault.name() : __fillDefault,
        __restart.name() : __restart,
        __id.name() : __id,
        __syncBehavior.name() : __syncBehavior,
        __syncTolerance.name() : __syncTolerance,
        __fill.name() : __fill,
        __syncBehaviorDefault.name() : __syncBehaviorDefault,
        __syncToleranceDefault.name() : __syncToleranceDefault,
        __lang.name() : __lang,
        __alt.name() : __alt,
        __skip_content.name() : __skip_content,
        __restartDefault.name() : __restartDefault,
        __targetElement.name() : __targetElement
    })
_Namespace_smil20lang.addCategoryObject('typeBinding', u'animateMotionType', animateMotionType)


# Complex type animateColorPrototype with content type EMPTY
class animateColorPrototype (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'animateColorPrototype')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute attributeName uses Python identifier attributeName
    __attributeName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'attributeName'), 'attributeName', '__httpwww_w3_org2001SMIL20_animateColorPrototype_attributeName', pyxb.binding.datatypes.string, required=True)
    
    attributeName = property(__attributeName.value, __attributeName.set, None, None)

    
    # Attribute values uses Python identifier values
    __values = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'values'), 'values', '__httpwww_w3_org2001SMIL20_animateColorPrototype_values', pyxb.binding.datatypes.string)
    
    values = property(__values.value, __values.set, None, None)

    
    # Attribute attributeType uses Python identifier attributeType
    __attributeType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'attributeType'), 'attributeType', '__httpwww_w3_org2001SMIL20_animateColorPrototype_attributeType', STD_ANON_4, unicode_default=u'auto')
    
    attributeType = property(__attributeType.value, __attributeType.set, None, None)

    
    # Attribute to uses Python identifier to
    __to = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'to'), 'to', '__httpwww_w3_org2001SMIL20_animateColorPrototype_to', pyxb.binding.datatypes.string)
    
    to = property(__to.value, __to.set, None, None)

    
    # Attribute from uses Python identifier from_
    __from = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'from'), 'from_', '__httpwww_w3_org2001SMIL20_animateColorPrototype_from', pyxb.binding.datatypes.string)
    
    from_ = property(__from.value, __from.set, None, None)

    
    # Attribute by uses Python identifier by
    __by = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'by'), 'by', '__httpwww_w3_org2001SMIL20_animateColorPrototype_by', pyxb.binding.datatypes.string)
    
    by = property(__by.value, __by.set, None, None)

    
    # Attribute additive uses Python identifier additive
    __additive = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'additive'), 'additive', '__httpwww_w3_org2001SMIL20_animateColorPrototype_additive', STD_ANON_3, unicode_default=u'replace')
    
    additive = property(__additive.value, __additive.set, None, None)

    
    # Attribute accumulate uses Python identifier accumulate
    __accumulate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'accumulate'), 'accumulate', '__httpwww_w3_org2001SMIL20_animateColorPrototype_accumulate', STD_ANON_2, unicode_default=u'none')
    
    accumulate = property(__accumulate.value, __accumulate.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __attributeName.name() : __attributeName,
        __values.name() : __values,
        __attributeType.name() : __attributeType,
        __to.name() : __to,
        __from.name() : __from,
        __by.name() : __by,
        __additive.name() : __additive,
        __accumulate.name() : __accumulate
    }
_Namespace_smil20.addCategoryObject('typeBinding', u'animateColorPrototype', animateColorPrototype)


# Complex type animateColorType with content type ELEMENT_ONLY
class animateColorType (animateColorPrototype):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20lang, u'animateColorType')
    # Base type is animateColorPrototype
    
    # Attribute restart uses Python identifier restart
    __restart = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'restart'), 'restart', '__httpwww_w3_org2001SMIL20Language_animateColorType_restart', restartTimingType, unicode_default=u'default')
    
    restart = property(__restart.value, __restart.set, None, None)

    
    # Attribute syncBehaviorDefault uses Python identifier syncBehaviorDefault
    __syncBehaviorDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncBehaviorDefault'), 'syncBehaviorDefault', '__httpwww_w3_org2001SMIL20Language_animateColorType_syncBehaviorDefault', syncBehaviorDefaultType, unicode_default=u'inherit')
    
    syncBehaviorDefault = property(__syncBehaviorDefault.value, __syncBehaviorDefault.set, None, None)

    
    # Attribute by inherited from {http://www.w3.org/2001/SMIL20/}animateColorPrototype
    
    # Attribute syncBehavior uses Python identifier syncBehavior
    __syncBehavior = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncBehavior'), 'syncBehavior', '__httpwww_w3_org2001SMIL20Language_animateColorType_syncBehavior', syncBehaviorType, unicode_default=u'default')
    
    syncBehavior = property(__syncBehavior.value, __syncBehavior.set, None, None)

    
    # Attribute syncTolerance uses Python identifier syncTolerance
    __syncTolerance = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncTolerance'), 'syncTolerance', '__httpwww_w3_org2001SMIL20Language_animateColorType_syncTolerance', pyxb.binding.datatypes.string)
    
    syncTolerance = property(__syncTolerance.value, __syncTolerance.set, None, None)

    
    # Attribute values inherited from {http://www.w3.org/2001/SMIL20/}animateColorPrototype
    
    # Attribute to inherited from {http://www.w3.org/2001/SMIL20/}animateColorPrototype
    
    # Attribute additive inherited from {http://www.w3.org/2001/SMIL20/}animateColorPrototype
    
    # Attribute accumulate inherited from {http://www.w3.org/2001/SMIL20/}animateColorPrototype
    
    # Attribute {http://www.w3.org/XML/1998/namespace}lang uses Python identifier lang
    __lang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.XML, 'lang'), 'lang', '__httpwww_w3_org2001SMIL20Language_animateColorType_httpwww_w3_orgXML1998namespacelang', pyxb.binding.xml_.STD_ANON_lang)
    
    lang = property(__lang.value, __lang.set, None, u'In due course, we should install the relevant ISO 2- and 3-letter\n                codes as the enumerated possible values . . .')

    
    # Attribute restartDefault uses Python identifier restartDefault
    __restartDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'restartDefault'), 'restartDefault', '__httpwww_w3_org2001SMIL20Language_animateColorType_restartDefault', restartDefaultType, unicode_default=u'inherit')
    
    restartDefault = property(__restartDefault.value, __restartDefault.set, None, None)

    
    # Attribute fill uses Python identifier fill
    __fill = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'fill'), 'fill', '__httpwww_w3_org2001SMIL20Language_animateColorType_fill', fillTimingAttrsType, unicode_default=u'default')
    
    fill = property(__fill.value, __fill.set, None, None)

    
    # Attribute skip-content uses Python identifier skip_content
    __skip_content = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'skip-content'), 'skip_content', '__httpwww_w3_org2001SMIL20Language_animateColorType_skip_content', pyxb.binding.datatypes.boolean, unicode_default=u'true')
    
    skip_content = property(__skip_content.value, __skip_content.set, None, None)

    
    # Attribute attributeType inherited from {http://www.w3.org/2001/SMIL20/}animateColorPrototype
    
    # Attribute targetElement uses Python identifier targetElement
    __targetElement = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetElement'), 'targetElement', '__httpwww_w3_org2001SMIL20Language_animateColorType_targetElement', pyxb.binding.datatypes.IDREF)
    
    targetElement = property(__targetElement.value, __targetElement.set, None, None)

    
    # Attribute attributeName inherited from {http://www.w3.org/2001/SMIL20/}animateColorPrototype
    
    # Attribute syncToleranceDefault uses Python identifier syncToleranceDefault
    __syncToleranceDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncToleranceDefault'), 'syncToleranceDefault', '__httpwww_w3_org2001SMIL20Language_animateColorType_syncToleranceDefault', pyxb.binding.datatypes.string, unicode_default=u'inherit')
    
    syncToleranceDefault = property(__syncToleranceDefault.value, __syncToleranceDefault.set, None, None)

    
    # Attribute from_ inherited from {http://www.w3.org/2001/SMIL20/}animateColorPrototype
    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_w3_org2001SMIL20Language_animateColorType_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute alt uses Python identifier alt
    __alt = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'alt'), 'alt', '__httpwww_w3_org2001SMIL20Language_animateColorType_alt', pyxb.binding.datatypes.string)
    
    alt = property(__alt.value, __alt.set, None, None)

    
    # Attribute longdesc uses Python identifier longdesc
    __longdesc = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'longdesc'), 'longdesc', '__httpwww_w3_org2001SMIL20Language_animateColorType_longdesc', pyxb.binding.datatypes.anyURI)
    
    longdesc = property(__longdesc.value, __longdesc.set, None, None)

    
    # Attribute calcMode uses Python identifier calcMode
    __calcMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'calcMode'), 'calcMode', '__httpwww_w3_org2001SMIL20Language_animateColorType_calcMode', STD_ANON_1, unicode_default=u'linear')
    
    calcMode = property(__calcMode.value, __calcMode.set, None, None)

    
    # Attribute class uses Python identifier class_
    __class = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'class'), 'class_', '__httpwww_w3_org2001SMIL20Language_animateColorType_class', pyxb.binding.datatypes.string)
    
    class_ = property(__class.value, __class.set, None, None)

    
    # Attribute fillDefault uses Python identifier fillDefault
    __fillDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'fillDefault'), 'fillDefault', '__httpwww_w3_org2001SMIL20Language_animateColorType_fillDefault', fillDefaultType, unicode_default=u'inherit')
    
    fillDefault = property(__fillDefault.value, __fillDefault.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = animateColorPrototype._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = animateColorPrototype._AttributeMap.copy()
    _AttributeMap.update({
        __restart.name() : __restart,
        __syncBehaviorDefault.name() : __syncBehaviorDefault,
        __syncBehavior.name() : __syncBehavior,
        __syncTolerance.name() : __syncTolerance,
        __lang.name() : __lang,
        __restartDefault.name() : __restartDefault,
        __fill.name() : __fill,
        __skip_content.name() : __skip_content,
        __targetElement.name() : __targetElement,
        __syncToleranceDefault.name() : __syncToleranceDefault,
        __id.name() : __id,
        __alt.name() : __alt,
        __longdesc.name() : __longdesc,
        __calcMode.name() : __calcMode,
        __class.name() : __class,
        __fillDefault.name() : __fillDefault
    })
_Namespace_smil20lang.addCategoryObject('typeBinding', u'animateColorType', animateColorType)


# Complex type setPrototype with content type EMPTY
class setPrototype (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'setPrototype')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute to uses Python identifier to
    __to = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'to'), 'to', '__httpwww_w3_org2001SMIL20_setPrototype_to', pyxb.binding.datatypes.string)
    
    to = property(__to.value, __to.set, None, None)

    
    # Attribute attributeName uses Python identifier attributeName
    __attributeName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'attributeName'), 'attributeName', '__httpwww_w3_org2001SMIL20_setPrototype_attributeName', pyxb.binding.datatypes.string, required=True)
    
    attributeName = property(__attributeName.value, __attributeName.set, None, None)

    
    # Attribute attributeType uses Python identifier attributeType
    __attributeType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'attributeType'), 'attributeType', '__httpwww_w3_org2001SMIL20_setPrototype_attributeType', STD_ANON_4, unicode_default=u'auto')
    
    attributeType = property(__attributeType.value, __attributeType.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __to.name() : __to,
        __attributeName.name() : __attributeName,
        __attributeType.name() : __attributeType
    }
_Namespace_smil20.addCategoryObject('typeBinding', u'setPrototype', setPrototype)


# Complex type setType with content type ELEMENT_ONLY
class setType (setPrototype):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20lang, u'setType')
    # Base type is setPrototype
    
    # Attribute attributeType inherited from {http://www.w3.org/2001/SMIL20/}setPrototype
    
    # Attribute syncTolerance uses Python identifier syncTolerance
    __syncTolerance = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncTolerance'), 'syncTolerance', '__httpwww_w3_org2001SMIL20Language_setType_syncTolerance', pyxb.binding.datatypes.string)
    
    syncTolerance = property(__syncTolerance.value, __syncTolerance.set, None, None)

    
    # Attribute fill uses Python identifier fill
    __fill = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'fill'), 'fill', '__httpwww_w3_org2001SMIL20Language_setType_fill', fillTimingAttrsType, unicode_default=u'default')
    
    fill = property(__fill.value, __fill.set, None, None)

    
    # Attribute syncToleranceDefault uses Python identifier syncToleranceDefault
    __syncToleranceDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncToleranceDefault'), 'syncToleranceDefault', '__httpwww_w3_org2001SMIL20Language_setType_syncToleranceDefault', pyxb.binding.datatypes.string, unicode_default=u'inherit')
    
    syncToleranceDefault = property(__syncToleranceDefault.value, __syncToleranceDefault.set, None, None)

    
    # Attribute attributeName inherited from {http://www.w3.org/2001/SMIL20/}setPrototype
    
    # Attribute alt uses Python identifier alt
    __alt = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'alt'), 'alt', '__httpwww_w3_org2001SMIL20Language_setType_alt', pyxb.binding.datatypes.string)
    
    alt = property(__alt.value, __alt.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_w3_org2001SMIL20Language_setType_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute targetElement uses Python identifier targetElement
    __targetElement = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetElement'), 'targetElement', '__httpwww_w3_org2001SMIL20Language_setType_targetElement', pyxb.binding.datatypes.IDREF)
    
    targetElement = property(__targetElement.value, __targetElement.set, None, None)

    
    # Attribute syncBehaviorDefault uses Python identifier syncBehaviorDefault
    __syncBehaviorDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncBehaviorDefault'), 'syncBehaviorDefault', '__httpwww_w3_org2001SMIL20Language_setType_syncBehaviorDefault', syncBehaviorDefaultType, unicode_default=u'inherit')
    
    syncBehaviorDefault = property(__syncBehaviorDefault.value, __syncBehaviorDefault.set, None, None)

    
    # Attribute {http://www.w3.org/XML/1998/namespace}lang uses Python identifier lang
    __lang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.XML, 'lang'), 'lang', '__httpwww_w3_org2001SMIL20Language_setType_httpwww_w3_orgXML1998namespacelang', pyxb.binding.xml_.STD_ANON_lang)
    
    lang = property(__lang.value, __lang.set, None, u'In due course, we should install the relevant ISO 2- and 3-letter\n                codes as the enumerated possible values . . .')

    
    # Attribute fillDefault uses Python identifier fillDefault
    __fillDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'fillDefault'), 'fillDefault', '__httpwww_w3_org2001SMIL20Language_setType_fillDefault', fillDefaultType, unicode_default=u'inherit')
    
    fillDefault = property(__fillDefault.value, __fillDefault.set, None, None)

    
    # Attribute syncBehavior uses Python identifier syncBehavior
    __syncBehavior = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncBehavior'), 'syncBehavior', '__httpwww_w3_org2001SMIL20Language_setType_syncBehavior', syncBehaviorType, unicode_default=u'default')
    
    syncBehavior = property(__syncBehavior.value, __syncBehavior.set, None, None)

    
    # Attribute longdesc uses Python identifier longdesc
    __longdesc = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'longdesc'), 'longdesc', '__httpwww_w3_org2001SMIL20Language_setType_longdesc', pyxb.binding.datatypes.anyURI)
    
    longdesc = property(__longdesc.value, __longdesc.set, None, None)

    
    # Attribute to inherited from {http://www.w3.org/2001/SMIL20/}setPrototype
    
    # Attribute restartDefault uses Python identifier restartDefault
    __restartDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'restartDefault'), 'restartDefault', '__httpwww_w3_org2001SMIL20Language_setType_restartDefault', restartDefaultType, unicode_default=u'inherit')
    
    restartDefault = property(__restartDefault.value, __restartDefault.set, None, None)

    
    # Attribute restart uses Python identifier restart
    __restart = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'restart'), 'restart', '__httpwww_w3_org2001SMIL20Language_setType_restart', restartTimingType, unicode_default=u'default')
    
    restart = property(__restart.value, __restart.set, None, None)

    
    # Attribute class uses Python identifier class_
    __class = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'class'), 'class_', '__httpwww_w3_org2001SMIL20Language_setType_class', pyxb.binding.datatypes.string)
    
    class_ = property(__class.value, __class.set, None, None)

    
    # Attribute skip-content uses Python identifier skip_content
    __skip_content = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'skip-content'), 'skip_content', '__httpwww_w3_org2001SMIL20Language_setType_skip_content', pyxb.binding.datatypes.boolean, unicode_default=u'true')
    
    skip_content = property(__skip_content.value, __skip_content.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = setPrototype._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = setPrototype._AttributeMap.copy()
    _AttributeMap.update({
        __syncTolerance.name() : __syncTolerance,
        __fill.name() : __fill,
        __syncToleranceDefault.name() : __syncToleranceDefault,
        __alt.name() : __alt,
        __id.name() : __id,
        __targetElement.name() : __targetElement,
        __syncBehaviorDefault.name() : __syncBehaviorDefault,
        __lang.name() : __lang,
        __fillDefault.name() : __fillDefault,
        __syncBehavior.name() : __syncBehavior,
        __longdesc.name() : __longdesc,
        __restartDefault.name() : __restartDefault,
        __restart.name() : __restart,
        __class.name() : __class,
        __skip_content.name() : __skip_content
    })
_Namespace_smil20lang.addCategoryObject('typeBinding', u'setType', setType)


# Complex type animatePrototype with content type EMPTY
class animatePrototype (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20, u'animatePrototype')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute attributeName uses Python identifier attributeName
    __attributeName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'attributeName'), 'attributeName', '__httpwww_w3_org2001SMIL20_animatePrototype_attributeName', pyxb.binding.datatypes.string, required=True)
    
    attributeName = property(__attributeName.value, __attributeName.set, None, None)

    
    # Attribute accumulate uses Python identifier accumulate
    __accumulate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'accumulate'), 'accumulate', '__httpwww_w3_org2001SMIL20_animatePrototype_accumulate', STD_ANON_2, unicode_default=u'none')
    
    accumulate = property(__accumulate.value, __accumulate.set, None, None)

    
    # Attribute values uses Python identifier values
    __values = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'values'), 'values', '__httpwww_w3_org2001SMIL20_animatePrototype_values', pyxb.binding.datatypes.string)
    
    values = property(__values.value, __values.set, None, None)

    
    # Attribute additive uses Python identifier additive
    __additive = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'additive'), 'additive', '__httpwww_w3_org2001SMIL20_animatePrototype_additive', STD_ANON_3, unicode_default=u'replace')
    
    additive = property(__additive.value, __additive.set, None, None)

    
    # Attribute to uses Python identifier to
    __to = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'to'), 'to', '__httpwww_w3_org2001SMIL20_animatePrototype_to', pyxb.binding.datatypes.string)
    
    to = property(__to.value, __to.set, None, None)

    
    # Attribute attributeType uses Python identifier attributeType
    __attributeType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'attributeType'), 'attributeType', '__httpwww_w3_org2001SMIL20_animatePrototype_attributeType', STD_ANON_4, unicode_default=u'auto')
    
    attributeType = property(__attributeType.value, __attributeType.set, None, None)

    
    # Attribute by uses Python identifier by
    __by = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'by'), 'by', '__httpwww_w3_org2001SMIL20_animatePrototype_by', pyxb.binding.datatypes.string)
    
    by = property(__by.value, __by.set, None, None)

    
    # Attribute from uses Python identifier from_
    __from = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'from'), 'from_', '__httpwww_w3_org2001SMIL20_animatePrototype_from', pyxb.binding.datatypes.string)
    
    from_ = property(__from.value, __from.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __attributeName.name() : __attributeName,
        __accumulate.name() : __accumulate,
        __values.name() : __values,
        __additive.name() : __additive,
        __to.name() : __to,
        __attributeType.name() : __attributeType,
        __by.name() : __by,
        __from.name() : __from
    }
_Namespace_smil20.addCategoryObject('typeBinding', u'animatePrototype', animatePrototype)


# Complex type animateType with content type ELEMENT_ONLY
class animateType (animatePrototype):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace_smil20lang, u'animateType')
    # Base type is animatePrototype
    
    # Attribute alt uses Python identifier alt
    __alt = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'alt'), 'alt', '__httpwww_w3_org2001SMIL20Language_animateType_alt', pyxb.binding.datatypes.string)
    
    alt = property(__alt.value, __alt.set, None, None)

    
    # Attribute additive inherited from {http://www.w3.org/2001/SMIL20/}animatePrototype
    
    # Attribute fill uses Python identifier fill
    __fill = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'fill'), 'fill', '__httpwww_w3_org2001SMIL20Language_animateType_fill', fillTimingAttrsType, unicode_default=u'default')
    
    fill = property(__fill.value, __fill.set, None, None)

    
    # Attribute {http://www.w3.org/XML/1998/namespace}lang uses Python identifier lang
    __lang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.XML, 'lang'), 'lang', '__httpwww_w3_org2001SMIL20Language_animateType_httpwww_w3_orgXML1998namespacelang', pyxb.binding.xml_.STD_ANON_lang)
    
    lang = property(__lang.value, __lang.set, None, u'In due course, we should install the relevant ISO 2- and 3-letter\n                codes as the enumerated possible values . . .')

    
    # Attribute from_ inherited from {http://www.w3.org/2001/SMIL20/}animatePrototype
    
    # Attribute attributeName inherited from {http://www.w3.org/2001/SMIL20/}animatePrototype
    
    # Attribute restartDefault uses Python identifier restartDefault
    __restartDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'restartDefault'), 'restartDefault', '__httpwww_w3_org2001SMIL20Language_animateType_restartDefault', restartDefaultType, unicode_default=u'inherit')
    
    restartDefault = property(__restartDefault.value, __restartDefault.set, None, None)

    
    # Attribute targetElement uses Python identifier targetElement
    __targetElement = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetElement'), 'targetElement', '__httpwww_w3_org2001SMIL20Language_animateType_targetElement', pyxb.binding.datatypes.IDREF)
    
    targetElement = property(__targetElement.value, __targetElement.set, None, None)

    
    # Attribute accumulate inherited from {http://www.w3.org/2001/SMIL20/}animatePrototype
    
    # Attribute to inherited from {http://www.w3.org/2001/SMIL20/}animatePrototype
    
    # Attribute values inherited from {http://www.w3.org/2001/SMIL20/}animatePrototype
    
    # Attribute calcMode uses Python identifier calcMode
    __calcMode = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'calcMode'), 'calcMode', '__httpwww_w3_org2001SMIL20Language_animateType_calcMode', STD_ANON_1, unicode_default=u'linear')
    
    calcMode = property(__calcMode.value, __calcMode.set, None, None)

    
    # Attribute class uses Python identifier class_
    __class = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'class'), 'class_', '__httpwww_w3_org2001SMIL20Language_animateType_class', pyxb.binding.datatypes.string)
    
    class_ = property(__class.value, __class.set, None, None)

    
    # Attribute longdesc uses Python identifier longdesc
    __longdesc = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'longdesc'), 'longdesc', '__httpwww_w3_org2001SMIL20Language_animateType_longdesc', pyxb.binding.datatypes.anyURI)
    
    longdesc = property(__longdesc.value, __longdesc.set, None, None)

    
    # Attribute fillDefault uses Python identifier fillDefault
    __fillDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'fillDefault'), 'fillDefault', '__httpwww_w3_org2001SMIL20Language_animateType_fillDefault', fillDefaultType, unicode_default=u'inherit')
    
    fillDefault = property(__fillDefault.value, __fillDefault.set, None, None)

    
    # Attribute skip-content uses Python identifier skip_content
    __skip_content = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'skip-content'), 'skip_content', '__httpwww_w3_org2001SMIL20Language_animateType_skip_content', pyxb.binding.datatypes.boolean, unicode_default=u'true')
    
    skip_content = property(__skip_content.value, __skip_content.set, None, None)

    
    # Attribute restart uses Python identifier restart
    __restart = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'restart'), 'restart', '__httpwww_w3_org2001SMIL20Language_animateType_restart', restartTimingType, unicode_default=u'default')
    
    restart = property(__restart.value, __restart.set, None, None)

    
    # Attribute syncBehavior uses Python identifier syncBehavior
    __syncBehavior = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncBehavior'), 'syncBehavior', '__httpwww_w3_org2001SMIL20Language_animateType_syncBehavior', syncBehaviorType, unicode_default=u'default')
    
    syncBehavior = property(__syncBehavior.value, __syncBehavior.set, None, None)

    
    # Attribute syncBehaviorDefault uses Python identifier syncBehaviorDefault
    __syncBehaviorDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncBehaviorDefault'), 'syncBehaviorDefault', '__httpwww_w3_org2001SMIL20Language_animateType_syncBehaviorDefault', syncBehaviorDefaultType, unicode_default=u'inherit')
    
    syncBehaviorDefault = property(__syncBehaviorDefault.value, __syncBehaviorDefault.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_w3_org2001SMIL20Language_animateType_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute attributeType inherited from {http://www.w3.org/2001/SMIL20/}animatePrototype
    
    # Attribute syncTolerance uses Python identifier syncTolerance
    __syncTolerance = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncTolerance'), 'syncTolerance', '__httpwww_w3_org2001SMIL20Language_animateType_syncTolerance', pyxb.binding.datatypes.string)
    
    syncTolerance = property(__syncTolerance.value, __syncTolerance.set, None, None)

    
    # Attribute syncToleranceDefault uses Python identifier syncToleranceDefault
    __syncToleranceDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'syncToleranceDefault'), 'syncToleranceDefault', '__httpwww_w3_org2001SMIL20Language_animateType_syncToleranceDefault', pyxb.binding.datatypes.string, unicode_default=u'inherit')
    
    syncToleranceDefault = property(__syncToleranceDefault.value, __syncToleranceDefault.set, None, None)

    
    # Attribute by inherited from {http://www.w3.org/2001/SMIL20/}animatePrototype
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = animatePrototype._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = animatePrototype._AttributeMap.copy()
    _AttributeMap.update({
        __alt.name() : __alt,
        __fill.name() : __fill,
        __lang.name() : __lang,
        __restartDefault.name() : __restartDefault,
        __targetElement.name() : __targetElement,
        __calcMode.name() : __calcMode,
        __class.name() : __class,
        __longdesc.name() : __longdesc,
        __fillDefault.name() : __fillDefault,
        __skip_content.name() : __skip_content,
        __restart.name() : __restart,
        __syncBehavior.name() : __syncBehavior,
        __syncBehaviorDefault.name() : __syncBehaviorDefault,
        __id.name() : __id,
        __syncTolerance.name() : __syncTolerance,
        __syncToleranceDefault.name() : __syncToleranceDefault
    })
_Namespace_smil20lang.addCategoryObject('typeBinding', u'animateType', animateType)


animateMotion = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_smil20lang, u'animateMotion'), animateMotionType)
_Namespace_smil20lang.addCategoryObject('elementBinding', animateMotion.name().localName(), animateMotion)

animateColor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_smil20, u'animateColor'), animateColorType)
_Namespace_smil20.addCategoryObject('elementBinding', animateColor.name().localName(), animateColor)

animateMotion_ = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_smil20, u'animateMotion'), animateMotionType)
_Namespace_smil20.addCategoryObject('elementBinding', animateMotion_.name().localName(), animateMotion_)

set = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_smil20lang, u'set'), setType)
_Namespace_smil20lang.addCategoryObject('elementBinding', set.name().localName(), set)

animateColor_ = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_smil20lang, u'animateColor'), animateColorType)
_Namespace_smil20lang.addCategoryObject('elementBinding', animateColor_.name().localName(), animateColor_)

set_ = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_smil20, u'set'), setType)
_Namespace_smil20.addCategoryObject('elementBinding', set_.name().localName(), set_)

animate = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_smil20, u'animate'), animateType)
_Namespace_smil20.addCategoryObject('elementBinding', animate.name().localName(), animate)

animate_ = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_smil20lang, u'animate'), animateType)
_Namespace_smil20lang.addCategoryObject('elementBinding', animate_.name().localName(), animate_)


animateMotionType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2001/SMIL20/Language'))),
    ])
})


animateColorType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2001/SMIL20/Language'))),
    ])
})


setType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2001/SMIL20/Language'))),
    ])
})


animateType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2001/SMIL20/Language'))),
    ])
})

animateColor._setSubstitutionGroup(animateColor_)

animateMotion_._setSubstitutionGroup(animateMotion)

set_._setSubstitutionGroup(set)

animate._setSubstitutionGroup(animate_)
