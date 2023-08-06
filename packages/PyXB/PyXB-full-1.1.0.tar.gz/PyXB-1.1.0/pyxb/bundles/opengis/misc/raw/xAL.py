# ./pyxb/bundles/opengis/misc/raw/xAL.py
# PyXB bindings for NamespaceModule
# NSM:28237b706ea7dd7f30e1bac6f6949d1f2f8264f7
# Generated 2009-11-30 18:08:59.271542 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:b8862732-de0d-11de-a7c4-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0', create_if_missing=True)
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
class STD_ANON_1 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_1._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_1, enum_prefix=None)
STD_ANON_1.Before = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_1.After = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_1._InitializeFacetMap(STD_ANON_1._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_2 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_2._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_2, enum_prefix=None)
STD_ANON_2.Single = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'Single')
STD_ANON_2.Range = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'Range')
STD_ANON_2._InitializeFacetMap(STD_ANON_2._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_3 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_3._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_3, enum_prefix=None)
STD_ANON_3.Before = STD_ANON_3._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_3.After = STD_ANON_3._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_3._InitializeFacetMap(STD_ANON_3._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_4 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_4._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_4, enum_prefix=None)
STD_ANON_4.Before = STD_ANON_4._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_4.After = STD_ANON_4._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_4._InitializeFacetMap(STD_ANON_4._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_5 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_5._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_5, enum_prefix=None)
STD_ANON_5.Before = STD_ANON_5._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_5.After = STD_ANON_5._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_5._InitializeFacetMap(STD_ANON_5._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_6 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_6._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_6, enum_prefix=None)
STD_ANON_6.Single = STD_ANON_6._CF_enumeration.addEnumeration(unicode_value=u'Single')
STD_ANON_6.Range = STD_ANON_6._CF_enumeration.addEnumeration(unicode_value=u'Range')
STD_ANON_6._InitializeFacetMap(STD_ANON_6._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_7 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_7._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_7, enum_prefix=None)
STD_ANON_7.BeforeName = STD_ANON_7._CF_enumeration.addEnumeration(unicode_value=u'BeforeName')
STD_ANON_7.AfterName = STD_ANON_7._CF_enumeration.addEnumeration(unicode_value=u'AfterName')
STD_ANON_7.BeforeType = STD_ANON_7._CF_enumeration.addEnumeration(unicode_value=u'BeforeType')
STD_ANON_7.AfterType = STD_ANON_7._CF_enumeration.addEnumeration(unicode_value=u'AfterType')
STD_ANON_7._InitializeFacetMap(STD_ANON_7._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_8 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_8._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_8, enum_prefix=None)
STD_ANON_8.Before = STD_ANON_8._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_8.After = STD_ANON_8._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_8._InitializeFacetMap(STD_ANON_8._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_9 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_9._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_9, enum_prefix=None)
STD_ANON_9.Before = STD_ANON_9._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_9.After = STD_ANON_9._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_9._InitializeFacetMap(STD_ANON_9._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_10 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_10._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_10, enum_prefix=None)
STD_ANON_10.BeforeName = STD_ANON_10._CF_enumeration.addEnumeration(unicode_value=u'BeforeName')
STD_ANON_10.AfterName = STD_ANON_10._CF_enumeration.addEnumeration(unicode_value=u'AfterName')
STD_ANON_10.BeforeType = STD_ANON_10._CF_enumeration.addEnumeration(unicode_value=u'BeforeType')
STD_ANON_10.AfterType = STD_ANON_10._CF_enumeration.addEnumeration(unicode_value=u'AfterType')
STD_ANON_10._InitializeFacetMap(STD_ANON_10._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_11 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_11._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_11, enum_prefix=None)
STD_ANON_11.Before = STD_ANON_11._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_11.After = STD_ANON_11._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_11._InitializeFacetMap(STD_ANON_11._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_12 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_12._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_12, enum_prefix=None)
STD_ANON_12.Before = STD_ANON_12._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_12.After = STD_ANON_12._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_12._InitializeFacetMap(STD_ANON_12._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_13 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_13._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_13, enum_prefix=None)
STD_ANON_13.Before = STD_ANON_13._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_13.After = STD_ANON_13._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_13._InitializeFacetMap(STD_ANON_13._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_14 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_14._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_14, enum_prefix=None)
STD_ANON_14.Before = STD_ANON_14._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_14.After = STD_ANON_14._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_14._InitializeFacetMap(STD_ANON_14._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_15 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_15._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_15, enum_prefix=None)
STD_ANON_15.Before = STD_ANON_15._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_15.After = STD_ANON_15._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_15._InitializeFacetMap(STD_ANON_15._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_16 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_16._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_16, enum_prefix=None)
STD_ANON_16.Yes = STD_ANON_16._CF_enumeration.addEnumeration(unicode_value=u'Yes')
STD_ANON_16.No = STD_ANON_16._CF_enumeration.addEnumeration(unicode_value=u'No')
STD_ANON_16._InitializeFacetMap(STD_ANON_16._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_17 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_17._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_17, enum_prefix=None)
STD_ANON_17.Before = STD_ANON_17._CF_enumeration.addEnumeration(unicode_value=u'Before')
STD_ANON_17.After = STD_ANON_17._CF_enumeration.addEnumeration(unicode_value=u'After')
STD_ANON_17._InitializeFacetMap(STD_ANON_17._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_18 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_18._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_18, enum_prefix=None)
STD_ANON_18.Odd = STD_ANON_18._CF_enumeration.addEnumeration(unicode_value=u'Odd')
STD_ANON_18.Even = STD_ANON_18._CF_enumeration.addEnumeration(unicode_value=u'Even')
STD_ANON_18._InitializeFacetMap(STD_ANON_18._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_19 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_19._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_19, enum_prefix=None)
STD_ANON_19.BeforeName = STD_ANON_19._CF_enumeration.addEnumeration(unicode_value=u'BeforeName')
STD_ANON_19.AfterName = STD_ANON_19._CF_enumeration.addEnumeration(unicode_value=u'AfterName')
STD_ANON_19.BeforeType = STD_ANON_19._CF_enumeration.addEnumeration(unicode_value=u'BeforeType')
STD_ANON_19.AfterType = STD_ANON_19._CF_enumeration.addEnumeration(unicode_value=u'AfterType')
STD_ANON_19._InitializeFacetMap(STD_ANON_19._CF_enumeration)

# Complex type CTD_ANON_1 with content type MIXED
class CTD_ANON_1 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_1_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_1_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_2 with content type MIXED
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberPrefixSeparator uses Python identifier NumberPrefixSeparator
    __NumberPrefixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberPrefixSeparator'), 'NumberPrefixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_2_NumberPrefixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberPrefixSeparator = property(__NumberPrefixSeparator.value, __NumberPrefixSeparator.set, None, u'A-12 where 12 is number and A is prefix and "-" is the separator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_2_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_2_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberPrefixSeparator.name() : __NumberPrefixSeparator,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type ThoroughfareNameType with content type MIXED
class ThoroughfareNameType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNameType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareNameType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareNameType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'ThoroughfareNameType', ThoroughfareNameType)


# Complex type CTD_ANON_3 with content type ELEMENT_ONLY
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DepartmentName uses Python identifier DepartmentName
    __DepartmentName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DepartmentName'), 'DepartmentName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0DepartmentName', True)

    
    DepartmentName = property(__DepartmentName.value, __DepartmentName.set, None, u'Specification of the name of a department.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStop uses Python identifier MailStop
    __MailStop = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), 'MailStop', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0MailStop', False)

    
    MailStop = property(__MailStop.value, __MailStop.set, None, u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'School in Physics School, Division in Radiology division of school of physics')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __DepartmentName.name() : __DepartmentName,
        __MailStop.name() : __MailStop,
        __PostalCode.name() : __PostalCode
    }
    _AttributeMap = {
        __Type.name() : __Type
    }



# Complex type CTD_ANON_4 with content type MIXED
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_4_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_5 with content type MIXED
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_5_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'MS in MS 62, # in MS # 12, etc.')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_5_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute IndicatorOccurrence uses Python identifier IndicatorOccurrence
    __IndicatorOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurrence'), 'IndicatorOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_5_IndicatorOccurrence', STD_ANON_1)
    
    IndicatorOccurrence = property(__IndicatorOccurrence.value, __IndicatorOccurrence.set, None, u'MS occurs before 62 in MS 62')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Indicator.name() : __Indicator,
        __Code.name() : __Code,
        __IndicatorOccurrence.name() : __IndicatorOccurrence
    }



# Complex type CTD_ANON_6 with content type ELEMENT_ONLY
class CTD_ANON_6 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_6_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCodeNumber uses Python identifier PostalCodeNumber
    __PostalCodeNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumber'), 'PostalCodeNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_6_urnoasisnamestcciqxsdschemaxAL2_0PostalCodeNumber', True)

    
    PostalCodeNumber = property(__PostalCodeNumber.value, __PostalCodeNumber.set, None, u'Specification of a postcode. The postcode is formatted according to country-specific rules. Example: SW3 0A8-1A, 600074, 2067')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCodeNumberExtension uses Python identifier PostalCodeNumberExtension
    __PostalCodeNumberExtension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumberExtension'), 'PostalCodeNumberExtension', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_6_urnoasisnamestcciqxsdschemaxAL2_0PostalCodeNumberExtension', True)

    
    PostalCodeNumberExtension = property(__PostalCodeNumberExtension.value, __PostalCodeNumberExtension.set, None, u'Examples are: 1234 (USA), 1G (UK), etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostTown uses Python identifier PostTown
    __PostTown = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostTown'), 'PostTown', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_6_urnoasisnamestcciqxsdschemaxAL2_0PostTown', False)

    
    PostTown = property(__PostTown.value, __PostTown.set, None, u'A post town is not the same as a locality. A post town can encompass a collection of (small) localities. It can also be a subpart of a locality. An actual post town in Norway is "Bergen".')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_6_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Area Code, Postcode, Delivery code as in NZ, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __PostalCodeNumber.name() : __PostalCodeNumber,
        __PostalCodeNumberExtension.name() : __PostalCodeNumberExtension,
        __PostTown.name() : __PostTown
    }
    _AttributeMap = {
        __Type.name() : __Type
    }



# Complex type CTD_ANON_7 with content type MIXED
class CTD_ANON_7 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_7_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute IndicatorOccurrence uses Python identifier IndicatorOccurrence
    __IndicatorOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurrence'), 'IndicatorOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_7_IndicatorOccurrence', STD_ANON_3)
    
    IndicatorOccurrence = property(__IndicatorOccurrence.value, __IndicatorOccurrence.set, None, u'No. occurs before 12 No.12')

    
    # Attribute NumberTypeOccurrence uses Python identifier NumberTypeOccurrence
    __NumberTypeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberTypeOccurrence'), 'NumberTypeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_7_NumberTypeOccurrence', STD_ANON_4)
    
    NumberTypeOccurrence = property(__NumberTypeOccurrence.value, __NumberTypeOccurrence.set, None, u'12 in BUILDING 12 occurs "after" premise type BUILDING')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_7_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'No. in House No.12, # in #12, etc.')

    
    # Attribute NumberType uses Python identifier NumberType
    __NumberType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberType'), 'NumberType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_7_NumberType', STD_ANON_2)
    
    NumberType = property(__NumberType.value, __NumberType.set, None, u'Building 12-14 is "Range" and Building 12 is "Single"')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_7_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __IndicatorOccurrence.name() : __IndicatorOccurrence,
        __NumberTypeOccurrence.name() : __NumberTypeOccurrence,
        __Indicator.name() : __Indicator,
        __NumberType.name() : __NumberType,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_8 with content type MIXED
class CTD_ANON_8 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_8_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_8_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Defines the type of address line. eg. Street, Address Line 1, etc.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_9 with content type ELEMENT_ONLY
class CTD_ANON_9 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberSuffix uses Python identifier PremiseNumberSuffix
    __PremiseNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), 'PremiseNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberSuffix', True)

    
    PremiseNumberSuffix = property(__PremiseNumberSuffix.value, __PremiseNumberSuffix.set, None, u'A in 12A')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseName uses Python identifier PremiseName
    __PremiseName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseName'), 'PremiseName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0PremiseName', True)

    
    PremiseName = property(__PremiseName.value, __PremiseName.set, None, u'Specification of the name of the premise (house, building, park, farm, etc). A premise name is specified when the premise cannot be addressed using a street name plus premise (house) number.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Firm uses Python identifier Firm
    __Firm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Firm'), 'Firm', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0Firm', False)

    
    Firm = property(__Firm.value, __Firm.set, None, u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from a large mail user address, which contains no street.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStop uses Python identifier MailStop
    __MailStop = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), 'MailStop', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0MailStop', False)

    
    MailStop = property(__MailStop.value, __MailStop.set, None, u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Premise uses Python identifier Premise
    __Premise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Premise'), 'Premise', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0Premise', False)

    
    Premise = property(__Premise.value, __Premise.set, None, u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberRange uses Python identifier PremiseNumberRange
    __PremiseNumberRange = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRange'), 'PremiseNumberRange', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberRange', False)

    
    PremiseNumberRange = property(__PremiseNumberRange.value, __PremiseNumberRange.set, None, u'Specification for defining the premise number range. Some premises have number as Building C1-C7')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}BuildingName uses Python identifier BuildingName
    __BuildingName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), 'BuildingName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0BuildingName', True)

    
    BuildingName = property(__BuildingName.value, __BuildingName.set, None, u'Specification of the name of a building.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumber uses Python identifier PremiseNumber
    __PremiseNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), 'PremiseNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumber', True)

    
    PremiseNumber = property(__PremiseNumber.value, __PremiseNumber.set, None, u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberPrefix uses Python identifier PremiseNumberPrefix
    __PremiseNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), 'PremiseNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberPrefix', True)

    
    PremiseNumberPrefix = property(__PremiseNumberPrefix.value, __PremiseNumberPrefix.set, None, u'A in A12')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseLocation uses Python identifier PremiseLocation
    __PremiseLocation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseLocation'), 'PremiseLocation', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0PremiseLocation', False)

    
    PremiseLocation = property(__PremiseLocation.value, __PremiseLocation.set, None, u'LOBBY, BASEMENT, GROUND FLOOR, etc...')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremise uses Python identifier SubPremise
    __SubPremise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'), 'SubPremise', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0SubPremise', True)

    
    SubPremise = property(__SubPremise.value, __SubPremise.set, None, u'Specification of a single sub-premise. Examples of sub-premises are apartments and suites. Each sub-premise should be uniquely identifiable.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Attribute PremiseThoroughfareConnector uses Python identifier PremiseThoroughfareConnector
    __PremiseThoroughfareConnector = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'PremiseThoroughfareConnector'), 'PremiseThoroughfareConnector', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_PremiseThoroughfareConnector', pyxb.binding.datatypes.anySimpleType)
    
    PremiseThoroughfareConnector = property(__PremiseThoroughfareConnector.value, __PremiseThoroughfareConnector.set, None, u'DES, DE, LA, LA, DU in RUE DU BOIS. These terms connect a premise/thoroughfare type and premise/thoroughfare name. Terms may appear with names AVE DU BOIS')

    
    # Attribute PremiseDependency uses Python identifier PremiseDependency
    __PremiseDependency = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'PremiseDependency'), 'PremiseDependency', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_PremiseDependency', pyxb.binding.datatypes.anySimpleType)
    
    PremiseDependency = property(__PremiseDependency.value, __PremiseDependency.set, None, u'STREET, PREMISE, SUBPREMISE, PARK, FARM, etc')

    
    # Attribute PremiseDependencyType uses Python identifier PremiseDependencyType
    __PremiseDependencyType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'PremiseDependencyType'), 'PremiseDependencyType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_PremiseDependencyType', pyxb.binding.datatypes.anySimpleType)
    
    PremiseDependencyType = property(__PremiseDependencyType.value, __PremiseDependencyType.set, None, u'NEAR, ADJACENT TO, etc')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'COMPLEXE in COMPLEX DES JARDINS, A building, station, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PremiseNumberSuffix.name() : __PremiseNumberSuffix,
        __PremiseName.name() : __PremiseName,
        __Firm.name() : __Firm,
        __MailStop.name() : __MailStop,
        __Premise.name() : __Premise,
        __PremiseNumberRange.name() : __PremiseNumberRange,
        __BuildingName.name() : __BuildingName,
        __PremiseNumber.name() : __PremiseNumber,
        __AddressLine.name() : __AddressLine,
        __PremiseNumberPrefix.name() : __PremiseNumberPrefix,
        __PremiseLocation.name() : __PremiseLocation,
        __SubPremise.name() : __SubPremise,
        __PostalCode.name() : __PostalCode
    }
    _AttributeMap = {
        __PremiseThoroughfareConnector.name() : __PremiseThoroughfareConnector,
        __PremiseDependency.name() : __PremiseDependency,
        __PremiseDependencyType.name() : __PremiseDependencyType,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_10 with content type ELEMENT_ONLY
class CTD_ANON_10 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberSuffix uses Python identifier PremiseNumberSuffix
    __PremiseNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), 'PremiseNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_10_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberSuffix', True)

    
    PremiseNumberSuffix = property(__PremiseNumberSuffix.value, __PremiseNumberSuffix.set, None, u'A in 12A')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_10_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberPrefix uses Python identifier PremiseNumberPrefix
    __PremiseNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), 'PremiseNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_10_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberPrefix', True)

    
    PremiseNumberPrefix = property(__PremiseNumberPrefix.value, __PremiseNumberPrefix.set, None, u'A in A12')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumber uses Python identifier PremiseNumber
    __PremiseNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), 'PremiseNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_10_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumber', True)

    
    PremiseNumber = property(__PremiseNumber.value, __PremiseNumber.set, None, u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.')


    _ElementMap = {
        __PremiseNumberSuffix.name() : __PremiseNumberSuffix,
        __AddressLine.name() : __AddressLine,
        __PremiseNumberPrefix.name() : __PremiseNumberPrefix,
        __PremiseNumber.name() : __PremiseNumber
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_11 with content type MIXED
class CTD_ANON_11 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute NameNumberOccurrence uses Python identifier NameNumberOccurrence
    __NameNumberOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NameNumberOccurrence'), 'NameNumberOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_NameNumberOccurrence', STD_ANON_5)
    
    NameNumberOccurrence = property(__NameNumberOccurrence.value, __NameNumberOccurrence.set, None, u'Eg. SECTOR occurs before 5 in SECTOR 5')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __NameNumberOccurrence.name() : __NameNumberOccurrence
    }



# Complex type CTD_ANON_12 with content type ELEMENT_ONLY
class CTD_ANON_12 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}LargeMailUser uses Python identifier LargeMailUser
    __LargeMailUser = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'), 'LargeMailUser', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_urnoasisnamestcciqxsdschemaxAL2_0LargeMailUser', False)

    
    LargeMailUser = property(__LargeMailUser.value, __LargeMailUser.set, None, u'Specification of a large mail user address. Examples of large mail users are postal companies, companies in France with a cedex number, hospitals and airports with their own post code. Large mail user addresses do not have a street name with premise name or premise number in countries like Netherlands. But they have a POBox and street also in countries like France')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}LocalityName uses Python identifier LocalityName
    __LocalityName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LocalityName'), 'LocalityName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_urnoasisnamestcciqxsdschemaxAL2_0LocalityName', True)

    
    LocalityName = property(__LocalityName.value, __LocalityName.set, None, u'Name of the locality')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOffice uses Python identifier PostOffice
    __PostOffice = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), 'PostOffice', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_urnoasisnamestcciqxsdschemaxAL2_0PostOffice', False)

    
    PostOffice = property(__PostOffice.value, __PostOffice.set, None, u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalRoute uses Python identifier PostalRoute
    __PostalRoute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), 'PostalRoute', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_urnoasisnamestcciqxsdschemaxAL2_0PostalRoute', False)

    
    PostalRoute = property(__PostalRoute.value, __PostalRoute.set, None, u'A Postal van is specific for a route as in Is`rael, Rural route')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBox uses Python identifier PostBox
    __PostBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), 'PostBox', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_urnoasisnamestcciqxsdschemaxAL2_0PostBox', False)

    
    PostBox = property(__PostBox.value, __PostBox.set, None, u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Thoroughfare uses Python identifier Thoroughfare
    __Thoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), 'Thoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_urnoasisnamestcciqxsdschemaxAL2_0Thoroughfare', False)

    
    Thoroughfare = property(__Thoroughfare.value, __Thoroughfare.set, None, u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentLocality uses Python identifier DependentLocality
    __DependentLocality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), 'DependentLocality', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_urnoasisnamestcciqxsdschemaxAL2_0DependentLocality', False)

    
    DependentLocality = property(__DependentLocality.value, __DependentLocality.set, None, u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Premise uses Python identifier Premise
    __Premise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Premise'), 'Premise', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_urnoasisnamestcciqxsdschemaxAL2_0Premise', False)

    
    Premise = property(__Premise.value, __Premise.set, None, u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station')

    
    # Attribute UsageType uses Python identifier UsageType
    __UsageType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'UsageType'), 'UsageType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_UsageType', pyxb.binding.datatypes.anySimpleType)
    
    UsageType = property(__UsageType.value, __UsageType.set, None, u'Postal or Political - Sometimes locations must be distinguished between postal system, and physical locations as defined by a political system')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'Erode (Dist) where (Dist) is the Indicator')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Possible values not limited to: City, IndustrialEstate, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PostalCode.name() : __PostalCode,
        __LargeMailUser.name() : __LargeMailUser,
        __LocalityName.name() : __LocalityName,
        __PostOffice.name() : __PostOffice,
        __PostalRoute.name() : __PostalRoute,
        __PostBox.name() : __PostBox,
        __AddressLine.name() : __AddressLine,
        __Thoroughfare.name() : __Thoroughfare,
        __DependentLocality.name() : __DependentLocality,
        __Premise.name() : __Premise
    }
    _AttributeMap = {
        __UsageType.name() : __UsageType,
        __Indicator.name() : __Indicator,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_13 with content type MIXED
class CTD_ANON_13 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_13_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_13_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type MailStopType with content type ELEMENT_ONLY
class MailStopType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MailStopType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_MailStopType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStopName uses Python identifier MailStopName
    __MailStopName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStopName'), 'MailStopName', '__urnoasisnamestcciqxsdschemaxAL2_0_MailStopType_urnoasisnamestcciqxsdschemaxAL2_0MailStopName', False)

    
    MailStopName = property(__MailStopName.value, __MailStopName.set, None, u'Name of the the Mail Stop. eg. MSP, MS, etc')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStopNumber uses Python identifier MailStopNumber
    __MailStopNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStopNumber'), 'MailStopNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_MailStopType_urnoasisnamestcciqxsdschemaxAL2_0MailStopNumber', False)

    
    MailStopNumber = property(__MailStopNumber.value, __MailStopNumber.set, None, u'Number of the Mail stop. eg. 123 in MS 123')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_MailStopType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __MailStopName.name() : __MailStopName,
        __MailStopNumber.name() : __MailStopNumber
    }
    _AttributeMap = {
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'MailStopType', MailStopType)


# Complex type CTD_ANON_14 with content type ELEMENT_ONLY
class CTD_ANON_14 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOfficeName uses Python identifier PostOfficeName
    __PostOfficeName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeName'), 'PostOfficeName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_14_urnoasisnamestcciqxsdschemaxAL2_0PostOfficeName', True)

    
    PostOfficeName = property(__PostOfficeName.value, __PostOfficeName.set, None, u'Specification of the name of the post office. This can be a rural postoffice where post is delivered or a post office containing post office boxes.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBox uses Python identifier PostBox
    __PostBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), 'PostBox', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_14_urnoasisnamestcciqxsdschemaxAL2_0PostBox', False)

    
    PostBox = property(__PostBox.value, __PostBox.set, None, u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalRoute uses Python identifier PostalRoute
    __PostalRoute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), 'PostalRoute', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_14_urnoasisnamestcciqxsdschemaxAL2_0PostalRoute', False)

    
    PostalRoute = property(__PostalRoute.value, __PostalRoute.set, None, u'A Postal van is specific for a route as in Is`rael, Rural route')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_14_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOfficeNumber uses Python identifier PostOfficeNumber
    __PostOfficeNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeNumber'), 'PostOfficeNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_14_urnoasisnamestcciqxsdschemaxAL2_0PostOfficeNumber', False)

    
    PostOfficeNumber = property(__PostOfficeNumber.value, __PostOfficeNumber.set, None, u'Specification of the number of the postoffice. Common in rural postoffices')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_14_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_14_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'eg. Kottivakkam (P.O) here (P.O) is the Indicator')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_14_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Could be a Mobile Postoffice Van as in Isreal')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PostOfficeName.name() : __PostOfficeName,
        __PostBox.name() : __PostBox,
        __PostalRoute.name() : __PostalRoute,
        __PostalCode.name() : __PostalCode,
        __PostOfficeNumber.name() : __PostOfficeNumber,
        __AddressLine.name() : __AddressLine
    }
    _AttributeMap = {
        __Indicator.name() : __Indicator,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_15 with content type ELEMENT_ONLY
class CTD_ANON_15 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBoxNumber uses Python identifier PostBoxNumber
    __PostBoxNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumber'), 'PostBoxNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0PostBoxNumber', False)

    
    PostBoxNumber = property(__PostBoxNumber.value, __PostBoxNumber.set, None, u'Specification of the number of a postbox')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Firm uses Python identifier Firm
    __Firm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Firm'), 'Firm', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0Firm', False)

    
    Firm = property(__Firm.value, __Firm.set, None, u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from \na large mail user address, which contains no street.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBoxNumberPrefix uses Python identifier PostBoxNumberPrefix
    __PostBoxNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberPrefix'), 'PostBoxNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0PostBoxNumberPrefix', False)

    
    PostBoxNumberPrefix = property(__PostBoxNumberPrefix.value, __PostBoxNumberPrefix.set, None, u'Specification of the prefix of the post box number. eg. A in POBox:A-123')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBoxNumberExtension uses Python identifier PostBoxNumberExtension
    __PostBoxNumberExtension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberExtension'), 'PostBoxNumberExtension', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0PostBoxNumberExtension', False)

    
    PostBoxNumberExtension = property(__PostBoxNumberExtension.value, __PostBoxNumberExtension.set, None, u'Some countries like USA have POBox as 12345-123')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBoxNumberSuffix uses Python identifier PostBoxNumberSuffix
    __PostBoxNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberSuffix'), 'PostBoxNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0PostBoxNumberSuffix', False)

    
    PostBoxNumberSuffix = property(__PostBoxNumberSuffix.value, __PostBoxNumberSuffix.set, None, u'Specification of the suffix of the post box number. eg. A in POBox:123A')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'LOCKED BAG NO:1234 where the Indicator is NO: and Type is LOCKED BAG')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Possible values are, not limited to: POBox and Freepost.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PostBoxNumber.name() : __PostBoxNumber,
        __Firm.name() : __Firm,
        __PostBoxNumberPrefix.name() : __PostBoxNumberPrefix,
        __PostBoxNumberExtension.name() : __PostBoxNumberExtension,
        __PostalCode.name() : __PostalCode,
        __AddressLine.name() : __AddressLine,
        __PostBoxNumberSuffix.name() : __PostBoxNumberSuffix
    }
    _AttributeMap = {
        __Indicator.name() : __Indicator,
        __Type.name() : __Type
    }



# Complex type SubPremiseType with content type ELEMENT_ONLY
class SubPremiseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SubPremiseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremiseLocation uses Python identifier SubPremiseLocation
    __SubPremiseLocation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseLocation'), 'SubPremiseLocation', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremiseLocation', False)

    
    SubPremiseLocation = property(__SubPremiseLocation.value, __SubPremiseLocation.set, None, u' Name of the SubPremise Location. eg. LOBBY, BASEMENT, GROUND FLOOR, etc...')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremiseNumberPrefix uses Python identifier SubPremiseNumberPrefix
    __SubPremiseNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberPrefix'), 'SubPremiseNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremiseNumberPrefix', True)

    
    SubPremiseNumberPrefix = property(__SubPremiseNumberPrefix.value, __SubPremiseNumberPrefix.set, None, u' Prefix of the sub premise number. eg. A in A-12')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremiseNumber uses Python identifier SubPremiseNumber
    __SubPremiseNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumber'), 'SubPremiseNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremiseNumber', True)

    
    SubPremiseNumber = property(__SubPremiseNumber.value, __SubPremiseNumber.set, None, u' Specification of the identifier of a sub-premise. Examples of sub-premises are apartments and suites. sub-premises in a building are often uniquely identified by means of consecutive\nidentifiers. The identifier can be a number, a letter or any combination of the two. In the latter case, the identifier includes exactly one variable (range) part, which is either a \nnumber or a single letter that is surrounded by fixed parts at the left (prefix) or the right (postfix).')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremiseName uses Python identifier SubPremiseName
    __SubPremiseName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseName'), 'SubPremiseName', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremiseName', True)

    
    SubPremiseName = property(__SubPremiseName.value, __SubPremiseName.set, None, u' Name of the SubPremise')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}BuildingName uses Python identifier BuildingName
    __BuildingName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), 'BuildingName', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0BuildingName', True)

    
    BuildingName = property(__BuildingName.value, __BuildingName.set, None, u'Name of the building')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremise uses Python identifier SubPremise
    __SubPremise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'), 'SubPremise', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremise', False)

    
    SubPremise = property(__SubPremise.value, __SubPremise.set, None, u'Specification of a single sub-premise. Examples of sub-premises are apartments and suites. \nEach sub-premise should be uniquely identifiable. SubPremiseType: Specification of the name of a sub-premise type. Possible values not limited to: Suite, Appartment, Floor, Unknown\nMultiple levels within a premise by recursively calling SubPremise Eg. Level 4, Suite 2, Block C')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Firm uses Python identifier Firm
    __Firm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Firm'), 'Firm', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0Firm', False)

    
    Firm = property(__Firm.value, __Firm.set, None, u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from a large mail user address, which contains no street.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremiseNumberSuffix uses Python identifier SubPremiseNumberSuffix
    __SubPremiseNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberSuffix'), 'SubPremiseNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremiseNumberSuffix', True)

    
    SubPremiseNumberSuffix = property(__SubPremiseNumberSuffix.value, __SubPremiseNumberSuffix.set, None, u' Suffix of the sub premise number. eg. A in 12A')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStop uses Python identifier MailStop
    __MailStop = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), 'MailStop', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0MailStop', False)

    
    MailStop = property(__MailStop.value, __MailStop.set, None, u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __SubPremiseLocation.name() : __SubPremiseLocation,
        __SubPremiseNumberPrefix.name() : __SubPremiseNumberPrefix,
        __AddressLine.name() : __AddressLine,
        __SubPremiseNumber.name() : __SubPremiseNumber,
        __SubPremiseName.name() : __SubPremiseName,
        __BuildingName.name() : __BuildingName,
        __SubPremise.name() : __SubPremise,
        __Firm.name() : __Firm,
        __SubPremiseNumberSuffix.name() : __SubPremiseNumberSuffix,
        __MailStop.name() : __MailStop,
        __PostalCode.name() : __PostalCode
    }
    _AttributeMap = {
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'SubPremiseType', SubPremiseType)


# Complex type CTD_ANON_16 with content type MIXED
class CTD_ANON_16 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberOccurrence uses Python identifier NumberOccurrence
    __NumberOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberOccurrence'), 'NumberOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_16_NumberOccurrence', STD_ANON_7)
    
    NumberOccurrence = property(__NumberOccurrence.value, __NumberOccurrence.set, None, u'23 Archer St, Archer Street 23, St Archer 23')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_16_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute NumberType uses Python identifier NumberType
    __NumberType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberType'), 'NumberType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_16_NumberType', STD_ANON_6)
    
    NumberType = property(__NumberType.value, __NumberType.set, None, u'12 Archer Street is "Single" and 12-14 Archer Street is "Range"')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_16_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_16_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'No. in Street No.12 or "#" in Street # 12, etc.')

    
    # Attribute IndicatorOccurrence uses Python identifier IndicatorOccurrence
    __IndicatorOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurrence'), 'IndicatorOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_16_IndicatorOccurrence', STD_ANON_8)
    
    IndicatorOccurrence = property(__IndicatorOccurrence.value, __IndicatorOccurrence.set, None, u'No.12 where "No." is before actual street number')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberOccurrence.name() : __NumberOccurrence,
        __Code.name() : __Code,
        __NumberType.name() : __NumberType,
        __Type.name() : __Type,
        __Indicator.name() : __Indicator,
        __IndicatorOccurrence.name() : __IndicatorOccurrence
    }



# Complex type CTD_ANON_17 with content type MIXED
class CTD_ANON_17 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberSuffix uses Python identifier ThoroughfareNumberSuffix
    __ThoroughfareNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), 'ThoroughfareNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_17_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberSuffix', True)

    
    ThoroughfareNumberSuffix = property(__ThoroughfareNumberSuffix.value, __ThoroughfareNumberSuffix.set, None, u'Suffix after the number. A in 12A Archer Street')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_17_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumber uses Python identifier ThoroughfareNumber
    __ThoroughfareNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), 'ThoroughfareNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_17_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumber', True)

    
    ThoroughfareNumber = property(__ThoroughfareNumber.value, __ThoroughfareNumber.set, None, u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberPrefix uses Python identifier ThoroughfareNumberPrefix
    __ThoroughfareNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), 'ThoroughfareNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_17_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberPrefix', True)

    
    ThoroughfareNumberPrefix = property(__ThoroughfareNumberPrefix.value, __ThoroughfareNumberPrefix.set, None, u'Prefix before the number. A in A12 Archer Street')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_17_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        __ThoroughfareNumberSuffix.name() : __ThoroughfareNumberSuffix,
        __AddressLine.name() : __AddressLine,
        __ThoroughfareNumber.name() : __ThoroughfareNumber,
        __ThoroughfareNumberPrefix.name() : __ThoroughfareNumberPrefix
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type DependentLocalityType with content type ELEMENT_ONLY
class DependentLocalityType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBox uses Python identifier PostBox
    __PostBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), 'PostBox', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0PostBox', False)

    
    PostBox = property(__PostBox.value, __PostBox.set, None, u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}LargeMailUser uses Python identifier LargeMailUser
    __LargeMailUser = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'), 'LargeMailUser', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0LargeMailUser', False)

    
    LargeMailUser = property(__LargeMailUser.value, __LargeMailUser.set, None, u'Specification of a large mail user address. Examples of large mail users are postal companies, companies in France with a cedex number, hospitals and airports with their own post code. Large mail user addresses do not have a street name with premise name or premise number in countries like Netherlands. But they have a POBox and street also in countries like France')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOffice uses Python identifier PostOffice
    __PostOffice = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), 'PostOffice', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0PostOffice', False)

    
    PostOffice = property(__PostOffice.value, __PostOffice.set, None, u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentLocalityNumber uses Python identifier DependentLocalityNumber
    __DependentLocalityNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityNumber'), 'DependentLocalityNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0DependentLocalityNumber', False)

    
    DependentLocalityNumber = property(__DependentLocalityNumber.value, __DependentLocalityNumber.set, None, u'Number of the dependent locality. Some areas are numbered. Eg. SECTOR 5 in a Suburb as in India or SOI SUKUMVIT 10 as in Thailand')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalRoute uses Python identifier PostalRoute
    __PostalRoute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), 'PostalRoute', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0PostalRoute', False)

    
    PostalRoute = property(__PostalRoute.value, __PostalRoute.set, None, u' A Postal van is specific for a route as in Is`rael, Rural route')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Thoroughfare uses Python identifier Thoroughfare
    __Thoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), 'Thoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0Thoroughfare', False)

    
    Thoroughfare = property(__Thoroughfare.value, __Thoroughfare.set, None, u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentLocality uses Python identifier DependentLocality
    __DependentLocality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), 'DependentLocality', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0DependentLocality', False)

    
    DependentLocality = property(__DependentLocality.value, __DependentLocality.set, None, u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Premise uses Python identifier Premise
    __Premise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Premise'), 'Premise', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0Premise', False)

    
    Premise = property(__Premise.value, __Premise.set, None, u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentLocalityName uses Python identifier DependentLocalityName
    __DependentLocalityName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityName'), 'DependentLocalityName', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0DependentLocalityName', True)

    
    DependentLocalityName = property(__DependentLocalityName.value, __DependentLocalityName.set, None, u'Name of the dependent locality')

    
    # Attribute Connector uses Python identifier Connector
    __Connector = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Connector'), 'Connector', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_Connector', pyxb.binding.datatypes.anySimpleType)
    
    Connector = property(__Connector.value, __Connector.set, None, u'"VIA" as in Hill Top VIA Parish where Parish is a locality and Hill Top is a dependent locality')

    
    # Attribute UsageType uses Python identifier UsageType
    __UsageType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'UsageType'), 'UsageType', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_UsageType', pyxb.binding.datatypes.anySimpleType)
    
    UsageType = property(__UsageType.value, __UsageType.set, None, u'Postal or Political - Sometimes locations must be distinguished between postal system, and physical locations as defined by a political system')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'Eg. Erode (Dist) where (Dist) is the Indicator')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'City or IndustrialEstate, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PostBox.name() : __PostBox,
        __PostalCode.name() : __PostalCode,
        __LargeMailUser.name() : __LargeMailUser,
        __PostOffice.name() : __PostOffice,
        __DependentLocalityNumber.name() : __DependentLocalityNumber,
        __PostalRoute.name() : __PostalRoute,
        __AddressLine.name() : __AddressLine,
        __Thoroughfare.name() : __Thoroughfare,
        __DependentLocality.name() : __DependentLocality,
        __Premise.name() : __Premise,
        __DependentLocalityName.name() : __DependentLocalityName
    }
    _AttributeMap = {
        __Connector.name() : __Connector,
        __UsageType.name() : __UsageType,
        __Indicator.name() : __Indicator,
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'DependentLocalityType', DependentLocalityType)


# Complex type CTD_ANON_18 with content type MIXED
class CTD_ANON_18 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberExtensionSeparator uses Python identifier NumberExtensionSeparator
    __NumberExtensionSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberExtensionSeparator'), 'NumberExtensionSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_18_NumberExtensionSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberExtensionSeparator = property(__NumberExtensionSeparator.value, __NumberExtensionSeparator.set, None, u'"-" is the NumberExtensionSeparator in POBOX:12345-123')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberExtensionSeparator.name() : __NumberExtensionSeparator
    }



# Complex type CTD_ANON_19 with content type MIXED
class CTD_ANON_19 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_19_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Scheme uses Python identifier Scheme
    __Scheme = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Scheme'), 'Scheme', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_19_Scheme', pyxb.binding.datatypes.anySimpleType)
    
    Scheme = property(__Scheme.value, __Scheme.set, None, u'Country code scheme possible values, but not limited to: iso.3166-2, iso.3166-3 for two and three character country codes.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Scheme.name() : __Scheme
    }



# Complex type AddressLinesType with content type ELEMENT_ONLY
class AddressLinesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AddressLinesType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressLinesType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AddressLinesType', AddressLinesType)


# Complex type CTD_ANON_20 with content type MIXED
class CTD_ANON_20 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_20_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_20_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_21 with content type MIXED
class CTD_ANON_21 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_21_Code', pyxb.binding.datatypes.string)
    
    Code = property(__Code.value, __Code.set, None, None)

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_21_Type', pyxb.binding.datatypes.string)
    
    Type = property(__Type.value, __Type.set, None, u'Airport, Hospital, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_22 with content type MIXED
class CTD_ANON_22 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_22_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_22_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type ThoroughfareTrailingTypeType with content type MIXED
class ThoroughfareTrailingTypeType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingTypeType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareTrailingTypeType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareTrailingTypeType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'ThoroughfareTrailingTypeType', ThoroughfareTrailingTypeType)


# Complex type CTD_ANON_23 with content type ELEMENT_ONLY
class CTD_ANON_23 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberRangeTo uses Python identifier PremiseNumberRangeTo
    __PremiseNumberRangeTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeTo'), 'PremiseNumberRangeTo', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberRangeTo', False)

    
    PremiseNumberRangeTo = property(__PremiseNumberRangeTo.value, __PremiseNumberRangeTo.set, None, u'End number details of the premise number range')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberRangeFrom uses Python identifier PremiseNumberRangeFrom
    __PremiseNumberRangeFrom = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeFrom'), 'PremiseNumberRangeFrom', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberRangeFrom', False)

    
    PremiseNumberRangeFrom = property(__PremiseNumberRangeFrom.value, __PremiseNumberRangeFrom.set, None, u'Start number details of the premise number range')

    
    # Attribute RangeType uses Python identifier RangeType
    __RangeType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'RangeType'), 'RangeType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_RangeType', pyxb.binding.datatypes.anySimpleType)
    
    RangeType = property(__RangeType.value, __RangeType.set, None, u'Eg. Odd or even number range')

    
    # Attribute Separator uses Python identifier Separator
    __Separator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Separator'), 'Separator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_Separator', pyxb.binding.datatypes.anySimpleType)
    
    Separator = property(__Separator.value, __Separator.set, None, u'"-" in 12-14  or "Thru" in 12 Thru 14 etc.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute IndicatorOccurence uses Python identifier IndicatorOccurence
    __IndicatorOccurence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurence'), 'IndicatorOccurence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_IndicatorOccurence', STD_ANON_9)
    
    IndicatorOccurence = property(__IndicatorOccurence.value, __IndicatorOccurence.set, None, u'No.12-14 where "No." is before actual street number')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'Eg. No. in Building No:C1-C5')

    
    # Attribute NumberRangeOccurence uses Python identifier NumberRangeOccurence
    __NumberRangeOccurence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberRangeOccurence'), 'NumberRangeOccurence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_NumberRangeOccurence', STD_ANON_10)
    
    NumberRangeOccurence = property(__NumberRangeOccurence.value, __NumberRangeOccurence.set, None, u'Building 23-25 where the number occurs after building name')


    _ElementMap = {
        __PremiseNumberRangeTo.name() : __PremiseNumberRangeTo,
        __PremiseNumberRangeFrom.name() : __PremiseNumberRangeFrom
    }
    _AttributeMap = {
        __RangeType.name() : __RangeType,
        __Separator.name() : __Separator,
        __Type.name() : __Type,
        __IndicatorOccurence.name() : __IndicatorOccurence,
        __Indicator.name() : __Indicator,
        __NumberRangeOccurence.name() : __NumberRangeOccurence
    }



# Complex type CTD_ANON_24 with content type MIXED
class CTD_ANON_24 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_24_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_24_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_25 with content type MIXED
class CTD_ANON_25 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberPrefixSeparator uses Python identifier NumberPrefixSeparator
    __NumberPrefixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberPrefixSeparator'), 'NumberPrefixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_25_NumberPrefixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberPrefixSeparator = property(__NumberPrefixSeparator.value, __NumberPrefixSeparator.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_25_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_25_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberPrefixSeparator.name() : __NumberPrefixSeparator,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_26 with content type MIXED
class CTD_ANON_26 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_26_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_27 with content type MIXED
class CTD_ANON_27 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberSuffixSeparator uses Python identifier NumberSuffixSeparator
    __NumberSuffixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberSuffixSeparator'), 'NumberSuffixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_27_NumberSuffixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberSuffixSeparator = property(__NumberSuffixSeparator.value, __NumberSuffixSeparator.set, None, u'12-A where 12 is number and A is suffix and "-" is the separator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_27_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_27_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberSuffixSeparator.name() : __NumberSuffixSeparator,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_28 with content type MIXED
class CTD_ANON_28 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_28_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_28_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_29 with content type SIMPLE
class CTD_ANON_29 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute NumberPrefixSeparator uses Python identifier NumberPrefixSeparator
    __NumberPrefixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberPrefixSeparator'), 'NumberPrefixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_NumberPrefixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberPrefixSeparator = property(__NumberPrefixSeparator.value, __NumberPrefixSeparator.set, None, u'A-12 where 12 is number and A is prefix and "-" is the separator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberPrefixSeparator.name() : __NumberPrefixSeparator,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_30 with content type MIXED
class CTD_ANON_30 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute TypeOccurrence uses Python identifier TypeOccurrence
    __TypeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'TypeOccurrence'), 'TypeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_30_TypeOccurrence', STD_ANON_11)
    
    TypeOccurrence = property(__TypeOccurrence.value, __TypeOccurrence.set, None, u'EGIS Building where EGIS occurs before Building')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_30_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_30_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __TypeOccurrence.name() : __TypeOccurrence,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_31 with content type MIXED
class CTD_ANON_31 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberSuffixSeparator uses Python identifier NumberSuffixSeparator
    __NumberSuffixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberSuffixSeparator'), 'NumberSuffixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_31_NumberSuffixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberSuffixSeparator = property(__NumberSuffixSeparator.value, __NumberSuffixSeparator.set, None, u'12-A where 12 is number and A is suffix and "-" is the separator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_31_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_31_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberSuffixSeparator.name() : __NumberSuffixSeparator,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type LargeMailUserType with content type ELEMENT_ONLY
class LargeMailUserType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}BuildingName uses Python identifier BuildingName
    __BuildingName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), 'BuildingName', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0BuildingName', True)

    
    BuildingName = property(__BuildingName.value, __BuildingName.set, None, u'Name of the building')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Thoroughfare uses Python identifier Thoroughfare
    __Thoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), 'Thoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0Thoroughfare', False)

    
    Thoroughfare = property(__Thoroughfare.value, __Thoroughfare.set, None, u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}LargeMailUserIdentifier uses Python identifier LargeMailUserIdentifier
    __LargeMailUserIdentifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserIdentifier'), 'LargeMailUserIdentifier', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0LargeMailUserIdentifier', False)

    
    LargeMailUserIdentifier = property(__LargeMailUserIdentifier.value, __LargeMailUserIdentifier.set, None, u'Specification of the identification number of a large mail user. An example are the Cedex codes in France.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Department uses Python identifier Department
    __Department = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Department'), 'Department', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0Department', False)

    
    Department = property(__Department.value, __Department.set, None, u'Subdivision in the firm: School of Physics at Victoria University (School of Physics is the department)')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}LargeMailUserName uses Python identifier LargeMailUserName
    __LargeMailUserName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserName'), 'LargeMailUserName', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0LargeMailUserName', True)

    
    LargeMailUserName = property(__LargeMailUserName.value, __LargeMailUserName.set, None, u'Name of the large mail user. eg. Smith Ford International airport')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBox uses Python identifier PostBox
    __PostBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), 'PostBox', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0PostBox', False)

    
    PostBox = property(__PostBox.value, __PostBox.set, None, u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_Type', pyxb.binding.datatypes.string)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __BuildingName.name() : __BuildingName,
        __Thoroughfare.name() : __Thoroughfare,
        __PostalCode.name() : __PostalCode,
        __AddressLine.name() : __AddressLine,
        __LargeMailUserIdentifier.name() : __LargeMailUserIdentifier,
        __Department.name() : __Department,
        __LargeMailUserName.name() : __LargeMailUserName,
        __PostBox.name() : __PostBox
    }
    _AttributeMap = {
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'LargeMailUserType', LargeMailUserType)


# Complex type CTD_ANON_32 with content type MIXED
class CTD_ANON_32 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberSuffixSeparator uses Python identifier NumberSuffixSeparator
    __NumberSuffixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberSuffixSeparator'), 'NumberSuffixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_32_NumberSuffixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberSuffixSeparator = property(__NumberSuffixSeparator.value, __NumberSuffixSeparator.set, None, u'NEAR, ADJACENT TO, etc12-A where 12 is number and A is suffix and "-" is the separator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_32_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_32_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberSuffixSeparator.name() : __NumberSuffixSeparator,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type PostalRouteType with content type ELEMENT_ONLY
class PostalRouteType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PostalRouteType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_PostalRouteType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalRouteName uses Python identifier PostalRouteName
    __PostalRouteName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteName'), 'PostalRouteName', '__urnoasisnamestcciqxsdschemaxAL2_0_PostalRouteType_urnoasisnamestcciqxsdschemaxAL2_0PostalRouteName', True)

    
    PostalRouteName = property(__PostalRouteName.value, __PostalRouteName.set, None, u' Name of the Postal Route')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBox uses Python identifier PostBox
    __PostBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), 'PostBox', '__urnoasisnamestcciqxsdschemaxAL2_0_PostalRouteType_urnoasisnamestcciqxsdschemaxAL2_0PostBox', False)

    
    PostBox = property(__PostBox.value, __PostBox.set, None, u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalRouteNumber uses Python identifier PostalRouteNumber
    __PostalRouteNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteNumber'), 'PostalRouteNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_PostalRouteType_urnoasisnamestcciqxsdschemaxAL2_0PostalRouteNumber', False)

    
    PostalRouteNumber = property(__PostalRouteNumber.value, __PostalRouteNumber.set, None, u' Number of the Postal Route')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_PostalRouteType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __PostalRouteName.name() : __PostalRouteName,
        __PostBox.name() : __PostBox,
        __PostalRouteNumber.name() : __PostalRouteNumber
    }
    _AttributeMap = {
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'PostalRouteType', PostalRouteType)


# Complex type CTD_ANON_33 with content type MIXED
class CTD_ANON_33 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_33_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_33_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_34 with content type MIXED
class CTD_ANON_34 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_34_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute IndicatorOccurrence uses Python identifier IndicatorOccurrence
    __IndicatorOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurrence'), 'IndicatorOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_34_IndicatorOccurrence', STD_ANON_12)
    
    IndicatorOccurrence = property(__IndicatorOccurrence.value, __IndicatorOccurrence.set, None, u'"No." occurs before 1 in No.1, or TH occurs after 12 in 12TH')

    
    # Attribute NumberTypeOccurrence uses Python identifier NumberTypeOccurrence
    __NumberTypeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberTypeOccurrence'), 'NumberTypeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_34_NumberTypeOccurrence', STD_ANON_13)
    
    NumberTypeOccurrence = property(__NumberTypeOccurrence.value, __NumberTypeOccurrence.set, None, u'12TH occurs "before" FLOOR (a type of subpremise) in 12TH FLOOR')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_34_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'"TH" in 12TH which is a floor number, "NO." in NO.1, "#" in APT #12, etc.')

    
    # Attribute PremiseNumberSeparator uses Python identifier PremiseNumberSeparator
    __PremiseNumberSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'PremiseNumberSeparator'), 'PremiseNumberSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_34_PremiseNumberSeparator', pyxb.binding.datatypes.anySimpleType)
    
    PremiseNumberSeparator = property(__PremiseNumberSeparator.value, __PremiseNumberSeparator.set, None, u'"/" in 12/14 Archer Street where 12 is sub-premise number and 14 is premise number')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_34_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __IndicatorOccurrence.name() : __IndicatorOccurrence,
        __NumberTypeOccurrence.name() : __NumberTypeOccurrence,
        __Indicator.name() : __Indicator,
        __PremiseNumberSeparator.name() : __PremiseNumberSeparator,
        __Type.name() : __Type
    }



# Complex type AddressDetails_ with content type ELEMENT_ONLY
class AddressDetails_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AddressDetails')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Thoroughfare uses Python identifier Thoroughfare
    __Thoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), 'Thoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0Thoroughfare', False)

    
    Thoroughfare = property(__Thoroughfare.value, __Thoroughfare.set, None, u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Address uses Python identifier Address
    __Address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Address'), 'Address', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0Address', False)

    
    Address = property(__Address.value, __Address.set, None, u'Address as one line of free text')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalServiceElements uses Python identifier PostalServiceElements
    __PostalServiceElements = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalServiceElements'), 'PostalServiceElements', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0PostalServiceElements', False)

    
    PostalServiceElements = property(__PostalServiceElements.value, __PostalServiceElements.set, None, u'Postal authorities use specific postal service data to expedient delivery of mail')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AdministrativeArea uses Python identifier AdministrativeArea
    __AdministrativeArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'), 'AdministrativeArea', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0AdministrativeArea', False)

    
    AdministrativeArea = property(__AdministrativeArea.value, __AdministrativeArea.set, None, u'Examples of administrative areas are provinces counties, special regions (such as "Rijnmond"), etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLines uses Python identifier AddressLines
    __AddressLines = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLines'), 'AddressLines', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0AddressLines', False)

    
    AddressLines = property(__AddressLines.value, __AddressLines.set, None, u'Container for Address lines')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Locality uses Python identifier Locality
    __Locality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Locality'), 'Locality', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0Locality', False)

    
    Locality = property(__Locality.value, __Locality.set, None, u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Country uses Python identifier Country
    __Country = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Country'), 'Country', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0Country', False)

    
    Country = property(__Country.value, __Country.set, None, u'Specification of a country')

    
    # Attribute ValidToDate uses Python identifier ValidToDate
    __ValidToDate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ValidToDate'), 'ValidToDate', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__ValidToDate', pyxb.binding.datatypes.anySimpleType)
    
    ValidToDate = property(__ValidToDate.value, __ValidToDate.set, None, u'End date of the validity of address')

    
    # Attribute AddressDetailsKey uses Python identifier AddressDetailsKey
    __AddressDetailsKey = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AddressDetailsKey'), 'AddressDetailsKey', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__AddressDetailsKey', pyxb.binding.datatypes.anySimpleType)
    
    AddressDetailsKey = property(__AddressDetailsKey.value, __AddressDetailsKey.set, None, u'Key identifier for the element for not reinforced references from other elements. Not required to be unique for the document to be valid, but application may get confused if not unique. Extend this schema adding unique contraint if needed.')

    
    # Attribute AddressType uses Python identifier AddressType
    __AddressType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AddressType'), 'AddressType', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__AddressType', pyxb.binding.datatypes.anySimpleType)
    
    AddressType = property(__AddressType.value, __AddressType.set, None, u'Type of address. Example: Postal, residential,business, primary, secondary, etc')

    
    # Attribute CurrentStatus uses Python identifier CurrentStatus
    __CurrentStatus = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'CurrentStatus'), 'CurrentStatus', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__CurrentStatus', pyxb.binding.datatypes.anySimpleType)
    
    CurrentStatus = property(__CurrentStatus.value, __CurrentStatus.set, None, u'Moved, Living, Investment, Deceased, etc..')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute ValidFromDate uses Python identifier ValidFromDate
    __ValidFromDate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ValidFromDate'), 'ValidFromDate', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__ValidFromDate', pyxb.binding.datatypes.anySimpleType)
    
    ValidFromDate = property(__ValidFromDate.value, __ValidFromDate.set, None, u'Start Date of the validity of address')

    
    # Attribute Usage uses Python identifier Usage
    __Usage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Usage'), 'Usage', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__Usage', pyxb.binding.datatypes.anySimpleType)
    
    Usage = property(__Usage.value, __Usage.set, None, u'Communication, Contact, etc.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __Thoroughfare.name() : __Thoroughfare,
        __Address.name() : __Address,
        __PostalServiceElements.name() : __PostalServiceElements,
        __AdministrativeArea.name() : __AdministrativeArea,
        __AddressLines.name() : __AddressLines,
        __Locality.name() : __Locality,
        __Country.name() : __Country
    }
    _AttributeMap = {
        __ValidToDate.name() : __ValidToDate,
        __AddressDetailsKey.name() : __AddressDetailsKey,
        __AddressType.name() : __AddressType,
        __CurrentStatus.name() : __CurrentStatus,
        __Code.name() : __Code,
        __ValidFromDate.name() : __ValidFromDate,
        __Usage.name() : __Usage
    }
Namespace.addCategoryObject('typeBinding', u'AddressDetails', AddressDetails_)


# Complex type CTD_ANON_35 with content type MIXED
class CTD_ANON_35 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_35_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_35_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type FirmType with content type ELEMENT_ONLY
class FirmType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FirmType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}FirmName uses Python identifier FirmName
    __FirmName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FirmName'), 'FirmName', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_urnoasisnamestcciqxsdschemaxAL2_0FirmName', True)

    
    FirmName = property(__FirmName.value, __FirmName.set, None, u'Name of the firm')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStop uses Python identifier MailStop
    __MailStop = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), 'MailStop', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_urnoasisnamestcciqxsdschemaxAL2_0MailStop', False)

    
    MailStop = property(__MailStop.value, __MailStop.set, None, u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Department uses Python identifier Department
    __Department = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Department'), 'Department', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_urnoasisnamestcciqxsdschemaxAL2_0Department', True)

    
    Department = property(__Department.value, __Department.set, None, u'Subdivision in the firm: School of Physics at Victoria University (School of Physics is the department)')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __FirmName.name() : __FirmName,
        __MailStop.name() : __MailStop,
        __Department.name() : __Department,
        __PostalCode.name() : __PostalCode
    }
    _AttributeMap = {
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'FirmType', FirmType)


# Complex type CTD_ANON_36 with content type MIXED
class CTD_ANON_36 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute TypeOccurrence uses Python identifier TypeOccurrence
    __TypeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'TypeOccurrence'), 'TypeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_36_TypeOccurrence', STD_ANON_14)
    
    TypeOccurrence = property(__TypeOccurrence.value, __TypeOccurrence.set, None, u'EGIS Building where EGIS occurs before Building, DES JARDINS occurs after COMPLEXE DES JARDINS')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_36_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_36_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __TypeOccurrence.name() : __TypeOccurrence,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_37 with content type MIXED
class CTD_ANON_37 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_37_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_37_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Postal, residential, corporate, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_38 with content type EMPTY
class CTD_ANON_38 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_38_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_38_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')


    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type BuildingNameType with content type MIXED
class BuildingNameType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingNameType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute TypeOccurrence uses Python identifier TypeOccurrence
    __TypeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'TypeOccurrence'), 'TypeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_BuildingNameType_TypeOccurrence', STD_ANON_15)
    
    TypeOccurrence = property(__TypeOccurrence.value, __TypeOccurrence.set, None, u'Occurrence of the building name before/after the type. eg. EGIS BUILDING where name appears before type')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_BuildingNameType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_BuildingNameType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __TypeOccurrence.name() : __TypeOccurrence,
        __Code.name() : __Code,
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'BuildingNameType', BuildingNameType)


# Complex type ThoroughfarePreDirectionType with content type MIXED
class ThoroughfarePreDirectionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirectionType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfarePreDirectionType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfarePreDirectionType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'ThoroughfarePreDirectionType', ThoroughfarePreDirectionType)


# Complex type CTD_ANON_39 with content type ELEMENT_ONLY
class CTD_ANON_39 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}CountryNameCode uses Python identifier CountryNameCode
    __CountryNameCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CountryNameCode'), 'CountryNameCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_39_urnoasisnamestcciqxsdschemaxAL2_0CountryNameCode', True)

    
    CountryNameCode = property(__CountryNameCode.value, __CountryNameCode.set, None, u'A country code according to the specified scheme')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AdministrativeArea uses Python identifier AdministrativeArea
    __AdministrativeArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'), 'AdministrativeArea', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_39_urnoasisnamestcciqxsdschemaxAL2_0AdministrativeArea', False)

    
    AdministrativeArea = property(__AdministrativeArea.value, __AdministrativeArea.set, None, u'Examples of administrative areas are provinces counties, special regions (such as "Rijnmond"), etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Locality uses Python identifier Locality
    __Locality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Locality'), 'Locality', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_39_urnoasisnamestcciqxsdschemaxAL2_0Locality', False)

    
    Locality = property(__Locality.value, __Locality.set, None, u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_39_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Thoroughfare uses Python identifier Thoroughfare
    __Thoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), 'Thoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_39_urnoasisnamestcciqxsdschemaxAL2_0Thoroughfare', False)

    
    Thoroughfare = property(__Thoroughfare.value, __Thoroughfare.set, None, u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}CountryName uses Python identifier CountryName
    __CountryName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CountryName'), 'CountryName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_39_urnoasisnamestcciqxsdschemaxAL2_0CountryName', True)

    
    CountryName = property(__CountryName.value, __CountryName.set, None, u'Specification of the name of a country.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __CountryNameCode.name() : __CountryNameCode,
        __AdministrativeArea.name() : __AdministrativeArea,
        __Locality.name() : __Locality,
        __AddressLine.name() : __AddressLine,
        __Thoroughfare.name() : __Thoroughfare,
        __CountryName.name() : __CountryName
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_40 with content type MIXED
class CTD_ANON_40 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_40_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_41 with content type MIXED
class CTD_ANON_41 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_41_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_41_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_42 with content type MIXED
class CTD_ANON_42 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_42_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'eg. Building 429 in which Building is the Indicator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_42_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_42_Type', pyxb.binding.datatypes.string)
    
    Type = property(__Type.value, __Type.set, None, u'CEDEX Code')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Indicator.name() : __Indicator,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_43 with content type MIXED
class CTD_ANON_43 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberSuffixSeparator uses Python identifier NumberSuffixSeparator
    __NumberSuffixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberSuffixSeparator'), 'NumberSuffixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_43_NumberSuffixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberSuffixSeparator = property(__NumberSuffixSeparator.value, __NumberSuffixSeparator.set, None, u'12-A where 12 is number and A is suffix and "-" is the separator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_43_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberSuffixSeparator.name() : __NumberSuffixSeparator,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_44 with content type ELEMENT_ONLY
class CTD_ANON_44 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberSuffix uses Python identifier PremiseNumberSuffix
    __PremiseNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), 'PremiseNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_44_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberSuffix', True)

    
    PremiseNumberSuffix = property(__PremiseNumberSuffix.value, __PremiseNumberSuffix.set, None, u'A in 12A')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_44_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumber uses Python identifier PremiseNumber
    __PremiseNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), 'PremiseNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_44_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumber', True)

    
    PremiseNumber = property(__PremiseNumber.value, __PremiseNumber.set, None, u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberPrefix uses Python identifier PremiseNumberPrefix
    __PremiseNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), 'PremiseNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_44_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberPrefix', True)

    
    PremiseNumberPrefix = property(__PremiseNumberPrefix.value, __PremiseNumberPrefix.set, None, u'A in A12')


    _ElementMap = {
        __PremiseNumberSuffix.name() : __PremiseNumberSuffix,
        __AddressLine.name() : __AddressLine,
        __PremiseNumber.name() : __PremiseNumber,
        __PremiseNumberPrefix.name() : __PremiseNumberPrefix
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_45 with content type MIXED
class CTD_ANON_45 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Old name, new name, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type ThoroughfarePostDirectionType with content type MIXED
class ThoroughfarePostDirectionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirectionType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfarePostDirectionType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfarePostDirectionType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'ThoroughfarePostDirectionType', ThoroughfarePostDirectionType)


# Complex type CTD_ANON_46 with content type MIXED
class CTD_ANON_46 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberPrefixSeparator uses Python identifier NumberPrefixSeparator
    __NumberPrefixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberPrefixSeparator'), 'NumberPrefixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_46_NumberPrefixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberPrefixSeparator = property(__NumberPrefixSeparator.value, __NumberPrefixSeparator.set, None, u'A-12 where 12 is number and A is prefix and "-" is the separator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_46_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberPrefixSeparator.name() : __NumberPrefixSeparator,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_47 with content type MIXED
class CTD_ANON_47 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_47_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_47_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_48 with content type MIXED
class CTD_ANON_48 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_48_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_48_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_49 with content type ELEMENT_ONLY
class CTD_ANON_49 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareName uses Python identifier ThoroughfareName
    __ThoroughfareName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'), 'ThoroughfareName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareName', True)

    
    ThoroughfareName = property(__ThoroughfareName.value, __ThoroughfareName.set, None, u'Specification of the name of a Thoroughfare (also dependant street name): street name, canal name, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberSuffix uses Python identifier ThoroughfareNumberSuffix
    __ThoroughfareNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), 'ThoroughfareNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberSuffix', True)

    
    ThoroughfareNumberSuffix = property(__ThoroughfareNumberSuffix.value, __ThoroughfareNumberSuffix.set, None, u'Suffix after the number. A in 12A Archer Street')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareTrailingType uses Python identifier ThoroughfareTrailingType
    __ThoroughfareTrailingType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'), 'ThoroughfareTrailingType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareTrailingType', False)

    
    ThoroughfareTrailingType = property(__ThoroughfareTrailingType.value, __ThoroughfareTrailingType.set, None, u'Appears after the thoroughfare name. Ed. British: Baker Lane, where Lane is the trailing type.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Firm uses Python identifier Firm
    __Firm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Firm'), 'Firm', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0Firm', False)

    
    Firm = property(__Firm.value, __Firm.set, None, u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from \na large mail user address, which contains no street.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Premise uses Python identifier Premise
    __Premise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Premise'), 'Premise', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0Premise', False)

    
    Premise = property(__Premise.value, __Premise.set, None, u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareLeadingType uses Python identifier ThoroughfareLeadingType
    __ThoroughfareLeadingType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'), 'ThoroughfareLeadingType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareLeadingType', False)

    
    ThoroughfareLeadingType = property(__ThoroughfareLeadingType.value, __ThoroughfareLeadingType.set, None, u'Appears before the thoroughfare name. Ed. Spanish: Avenida Aurora, where Avenida is the leading type / French: Rue Moliere, where Rue is the leading type.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfarePostDirection uses Python identifier ThoroughfarePostDirection
    __ThoroughfarePostDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'), 'ThoroughfarePostDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfarePostDirection', False)

    
    ThoroughfarePostDirection = property(__ThoroughfarePostDirection.value, __ThoroughfarePostDirection.set, None, u'221-bis Baker Street North, where North is the post-direction. The post-direction appears after the name.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentLocality uses Python identifier DependentLocality
    __DependentLocality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), 'DependentLocality', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0DependentLocality', False)

    
    DependentLocality = property(__DependentLocality.value, __DependentLocality.set, None, u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumber uses Python identifier ThoroughfareNumber
    __ThoroughfareNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), 'ThoroughfareNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumber', True)

    
    ThoroughfareNumber = property(__ThoroughfareNumber.value, __ThoroughfareNumber.set, None, u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentThoroughfare uses Python identifier DependentThoroughfare
    __DependentThoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentThoroughfare'), 'DependentThoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0DependentThoroughfare', False)

    
    DependentThoroughfare = property(__DependentThoroughfare.value, __DependentThoroughfare.set, None, u'DependentThroughfare is related to a street; occurs in GB, IE, ES, PT')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfarePreDirection uses Python identifier ThoroughfarePreDirection
    __ThoroughfarePreDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection'), 'ThoroughfarePreDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfarePreDirection', False)

    
    ThoroughfarePreDirection = property(__ThoroughfarePreDirection.value, __ThoroughfarePreDirection.set, None, u'North Baker Street, where North is the pre-direction. The direction appears before the name.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberRange uses Python identifier ThoroughfareNumberRange
    __ThoroughfareNumberRange = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberRange'), 'ThoroughfareNumberRange', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberRange', True)

    
    ThoroughfareNumberRange = property(__ThoroughfareNumberRange.value, __ThoroughfareNumberRange.set, None, u'A container to represent a range of numbers (from x thru y)for a thoroughfare. eg. 1-2 Albert Av')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberPrefix uses Python identifier ThoroughfareNumberPrefix
    __ThoroughfareNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), 'ThoroughfareNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberPrefix', True)

    
    ThoroughfareNumberPrefix = property(__ThoroughfareNumberPrefix.value, __ThoroughfareNumberPrefix.set, None, u'Prefix before the number. A in A12 Archer Street')

    
    # Attribute DependentThoroughfaresType uses Python identifier DependentThoroughfaresType
    __DependentThoroughfaresType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DependentThoroughfaresType'), 'DependentThoroughfaresType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_DependentThoroughfaresType', pyxb.binding.datatypes.anySimpleType)
    
    DependentThoroughfaresType = property(__DependentThoroughfaresType.value, __DependentThoroughfaresType.set, None, u'STS in GEORGE and ADELAIDE STS, RDS IN A and B RDS, etc. Use only when both the street types are the same')

    
    # Attribute DependentThoroughfares uses Python identifier DependentThoroughfares
    __DependentThoroughfares = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DependentThoroughfares'), 'DependentThoroughfares', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_DependentThoroughfares', STD_ANON_16)
    
    DependentThoroughfares = property(__DependentThoroughfares.value, __DependentThoroughfares.set, None, u'Does this thoroughfare have a a dependent thoroughfare? Corner of street X, etc')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute DependentThoroughfaresIndicator uses Python identifier DependentThoroughfaresIndicator
    __DependentThoroughfaresIndicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DependentThoroughfaresIndicator'), 'DependentThoroughfaresIndicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_DependentThoroughfaresIndicator', pyxb.binding.datatypes.anySimpleType)
    
    DependentThoroughfaresIndicator = property(__DependentThoroughfaresIndicator.value, __DependentThoroughfaresIndicator.set, None, u'Corner of, Intersection of')

    
    # Attribute DependentThoroughfaresConnector uses Python identifier DependentThoroughfaresConnector
    __DependentThoroughfaresConnector = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DependentThoroughfaresConnector'), 'DependentThoroughfaresConnector', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_DependentThoroughfaresConnector', pyxb.binding.datatypes.anySimpleType)
    
    DependentThoroughfaresConnector = property(__DependentThoroughfaresConnector.value, __DependentThoroughfaresConnector.set, None, u'Corner of Street1 AND Street 2 where AND is the Connector')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __ThoroughfareName.name() : __ThoroughfareName,
        __ThoroughfareNumberSuffix.name() : __ThoroughfareNumberSuffix,
        __AddressLine.name() : __AddressLine,
        __ThoroughfareTrailingType.name() : __ThoroughfareTrailingType,
        __Firm.name() : __Firm,
        __Premise.name() : __Premise,
        __ThoroughfareLeadingType.name() : __ThoroughfareLeadingType,
        __ThoroughfarePostDirection.name() : __ThoroughfarePostDirection,
        __DependentLocality.name() : __DependentLocality,
        __ThoroughfareNumber.name() : __ThoroughfareNumber,
        __DependentThoroughfare.name() : __DependentThoroughfare,
        __PostalCode.name() : __PostalCode,
        __ThoroughfarePreDirection.name() : __ThoroughfarePreDirection,
        __ThoroughfareNumberRange.name() : __ThoroughfareNumberRange,
        __ThoroughfareNumberPrefix.name() : __ThoroughfareNumberPrefix
    }
    _AttributeMap = {
        __DependentThoroughfaresType.name() : __DependentThoroughfaresType,
        __DependentThoroughfares.name() : __DependentThoroughfares,
        __Type.name() : __Type,
        __DependentThoroughfaresIndicator.name() : __DependentThoroughfaresIndicator,
        __DependentThoroughfaresConnector.name() : __DependentThoroughfaresConnector
    }



# Complex type CTD_ANON_50 with content type MIXED
class CTD_ANON_50 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_50_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute NumberExtensionSeparator uses Python identifier NumberExtensionSeparator
    __NumberExtensionSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberExtensionSeparator'), 'NumberExtensionSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_50_NumberExtensionSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberExtensionSeparator = property(__NumberExtensionSeparator.value, __NumberExtensionSeparator.set, None, u'The separator between postal code number and the extension. Eg. "-"')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_50_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Delivery Point Suffix, New Postal Code, etc..')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __NumberExtensionSeparator.name() : __NumberExtensionSeparator,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_51 with content type MIXED
class CTD_ANON_51 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberSuffix uses Python identifier ThoroughfareNumberSuffix
    __ThoroughfareNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), 'ThoroughfareNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_51_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberSuffix', True)

    
    ThoroughfareNumberSuffix = property(__ThoroughfareNumberSuffix.value, __ThoroughfareNumberSuffix.set, None, u'Suffix after the number. A in 12A Archer Street')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_51_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberPrefix uses Python identifier ThoroughfareNumberPrefix
    __ThoroughfareNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), 'ThoroughfareNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_51_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberPrefix', True)

    
    ThoroughfareNumberPrefix = property(__ThoroughfareNumberPrefix.value, __ThoroughfareNumberPrefix.set, None, u'Prefix before the number. A in A12 Archer Street')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumber uses Python identifier ThoroughfareNumber
    __ThoroughfareNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), 'ThoroughfareNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_51_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumber', True)

    
    ThoroughfareNumber = property(__ThoroughfareNumber.value, __ThoroughfareNumber.set, None, u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_51_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        __ThoroughfareNumberSuffix.name() : __ThoroughfareNumberSuffix,
        __AddressLine.name() : __AddressLine,
        __ThoroughfareNumberPrefix.name() : __ThoroughfareNumberPrefix,
        __ThoroughfareNumber.name() : __ThoroughfareNumber
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_52 with content type ELEMENT_ONLY
class CTD_ANON_52 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AdministrativeAreaName uses Python identifier AdministrativeAreaName
    __AdministrativeAreaName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeAreaName'), 'AdministrativeAreaName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_urnoasisnamestcciqxsdschemaxAL2_0AdministrativeAreaName', True)

    
    AdministrativeAreaName = property(__AdministrativeAreaName.value, __AdministrativeAreaName.set, None, u' Name of the administrative area. eg. MI in USA, NSW in Australia')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Locality uses Python identifier Locality
    __Locality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Locality'), 'Locality', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_urnoasisnamestcciqxsdschemaxAL2_0Locality', False)

    
    Locality = property(__Locality.value, __Locality.set, None, u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubAdministrativeArea uses Python identifier SubAdministrativeArea
    __SubAdministrativeArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeArea'), 'SubAdministrativeArea', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_urnoasisnamestcciqxsdschemaxAL2_0SubAdministrativeArea', False)

    
    SubAdministrativeArea = property(__SubAdministrativeArea.value, __SubAdministrativeArea.set, None, u' Specification of a sub-administrative area. An example of a sub-administrative areas is a county. There are two places where the name of an administrative \narea can be specified and in this case, one becomes sub-administrative area.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOffice uses Python identifier PostOffice
    __PostOffice = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), 'PostOffice', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_urnoasisnamestcciqxsdschemaxAL2_0PostOffice', False)

    
    PostOffice = property(__PostOffice.value, __PostOffice.set, None, u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.')

    
    # Attribute UsageType uses Python identifier UsageType
    __UsageType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'UsageType'), 'UsageType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_UsageType', pyxb.binding.datatypes.anySimpleType)
    
    UsageType = property(__UsageType.value, __UsageType.set, None, u'Postal or Political - Sometimes locations must be distinguished between postal system, and physical locations as defined by a political system')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'Erode (Dist) where (Dist) is the Indicator')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Province or State or County or Kanton, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AdministrativeAreaName.name() : __AdministrativeAreaName,
        __Locality.name() : __Locality,
        __AddressLine.name() : __AddressLine,
        __SubAdministrativeArea.name() : __SubAdministrativeArea,
        __PostalCode.name() : __PostalCode,
        __PostOffice.name() : __PostOffice
    }
    _AttributeMap = {
        __UsageType.name() : __UsageType,
        __Indicator.name() : __Indicator,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_53 with content type ELEMENT_ONLY
class CTD_ANON_53 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostTownSuffix uses Python identifier PostTownSuffix
    __PostTownSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostTownSuffix'), 'PostTownSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_53_urnoasisnamestcciqxsdschemaxAL2_0PostTownSuffix', False)

    
    PostTownSuffix = property(__PostTownSuffix.value, __PostTownSuffix.set, None, u'GENERAL PO in MIAMI GENERAL PO')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_53_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostTownName uses Python identifier PostTownName
    __PostTownName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostTownName'), 'PostTownName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_53_urnoasisnamestcciqxsdschemaxAL2_0PostTownName', True)

    
    PostTownName = property(__PostTownName.value, __PostTownName.set, None, u'Name of the post town')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_53_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'eg. village, town, suburb, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        __PostTownSuffix.name() : __PostTownSuffix,
        __AddressLine.name() : __AddressLine,
        __PostTownName.name() : __PostTownName
    }
    _AttributeMap = {
        __Type.name() : __Type
    }



# Complex type CTD_ANON_54 with content type MIXED
class CTD_ANON_54 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_54_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_54_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type ThoroughfareLeadingTypeType with content type MIXED
class ThoroughfareLeadingTypeType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingTypeType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareLeadingTypeType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareLeadingTypeType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'ThoroughfareLeadingTypeType', ThoroughfareLeadingTypeType)


# Complex type CTD_ANON_55 with content type MIXED
class CTD_ANON_55 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_55_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_55_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_56 with content type ELEMENT_ONLY
class CTD_ANON_56 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Barcode uses Python identifier Barcode
    __Barcode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Barcode'), 'Barcode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_urnoasisnamestcciqxsdschemaxAL2_0Barcode', False)

    
    Barcode = property(__Barcode.value, __Barcode.set, None, u'Required for some postal services')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressIdentifier uses Python identifier AddressIdentifier
    __AddressIdentifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressIdentifier'), 'AddressIdentifier', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_urnoasisnamestcciqxsdschemaxAL2_0AddressIdentifier', True)

    
    AddressIdentifier = property(__AddressIdentifier.value, __AddressIdentifier.set, None, u'A unique identifier of an address assigned by postal authorities. Example: DPID in Australia')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SortingCode uses Python identifier SortingCode
    __SortingCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SortingCode'), 'SortingCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_urnoasisnamestcciqxsdschemaxAL2_0SortingCode', False)

    
    SortingCode = property(__SortingCode.value, __SortingCode.set, None, u'Used for sorting addresses. Values may for example be CEDEX 16 (France)')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLongitude uses Python identifier AddressLongitude
    __AddressLongitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'), 'AddressLongitude', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_urnoasisnamestcciqxsdschemaxAL2_0AddressLongitude', False)

    
    AddressLongitude = property(__AddressLongitude.value, __AddressLongitude.set, None, u'Longtitude of delivery address')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SupplementaryPostalServiceData uses Python identifier SupplementaryPostalServiceData
    __SupplementaryPostalServiceData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'), 'SupplementaryPostalServiceData', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_urnoasisnamestcciqxsdschemaxAL2_0SupplementaryPostalServiceData', True)

    
    SupplementaryPostalServiceData = property(__SupplementaryPostalServiceData.value, __SupplementaryPostalServiceData.set, None, u'any postal service elements not covered by the container can be represented using this element')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}KeyLineCode uses Python identifier KeyLineCode
    __KeyLineCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyLineCode'), 'KeyLineCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_urnoasisnamestcciqxsdschemaxAL2_0KeyLineCode', False)

    
    KeyLineCode = property(__KeyLineCode.value, __KeyLineCode.set, None, u'Required for some postal services')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLatitude uses Python identifier AddressLatitude
    __AddressLatitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitude'), 'AddressLatitude', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_urnoasisnamestcciqxsdschemaxAL2_0AddressLatitude', False)

    
    AddressLatitude = property(__AddressLatitude.value, __AddressLatitude.set, None, u'Latitude of delivery address')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLatitudeDirection uses Python identifier AddressLatitudeDirection
    __AddressLatitudeDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection'), 'AddressLatitudeDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_urnoasisnamestcciqxsdschemaxAL2_0AddressLatitudeDirection', False)

    
    AddressLatitudeDirection = property(__AddressLatitudeDirection.value, __AddressLatitudeDirection.set, None, u'Latitude direction of delivery address;N = North and S = South')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLongitudeDirection uses Python identifier AddressLongitudeDirection
    __AddressLongitudeDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'), 'AddressLongitudeDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_urnoasisnamestcciqxsdschemaxAL2_0AddressLongitudeDirection', False)

    
    AddressLongitudeDirection = property(__AddressLongitudeDirection.value, __AddressLongitudeDirection.set, None, u'Longtitude direction of delivery address;N=North and S=South')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}EndorsementLineCode uses Python identifier EndorsementLineCode
    __EndorsementLineCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EndorsementLineCode'), 'EndorsementLineCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_urnoasisnamestcciqxsdschemaxAL2_0EndorsementLineCode', False)

    
    EndorsementLineCode = property(__EndorsementLineCode.value, __EndorsementLineCode.set, None, u'Directly affects postal service distribution')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'USPS, ECMA, UN/PROLIST, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __Barcode.name() : __Barcode,
        __AddressIdentifier.name() : __AddressIdentifier,
        __SortingCode.name() : __SortingCode,
        __AddressLongitude.name() : __AddressLongitude,
        __SupplementaryPostalServiceData.name() : __SupplementaryPostalServiceData,
        __KeyLineCode.name() : __KeyLineCode,
        __AddressLatitude.name() : __AddressLatitude,
        __AddressLatitudeDirection.name() : __AddressLatitudeDirection,
        __AddressLongitudeDirection.name() : __AddressLongitudeDirection,
        __EndorsementLineCode.name() : __EndorsementLineCode
    }
    _AttributeMap = {
        __Type.name() : __Type
    }



# Complex type CTD_ANON_57 with content type MIXED
class CTD_ANON_57 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_57_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_57_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute IdentifierType uses Python identifier IdentifierType
    __IdentifierType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IdentifierType'), 'IdentifierType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_57_IdentifierType', pyxb.binding.datatypes.anySimpleType)
    
    IdentifierType = property(__IdentifierType.value, __IdentifierType.set, None, u'Type of identifier. eg. DPID as in Australia')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type,
        __IdentifierType.name() : __IdentifierType
    }



# Complex type CTD_ANON_58 with content type ELEMENT_ONLY
class CTD_ANON_58 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubAdministrativeAreaName uses Python identifier SubAdministrativeAreaName
    __SubAdministrativeAreaName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeAreaName'), 'SubAdministrativeAreaName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_urnoasisnamestcciqxsdschemaxAL2_0SubAdministrativeAreaName', True)

    
    SubAdministrativeAreaName = property(__SubAdministrativeAreaName.value, __SubAdministrativeAreaName.set, None, u' Name of the sub-administrative area')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Locality uses Python identifier Locality
    __Locality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Locality'), 'Locality', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_urnoasisnamestcciqxsdschemaxAL2_0Locality', False)

    
    Locality = property(__Locality.value, __Locality.set, None, u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOffice uses Python identifier PostOffice
    __PostOffice = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), 'PostOffice', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_urnoasisnamestcciqxsdschemaxAL2_0PostOffice', False)

    
    PostOffice = property(__PostOffice.value, __PostOffice.set, None, u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Attribute UsageType uses Python identifier UsageType
    __UsageType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'UsageType'), 'UsageType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_UsageType', pyxb.binding.datatypes.anySimpleType)
    
    UsageType = property(__UsageType.value, __UsageType.set, None, u'Postal or Political - Sometimes locations must be distinguished between postal system, and physical locations as defined by a political system')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'Erode (Dist) where (Dist) is the Indicator')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Province or State or County or Kanton, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __SubAdministrativeAreaName.name() : __SubAdministrativeAreaName,
        __Locality.name() : __Locality,
        __PostOffice.name() : __PostOffice,
        __PostalCode.name() : __PostalCode
    }
    _AttributeMap = {
        __UsageType.name() : __UsageType,
        __Indicator.name() : __Indicator,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_59 with content type ELEMENT_ONLY
class CTD_ANON_59 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberTo uses Python identifier ThoroughfareNumberTo
    __ThoroughfareNumberTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberTo'), 'ThoroughfareNumberTo', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberTo', False)

    
    ThoroughfareNumberTo = property(__ThoroughfareNumberTo.value, __ThoroughfareNumberTo.set, None, u'Ending number in the range')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberFrom uses Python identifier ThoroughfareNumberFrom
    __ThoroughfareNumberFrom = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberFrom'), 'ThoroughfareNumberFrom', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberFrom', False)

    
    ThoroughfareNumberFrom = property(__ThoroughfareNumberFrom.value, __ThoroughfareNumberFrom.set, None, u'Starting number in the range')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Separator uses Python identifier Separator
    __Separator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Separator'), 'Separator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_Separator', pyxb.binding.datatypes.anySimpleType)
    
    Separator = property(__Separator.value, __Separator.set, None, u'"-" in 12-14  or "Thru" in 12 Thru 14 etc.')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'"No." No.12-13')

    
    # Attribute IndicatorOccurrence uses Python identifier IndicatorOccurrence
    __IndicatorOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurrence'), 'IndicatorOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_IndicatorOccurrence', STD_ANON_17)
    
    IndicatorOccurrence = property(__IndicatorOccurrence.value, __IndicatorOccurrence.set, None, u'No.12-14 where "No." is before actual street number')

    
    # Attribute NumberRangeOccurrence uses Python identifier NumberRangeOccurrence
    __NumberRangeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberRangeOccurrence'), 'NumberRangeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_NumberRangeOccurrence', STD_ANON_19)
    
    NumberRangeOccurrence = property(__NumberRangeOccurrence.value, __NumberRangeOccurrence.set, None, u'23-25 Archer St, where number appears before name')

    
    # Attribute RangeType uses Python identifier RangeType
    __RangeType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'RangeType'), 'RangeType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_RangeType', STD_ANON_18)
    
    RangeType = property(__RangeType.value, __RangeType.set, None, u'Thoroughfare number ranges are odd or even')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        __ThoroughfareNumberTo.name() : __ThoroughfareNumberTo,
        __AddressLine.name() : __AddressLine,
        __ThoroughfareNumberFrom.name() : __ThoroughfareNumberFrom
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type,
        __Separator.name() : __Separator,
        __Indicator.name() : __Indicator,
        __IndicatorOccurrence.name() : __IndicatorOccurrence,
        __NumberRangeOccurrence.name() : __NumberRangeOccurrence,
        __RangeType.name() : __RangeType
    }



# Complex type CTD_ANON_60 with content type ELEMENT_ONLY
class CTD_ANON_60 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfarePreDirection uses Python identifier ThoroughfarePreDirection
    __ThoroughfarePreDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection'), 'ThoroughfarePreDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfarePreDirection', False)

    
    ThoroughfarePreDirection = property(__ThoroughfarePreDirection.value, __ThoroughfarePreDirection.set, None, u'North Baker Street, where North is the pre-direction. The direction appears before the name.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfarePostDirection uses Python identifier ThoroughfarePostDirection
    __ThoroughfarePostDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'), 'ThoroughfarePostDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfarePostDirection', False)

    
    ThoroughfarePostDirection = property(__ThoroughfarePostDirection.value, __ThoroughfarePostDirection.set, None, u'221-bis Baker Street North, where North is the post-direction. The post-direction appears after the name.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareLeadingType uses Python identifier ThoroughfareLeadingType
    __ThoroughfareLeadingType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'), 'ThoroughfareLeadingType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareLeadingType', False)

    
    ThoroughfareLeadingType = property(__ThoroughfareLeadingType.value, __ThoroughfareLeadingType.set, None, u'Appears before the thoroughfare name. Ed. Spanish: Avenida Aurora, where Avenida is the leading type / French: Rue Moliere, where Rue is the leading type.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareName uses Python identifier ThoroughfareName
    __ThoroughfareName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'), 'ThoroughfareName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareName', True)

    
    ThoroughfareName = property(__ThoroughfareName.value, __ThoroughfareName.set, None, u'Specification of the name of a Thoroughfare (also dependant street name): street name, canal name, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareTrailingType uses Python identifier ThoroughfareTrailingType
    __ThoroughfareTrailingType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'), 'ThoroughfareTrailingType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareTrailingType', False)

    
    ThoroughfareTrailingType = property(__ThoroughfareTrailingType.value, __ThoroughfareTrailingType.set, None, u'Appears after the thoroughfare name. Ed. British: Baker Lane, where Lane is the trailing type.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __ThoroughfarePreDirection.name() : __ThoroughfarePreDirection,
        __ThoroughfarePostDirection.name() : __ThoroughfarePostDirection,
        __ThoroughfareLeadingType.name() : __ThoroughfareLeadingType,
        __ThoroughfareName.name() : __ThoroughfareName,
        __ThoroughfareTrailingType.name() : __ThoroughfareTrailingType
    }
    _AttributeMap = {
        __Type.name() : __Type
    }



# Complex type CTD_ANON_61 with content type MIXED
class CTD_ANON_61 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_61_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_61_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_62 with content type MIXED
class CTD_ANON_62 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_63 with content type MIXED
class CTD_ANON_63 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_63_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_63_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_64 with content type ELEMENT_ONLY
class CTD_ANON_64 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails uses Python identifier AddressDetails
    __AddressDetails = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressDetails'), 'AddressDetails', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_64_urnoasisnamestcciqxsdschemaxAL2_0AddressDetails', True)

    
    AddressDetails = property(__AddressDetails.value, __AddressDetails.set, None, u'This container defines the details of the address. Can define multiple addresses including tracking address history')

    
    # Attribute Version uses Python identifier Version
    __Version = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Version'), 'Version', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_64_Version', pyxb.binding.datatypes.anySimpleType)
    
    Version = property(__Version.value, __Version.set, None, u'Specific to DTD to specify the version number of DTD')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressDetails.name() : __AddressDetails
    }
    _AttributeMap = {
        __Version.name() : __Version
    }



# Complex type CTD_ANON_65 with content type MIXED
class CTD_ANON_65 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_65_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_65_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Old Postal Code, new code, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_66 with content type MIXED
class CTD_ANON_66 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_66_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')


    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_67 with content type MIXED
class CTD_ANON_67 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_67_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute NameNumberSeparator uses Python identifier NameNumberSeparator
    __NameNumberSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NameNumberSeparator'), 'NameNumberSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_67_NameNumberSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NameNumberSeparator = property(__NameNumberSeparator.value, __NameNumberSeparator.set, None, u'"-" in MS-123')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __NameNumberSeparator.name() : __NameNumberSeparator
    }



# Complex type CTD_ANON_68 with content type MIXED
class CTD_ANON_68 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_68_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_68_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_69 with content type MIXED
class CTD_ANON_69 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_69_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_70 with content type MIXED
class CTD_ANON_70 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_70_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_70_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



Department = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Department'), CTD_ANON_3, documentation=u'Subdivision in the firm: School of Physics at Victoria University (School of Physics is the department)')
Namespace.addCategoryObject('elementBinding', Department.name().localName(), Department)

Locality = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Locality'), CTD_ANON_12, documentation=u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.')
Namespace.addCategoryObject('elementBinding', Locality.name().localName(), Locality)

ThoroughfareNumberPrefix = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), CTD_ANON_25, documentation=u'Prefix before the number. A in A12 Archer Street')
Namespace.addCategoryObject('elementBinding', ThoroughfareNumberPrefix.name().localName(), ThoroughfareNumberPrefix)

PostalCode = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')
Namespace.addCategoryObject('elementBinding', PostalCode.name().localName(), PostalCode)

ThoroughfareNumber = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), CTD_ANON_16, documentation=u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc')
Namespace.addCategoryObject('elementBinding', ThoroughfareNumber.name().localName(), ThoroughfareNumber)

AddressDetails = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressDetails'), AddressDetails_, documentation=u'This container defines the details of the address. Can define multiple addresses including tracking address history')
Namespace.addCategoryObject('elementBinding', AddressDetails.name().localName(), AddressDetails)

PostBox = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_15, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')
Namespace.addCategoryObject('elementBinding', PostBox.name().localName(), PostBox)

CountryName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CountryName'), CTD_ANON_45, documentation=u'Specification of the name of a country.')
Namespace.addCategoryObject('elementBinding', CountryName.name().localName(), CountryName)

AddressLine = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')
Namespace.addCategoryObject('elementBinding', AddressLine.name().localName(), AddressLine)

PostOffice = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), CTD_ANON_14, documentation=u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.')
Namespace.addCategoryObject('elementBinding', PostOffice.name().localName(), PostOffice)

AdministrativeArea = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'), CTD_ANON_52, documentation=u'Examples of administrative areas are provinces counties, special regions (such as "Rijnmond"), etc.')
Namespace.addCategoryObject('elementBinding', AdministrativeArea.name().localName(), AdministrativeArea)

PremiseNumberPrefix = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), CTD_ANON_29, documentation=u'A in A12')
Namespace.addCategoryObject('elementBinding', PremiseNumberPrefix.name().localName(), PremiseNumberPrefix)

Premise = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Premise'), CTD_ANON_9, documentation=u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station')
Namespace.addCategoryObject('elementBinding', Premise.name().localName(), Premise)

ThoroughfareNumberSuffix = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), CTD_ANON_32, documentation=u'Suffix after the number. A in 12A Archer Street')
Namespace.addCategoryObject('elementBinding', ThoroughfareNumberSuffix.name().localName(), ThoroughfareNumberSuffix)

xAL = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'xAL'), CTD_ANON_64, documentation=u'Root element for a list of addresses')
Namespace.addCategoryObject('elementBinding', xAL.name().localName(), xAL)

Thoroughfare = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_49, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')
Namespace.addCategoryObject('elementBinding', Thoroughfare.name().localName(), Thoroughfare)

PremiseNumber = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), CTD_ANON_7, documentation=u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.')
Namespace.addCategoryObject('elementBinding', PremiseNumber.name().localName(), PremiseNumber)

PremiseNumberSuffix = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), CTD_ANON_27, documentation=u'A in 12A')
Namespace.addCategoryObject('elementBinding', PremiseNumberSuffix.name().localName(), PremiseNumberSuffix)


CTD_ANON_1._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_2._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


ThoroughfareNameType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_3, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DepartmentName'), CTD_ANON_28, scope=CTD_ANON_3, documentation=u'Specification of the name of a department.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), MailStopType, scope=CTD_ANON_3, documentation=u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=CTD_ANON_3, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))
CTD_ANON_3._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DepartmentName'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_4._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_5._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_6, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumber'), CTD_ANON_65, scope=CTD_ANON_6, documentation=u'Specification of a postcode. The postcode is formatted according to country-specific rules. Example: SW3 0A8-1A, 600074, 2067'))

CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumberExtension'), CTD_ANON_50, scope=CTD_ANON_6, documentation=u'Examples are: 1234 (USA), 1G (UK), etc.'))

CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostTown'), CTD_ANON_53, scope=CTD_ANON_6, documentation=u'A post town is not the same as a locality. A post town can encompass a collection of (small) localities. It can also be a subpart of a locality. An actual post town in Norway is "Bergen".'))
CTD_ANON_6._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostTown'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumberExtension'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_7._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_8._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), CTD_ANON_27, scope=CTD_ANON_9, documentation=u'A in 12A'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseName'), CTD_ANON_36, scope=CTD_ANON_9, documentation=u'Specification of the name of the premise (house, building, park, farm, etc). A premise name is specified when the premise cannot be addressed using a street name plus premise (house) number.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Firm'), FirmType, scope=CTD_ANON_9, documentation=u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from a large mail user address, which contains no street.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), MailStopType, scope=CTD_ANON_9, documentation=u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Premise'), CTD_ANON_9, scope=CTD_ANON_9, documentation=u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRange'), CTD_ANON_23, scope=CTD_ANON_9, documentation=u'Specification for defining the premise number range. Some premises have number as Building C1-C7'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), BuildingNameType, scope=CTD_ANON_9, documentation=u'Specification of the name of a building.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), CTD_ANON_7, scope=CTD_ANON_9, documentation=u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_9, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), CTD_ANON_29, scope=CTD_ANON_9, documentation=u'A in A12'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseLocation'), CTD_ANON_40, scope=CTD_ANON_9, documentation=u'LOBBY, BASEMENT, GROUND FLOOR, etc...'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'), SubPremiseType, scope=CTD_ANON_9, documentation=u'Specification of a single sub-premise. Examples of sub-premises are apartments and suites. Each sub-premise should be uniquely identifiable.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=CTD_ANON_9, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))
CTD_ANON_9._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseName'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRange'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseLocation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
})



CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), CTD_ANON_27, scope=CTD_ANON_10, documentation=u'A in 12A'))

CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_10, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), CTD_ANON_29, scope=CTD_ANON_10, documentation=u'A in A12'))

CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), CTD_ANON_7, scope=CTD_ANON_10, documentation=u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.'))
CTD_ANON_10._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'))),
    ])
})


CTD_ANON_11._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=CTD_ANON_12, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'), LargeMailUserType, scope=CTD_ANON_12, documentation=u'Specification of a large mail user address. Examples of large mail users are postal companies, companies in France with a cedex number, hospitals and airports with their own post code. Large mail user addresses do not have a street name with premise name or premise number in countries like Netherlands. But they have a POBox and street also in countries like France'))

CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LocalityName'), CTD_ANON_13, scope=CTD_ANON_12, documentation=u'Name of the locality'))

CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), CTD_ANON_14, scope=CTD_ANON_12, documentation=u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.'))

CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), PostalRouteType, scope=CTD_ANON_12, documentation=u'A Postal van is specific for a route as in Is`rael, Rural route'))

CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_15, scope=CTD_ANON_12, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.'))

CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_12, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_49, scope=CTD_ANON_12, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK'))

CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), DependentLocalityType, scope=CTD_ANON_12, documentation=u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).'))

CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Premise'), CTD_ANON_9, scope=CTD_ANON_12, documentation=u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station'))
CTD_ANON_12._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LocalityName'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_13._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



MailStopType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=MailStopType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

MailStopType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStopName'), CTD_ANON_68, scope=MailStopType, documentation=u'Name of the the Mail Stop. eg. MSP, MS, etc'))

MailStopType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStopNumber'), CTD_ANON_67, scope=MailStopType, documentation=u'Number of the Mail stop. eg. 123 in MS 123'))
MailStopType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=MailStopType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=MailStopType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStopNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=MailStopType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStopName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=MailStopType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStopNumber'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})



CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeName'), CTD_ANON_70, scope=CTD_ANON_14, documentation=u'Specification of the name of the post office. This can be a rural postoffice where post is delivered or a post office containing post office boxes.'))

CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_15, scope=CTD_ANON_14, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.'))

CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), PostalRouteType, scope=CTD_ANON_14, documentation=u'A Postal van is specific for a route as in Is`rael, Rural route'))

CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=CTD_ANON_14, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeNumber'), CTD_ANON_5, scope=CTD_ANON_14, documentation=u'Specification of the number of the postoffice. Common in rural postoffices'))

CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_14, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))
CTD_ANON_14._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeName'))),
    ])
})



CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumber'), CTD_ANON_4, scope=CTD_ANON_15, documentation=u'Specification of the number of a postbox'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Firm'), FirmType, scope=CTD_ANON_15, documentation=u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from \na large mail user address, which contains no street.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberPrefix'), CTD_ANON_46, scope=CTD_ANON_15, documentation=u'Specification of the prefix of the post box number. eg. A in POBox:A-123'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberExtension'), CTD_ANON_18, scope=CTD_ANON_15, documentation=u'Some countries like USA have POBox as 12345-123'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=CTD_ANON_15, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_15, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberSuffix'), CTD_ANON_43, scope=CTD_ANON_15, documentation=u'Specification of the suffix of the post box number. eg. A in POBox:123A'))
CTD_ANON_15._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberExtension'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberSuffix'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberExtension'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberExtension'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberSuffix'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})



SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseLocation'), CTD_ANON_66, scope=SubPremiseType, documentation=u' Name of the SubPremise Location. eg. LOBBY, BASEMENT, GROUND FLOOR, etc...'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberPrefix'), CTD_ANON_2, scope=SubPremiseType, documentation=u' Prefix of the sub premise number. eg. A in A-12'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=SubPremiseType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumber'), CTD_ANON_34, scope=SubPremiseType, documentation=u' Specification of the identifier of a sub-premise. Examples of sub-premises are apartments and suites. sub-premises in a building are often uniquely identified by means of consecutive\nidentifiers. The identifier can be a number, a letter or any combination of the two. In the latter case, the identifier includes exactly one variable (range) part, which is either a \nnumber or a single letter that is surrounded by fixed parts at the left (prefix) or the right (postfix).'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseName'), CTD_ANON_30, scope=SubPremiseType, documentation=u' Name of the SubPremise'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), BuildingNameType, scope=SubPremiseType, documentation=u'Name of the building'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'), SubPremiseType, scope=SubPremiseType, documentation=u'Specification of a single sub-premise. Examples of sub-premises are apartments and suites. \nEach sub-premise should be uniquely identifiable. SubPremiseType: Specification of the name of a sub-premise type. Possible values not limited to: Suite, Appartment, Floor, Unknown\nMultiple levels within a premise by recursively calling SubPremise Eg. Level 4, Suite 2, Block C'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Firm'), FirmType, scope=SubPremiseType, documentation=u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from a large mail user address, which contains no street.'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberSuffix'), CTD_ANON_31, scope=SubPremiseType, documentation=u' Suffix of the sub premise number. eg. A in 12A'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), MailStopType, scope=SubPremiseType, documentation=u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=SubPremiseType, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))
SubPremiseType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseName'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberSuffix'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseLocation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberSuffix'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberSuffix'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_16._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), CTD_ANON_32, scope=CTD_ANON_17, documentation=u'Suffix after the number. A in 12A Archer Street'))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_17, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), CTD_ANON_16, scope=CTD_ANON_17, documentation=u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc'))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), CTD_ANON_25, scope=CTD_ANON_17, documentation=u'Prefix before the number. A in A12 Archer Street'))
CTD_ANON_17._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'))),
    ])
})



DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_15, scope=DependentLocalityType, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=DependentLocalityType, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'), LargeMailUserType, scope=DependentLocalityType, documentation=u'Specification of a large mail user address. Examples of large mail users are postal companies, companies in France with a cedex number, hospitals and airports with their own post code. Large mail user addresses do not have a street name with premise name or premise number in countries like Netherlands. But they have a POBox and street also in countries like France'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), CTD_ANON_14, scope=DependentLocalityType, documentation=u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityNumber'), CTD_ANON_11, scope=DependentLocalityType, documentation=u'Number of the dependent locality. Some areas are numbered. Eg. SECTOR 5 in a Suburb as in India or SOI SUKUMVIT 10 as in Thailand'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), PostalRouteType, scope=DependentLocalityType, documentation=u' A Postal van is specific for a route as in Is`rael, Rural route'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=DependentLocalityType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_49, scope=DependentLocalityType, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), DependentLocalityType, scope=DependentLocalityType, documentation=u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Premise'), CTD_ANON_9, scope=DependentLocalityType, documentation=u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityName'), CTD_ANON_54, scope=DependentLocalityType, documentation=u'Name of the dependent locality'))
DependentLocalityType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityName'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
    ])
})


CTD_ANON_18._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_19._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



AddressLinesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=AddressLinesType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))
AddressLinesType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressLinesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressLinesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_20._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_21._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_22._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


ThoroughfareTrailingTypeType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeTo'), CTD_ANON_10, scope=CTD_ANON_23, documentation=u'End number details of the premise number range'))

CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeFrom'), CTD_ANON_44, scope=CTD_ANON_23, documentation=u'Start number details of the premise number range'))
CTD_ANON_23._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeFrom'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeTo'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})


CTD_ANON_24._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_25._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_26._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_27._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_28._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_30._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_31._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), BuildingNameType, scope=LargeMailUserType, documentation=u'Name of the building'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_49, scope=LargeMailUserType, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=LargeMailUserType, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=LargeMailUserType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserIdentifier'), CTD_ANON_42, scope=LargeMailUserType, documentation=u'Specification of the identification number of a large mail user. An example are the Cedex codes in France.'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Department'), CTD_ANON_3, scope=LargeMailUserType, documentation=u'Subdivision in the firm: School of Physics at Victoria University (School of Physics is the department)'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserName'), CTD_ANON_21, scope=LargeMailUserType, documentation=u'Name of the large mail user. eg. Smith Ford International airport'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_15, scope=LargeMailUserType, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.'))
LargeMailUserType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserIdentifier'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Department'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserName'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Department'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
    ])
})


CTD_ANON_32._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



PostalRouteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=PostalRouteType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

PostalRouteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteName'), CTD_ANON_1, scope=PostalRouteType, documentation=u' Name of the Postal Route'))

PostalRouteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_15, scope=PostalRouteType, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.'))

PostalRouteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteNumber'), CTD_ANON_69, scope=PostalRouteType, documentation=u' Number of the Postal Route'))
PostalRouteType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PostalRouteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteName'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=PostalRouteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=PostalRouteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteNumber'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=PostalRouteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteName'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PostalRouteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PostalRouteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_33._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_34._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_49, scope=AddressDetails_, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Address'), CTD_ANON_37, scope=AddressDetails_, documentation=u'Address as one line of free text'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalServiceElements'), CTD_ANON_56, scope=AddressDetails_, documentation=u'Postal authorities use specific postal service data to expedient delivery of mail'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'), CTD_ANON_52, scope=AddressDetails_, documentation=u'Examples of administrative areas are provinces counties, special regions (such as "Rijnmond"), etc.'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLines'), AddressLinesType, scope=AddressDetails_, documentation=u'Container for Address lines'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Locality'), CTD_ANON_12, scope=AddressDetails_, documentation=u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Country'), CTD_ANON_39, scope=AddressDetails_, documentation=u'Specification of a country'))
AddressDetails_._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalServiceElements'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Address'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLines'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Locality'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Country'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Address'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLines'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Locality'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Country'))),
    ])
})


CTD_ANON_35._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



FirmType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=FirmType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

FirmType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FirmName'), CTD_ANON_33, scope=FirmType, documentation=u'Name of the firm'))

FirmType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), MailStopType, scope=FirmType, documentation=u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.'))

FirmType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Department'), CTD_ANON_3, scope=FirmType, documentation=u'Subdivision in the firm: School of Physics at Victoria University (School of Physics is the department)'))

FirmType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=FirmType, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))
FirmType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Department'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FirmName'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_36._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_37._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


BuildingNameType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


ThoroughfarePreDirectionType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_39._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CountryNameCode'), CTD_ANON_19, scope=CTD_ANON_39, documentation=u'A country code according to the specified scheme'))

CTD_ANON_39._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'), CTD_ANON_52, scope=CTD_ANON_39, documentation=u'Examples of administrative areas are provinces counties, special regions (such as "Rijnmond"), etc.'))

CTD_ANON_39._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Locality'), CTD_ANON_12, scope=CTD_ANON_39, documentation=u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.'))

CTD_ANON_39._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_39, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_39._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_49, scope=CTD_ANON_39, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK'))

CTD_ANON_39._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CountryName'), CTD_ANON_45, scope=CTD_ANON_39, documentation=u'Specification of the name of a country.'))
CTD_ANON_39._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_39._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Locality'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_39._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CountryNameCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_39._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_39._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_39._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CountryName'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_39._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_40._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_41._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_42._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_43._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_44._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), CTD_ANON_27, scope=CTD_ANON_44, documentation=u'A in 12A'))

CTD_ANON_44._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_44, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_44._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), CTD_ANON_7, scope=CTD_ANON_44, documentation=u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.'))

CTD_ANON_44._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), CTD_ANON_29, scope=CTD_ANON_44, documentation=u'A in A12'))
CTD_ANON_44._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'))),
    ])
})


CTD_ANON_45._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


ThoroughfarePostDirectionType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_46._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_47._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_48._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'), ThoroughfareNameType, scope=CTD_ANON_49, documentation=u'Specification of the name of a Thoroughfare (also dependant street name): street name, canal name, etc.'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), CTD_ANON_32, scope=CTD_ANON_49, documentation=u'Suffix after the number. A in 12A Archer Street'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_49, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'), ThoroughfareTrailingTypeType, scope=CTD_ANON_49, documentation=u'Appears after the thoroughfare name. Ed. British: Baker Lane, where Lane is the trailing type.'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Firm'), FirmType, scope=CTD_ANON_49, documentation=u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from \na large mail user address, which contains no street.'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Premise'), CTD_ANON_9, scope=CTD_ANON_49, documentation=u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'), ThoroughfareLeadingTypeType, scope=CTD_ANON_49, documentation=u'Appears before the thoroughfare name. Ed. Spanish: Avenida Aurora, where Avenida is the leading type / French: Rue Moliere, where Rue is the leading type.'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'), ThoroughfarePostDirectionType, scope=CTD_ANON_49, documentation=u'221-bis Baker Street North, where North is the post-direction. The post-direction appears after the name.'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), DependentLocalityType, scope=CTD_ANON_49, documentation=u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), CTD_ANON_16, scope=CTD_ANON_49, documentation=u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentThoroughfare'), CTD_ANON_60, scope=CTD_ANON_49, documentation=u'DependentThroughfare is related to a street; occurs in GB, IE, ES, PT'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=CTD_ANON_49, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection'), ThoroughfarePreDirectionType, scope=CTD_ANON_49, documentation=u'North Baker Street, where North is the pre-direction. The direction appears before the name.'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberRange'), CTD_ANON_59, scope=CTD_ANON_49, documentation=u'A container to represent a range of numbers (from x thru y)for a thoroughfare. eg. 1-2 Albert Av'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), CTD_ANON_25, scope=CTD_ANON_49, documentation=u'Prefix before the number. A in A12 Archer Street'))
CTD_ANON_49._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentThoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberRange'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentThoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentThoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentThoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentThoroughfare'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'))),
    ])
})


CTD_ANON_50._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_51._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), CTD_ANON_32, scope=CTD_ANON_51, documentation=u'Suffix after the number. A in 12A Archer Street'))

CTD_ANON_51._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_51, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_51._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), CTD_ANON_25, scope=CTD_ANON_51, documentation=u'Prefix before the number. A in A12 Archer Street'))

CTD_ANON_51._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), CTD_ANON_16, scope=CTD_ANON_51, documentation=u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc'))
CTD_ANON_51._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_51._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_51._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_51._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_51._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_51._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_51._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_51._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_51._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'))),
    ])
})



CTD_ANON_52._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeAreaName'), CTD_ANON_55, scope=CTD_ANON_52, documentation=u' Name of the administrative area. eg. MI in USA, NSW in Australia'))

CTD_ANON_52._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Locality'), CTD_ANON_12, scope=CTD_ANON_52, documentation=u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.'))

CTD_ANON_52._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_52, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_52._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeArea'), CTD_ANON_58, scope=CTD_ANON_52, documentation=u' Specification of a sub-administrative area. An example of a sub-administrative areas is a county. There are two places where the name of an administrative \narea can be specified and in this case, one becomes sub-administrative area.'))

CTD_ANON_52._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=CTD_ANON_52, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_52._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), CTD_ANON_14, scope=CTD_ANON_52, documentation=u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.'))
CTD_ANON_52._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_52._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Locality'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_52._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeAreaName'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_52._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_52._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_52._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_52._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_52._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Locality'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_52._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_52._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})



CTD_ANON_53._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostTownSuffix'), CTD_ANON_26, scope=CTD_ANON_53, documentation=u'GENERAL PO in MIAMI GENERAL PO'))

CTD_ANON_53._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_53, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_53._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostTownName'), CTD_ANON_22, scope=CTD_ANON_53, documentation=u'Name of the post town'))
CTD_ANON_53._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_53._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_53._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostTownName'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_53._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostTownSuffix'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


CTD_ANON_54._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


ThoroughfareLeadingTypeType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_55._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_56._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Barcode'), CTD_ANON_35, scope=CTD_ANON_56, documentation=u'Required for some postal services'))

CTD_ANON_56._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressIdentifier'), CTD_ANON_57, scope=CTD_ANON_56, documentation=u'A unique identifier of an address assigned by postal authorities. Example: DPID in Australia'))

CTD_ANON_56._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SortingCode'), CTD_ANON_38, scope=CTD_ANON_56, documentation=u'Used for sorting addresses. Values may for example be CEDEX 16 (France)'))

CTD_ANON_56._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'), CTD_ANON_20, scope=CTD_ANON_56, documentation=u'Longtitude of delivery address'))

CTD_ANON_56._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'), CTD_ANON_47, scope=CTD_ANON_56, documentation=u'any postal service elements not covered by the container can be represented using this element'))

CTD_ANON_56._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyLineCode'), CTD_ANON_48, scope=CTD_ANON_56, documentation=u'Required for some postal services'))

CTD_ANON_56._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitude'), CTD_ANON_41, scope=CTD_ANON_56, documentation=u'Latitude of delivery address'))

CTD_ANON_56._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection'), CTD_ANON_24, scope=CTD_ANON_56, documentation=u'Latitude direction of delivery address;N = North and S = South'))

CTD_ANON_56._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'), CTD_ANON_62, scope=CTD_ANON_56, documentation=u'Longtitude direction of delivery address;N=North and S=South'))

CTD_ANON_56._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EndorsementLineCode'), CTD_ANON_63, scope=CTD_ANON_56, documentation=u'Directly affects postal service distribution'))
CTD_ANON_56._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressIdentifier'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyLineCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Barcode'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SortingCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EndorsementLineCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyLineCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Barcode'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SortingCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Barcode'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SortingCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitude'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SortingCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_56._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_57._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_58._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_58, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_58._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeAreaName'), CTD_ANON_61, scope=CTD_ANON_58, documentation=u' Name of the sub-administrative area'))

CTD_ANON_58._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Locality'), CTD_ANON_12, scope=CTD_ANON_58, documentation=u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.'))

CTD_ANON_58._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), CTD_ANON_14, scope=CTD_ANON_58, documentation=u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.'))

CTD_ANON_58._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_6, scope=CTD_ANON_58, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))
CTD_ANON_58._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_58._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_58._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_58._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_58._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeAreaName'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_58._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Locality'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})



CTD_ANON_59._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberTo'), CTD_ANON_51, scope=CTD_ANON_59, documentation=u'Ending number in the range'))

CTD_ANON_59._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_59, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_59._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberFrom'), CTD_ANON_17, scope=CTD_ANON_59, documentation=u'Starting number in the range'))
CTD_ANON_59._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_59._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_59._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberFrom'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_59._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberTo'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON_8, scope=CTD_ANON_60, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection'), ThoroughfarePreDirectionType, scope=CTD_ANON_60, documentation=u'North Baker Street, where North is the pre-direction. The direction appears before the name.'))

CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'), ThoroughfarePostDirectionType, scope=CTD_ANON_60, documentation=u'221-bis Baker Street North, where North is the post-direction. The post-direction appears after the name.'))

CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'), ThoroughfareLeadingTypeType, scope=CTD_ANON_60, documentation=u'Appears before the thoroughfare name. Ed. Spanish: Avenida Aurora, where Avenida is the leading type / French: Rue Moliere, where Rue is the leading type.'))

CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'), ThoroughfareNameType, scope=CTD_ANON_60, documentation=u'Specification of the name of a Thoroughfare (also dependant street name): street name, canal name, etc.'))

CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'), ThoroughfareTrailingTypeType, scope=CTD_ANON_60, documentation=u'Appears after the thoroughfare name. Ed. British: Baker Lane, where Lane is the trailing type.'))
CTD_ANON_60._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_61._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_62._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_63._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})



CTD_ANON_64._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressDetails'), AddressDetails_, scope=CTD_ANON_64, documentation=u'This container defines the details of the address. Can define multiple addresses including tracking address history'))
CTD_ANON_64._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_64._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressDetails'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_64._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressDetails'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))),
    ])
})


CTD_ANON_65._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_66._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_67._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_68._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_69._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})


CTD_ANON_70._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
    ])
})
