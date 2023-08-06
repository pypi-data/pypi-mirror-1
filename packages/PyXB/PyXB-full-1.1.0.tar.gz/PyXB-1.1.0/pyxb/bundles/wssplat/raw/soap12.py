# ./pyxb/bundles/wssplat/raw/soap12.py
# PyXB bindings for NamespaceModule
# NSM:d8b77ba08b421cd2387db6ece722305a4cdf2cdc
# Generated 2009-11-30 18:08:40.043898 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:ad9e9a20-de0d-11de-a3d2-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.binding.xml_

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2003/05/soap-envelope', create_if_missing=True)
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
class faultcodeEnum (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'faultcodeEnum')
    _Documentation = None
faultcodeEnum._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=faultcodeEnum, enum_prefix=None)
faultcodeEnum.tnsDataEncodingUnknown = faultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'tns:DataEncodingUnknown')
faultcodeEnum.tnsMustUnderstand = faultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'tns:MustUnderstand')
faultcodeEnum.tnsReceiver = faultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'tns:Receiver')
faultcodeEnum.tnsSender = faultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'tns:Sender')
faultcodeEnum.tnsVersionMismatch = faultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'tns:VersionMismatch')
faultcodeEnum._InitializeFacetMap(faultcodeEnum._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'faultcodeEnum', faultcodeEnum)

# Complex type subcode with content type ELEMENT_ONLY
class subcode (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'subcode')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2003/05/soap-envelope}Subcode uses Python identifier Subcode
    __Subcode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Subcode'), 'Subcode', '__httpwww_w3_org200305soap_envelope_subcode_httpwww_w3_org200305soap_envelopeSubcode', False)

    
    Subcode = property(__Subcode.value, __Subcode.set, None, None)

    
    # Element {http://www.w3.org/2003/05/soap-envelope}Value uses Python identifier Value
    __Value = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Value'), 'Value', '__httpwww_w3_org200305soap_envelope_subcode_httpwww_w3_org200305soap_envelopeValue', False)

    
    Value = property(__Value.value, __Value.set, None, None)


    _ElementMap = {
        __Subcode.name() : __Subcode,
        __Value.name() : __Value
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'subcode', subcode)


# Complex type NotUnderstoodType with content type EMPTY
class NotUnderstoodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'NotUnderstoodType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute qname uses Python identifier qname
    __qname = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'qname'), 'qname', '__httpwww_w3_org200305soap_envelope_NotUnderstoodType_qname', pyxb.binding.datatypes.QName, required=True)
    
    qname = property(__qname.value, __qname.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __qname.name() : __qname
    }
Namespace.addCategoryObject('typeBinding', u'NotUnderstoodType', NotUnderstoodType)


# Complex type Body_ with content type ELEMENT_ONLY
class Body_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Body')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2003/05/soap-envelope'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Body', Body_)


# Complex type detail with content type ELEMENT_ONLY
class detail (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'detail')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2003/05/soap-envelope'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'detail', detail)


# Complex type Header_ with content type ELEMENT_ONLY
class Header_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Header')
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2003/05/soap-envelope'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Header', Header_)


# Complex type Fault_ with content type ELEMENT_ONLY
class Fault_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Fault')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2003/05/soap-envelope}Detail uses Python identifier Detail
    __Detail = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Detail'), 'Detail', '__httpwww_w3_org200305soap_envelope_Fault__httpwww_w3_org200305soap_envelopeDetail', False)

    
    Detail = property(__Detail.value, __Detail.set, None, None)

    
    # Element {http://www.w3.org/2003/05/soap-envelope}Code uses Python identifier Code
    __Code = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Code'), 'Code', '__httpwww_w3_org200305soap_envelope_Fault__httpwww_w3_org200305soap_envelopeCode', False)

    
    Code = property(__Code.value, __Code.set, None, None)

    
    # Element {http://www.w3.org/2003/05/soap-envelope}Reason uses Python identifier Reason
    __Reason = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Reason'), 'Reason', '__httpwww_w3_org200305soap_envelope_Fault__httpwww_w3_org200305soap_envelopeReason', False)

    
    Reason = property(__Reason.value, __Reason.set, None, None)

    
    # Element {http://www.w3.org/2003/05/soap-envelope}Node uses Python identifier Node
    __Node = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Node'), 'Node', '__httpwww_w3_org200305soap_envelope_Fault__httpwww_w3_org200305soap_envelopeNode', False)

    
    Node = property(__Node.value, __Node.set, None, None)

    
    # Element {http://www.w3.org/2003/05/soap-envelope}Role uses Python identifier Role
    __Role = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Role'), 'Role', '__httpwww_w3_org200305soap_envelope_Fault__httpwww_w3_org200305soap_envelopeRole', False)

    
    Role = property(__Role.value, __Role.set, None, None)


    _ElementMap = {
        __Detail.name() : __Detail,
        __Code.name() : __Code,
        __Reason.name() : __Reason,
        __Node.name() : __Node,
        __Role.name() : __Role
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Fault', Fault_)


# Complex type faultcode with content type ELEMENT_ONLY
class faultcode (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'faultcode')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2003/05/soap-envelope}Subcode uses Python identifier Subcode
    __Subcode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Subcode'), 'Subcode', '__httpwww_w3_org200305soap_envelope_faultcode_httpwww_w3_org200305soap_envelopeSubcode', False)

    
    Subcode = property(__Subcode.value, __Subcode.set, None, None)

    
    # Element {http://www.w3.org/2003/05/soap-envelope}Value uses Python identifier Value
    __Value = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Value'), 'Value', '__httpwww_w3_org200305soap_envelope_faultcode_httpwww_w3_org200305soap_envelopeValue', False)

    
    Value = property(__Value.value, __Value.set, None, None)


    _ElementMap = {
        __Subcode.name() : __Subcode,
        __Value.name() : __Value
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'faultcode', faultcode)


# Complex type UpgradeType with content type ELEMENT_ONLY
class UpgradeType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UpgradeType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2003/05/soap-envelope}SupportedEnvelope uses Python identifier SupportedEnvelope
    __SupportedEnvelope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SupportedEnvelope'), 'SupportedEnvelope', '__httpwww_w3_org200305soap_envelope_UpgradeType_httpwww_w3_org200305soap_envelopeSupportedEnvelope', True)

    
    SupportedEnvelope = property(__SupportedEnvelope.value, __SupportedEnvelope.set, None, None)


    _ElementMap = {
        __SupportedEnvelope.name() : __SupportedEnvelope
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'UpgradeType', UpgradeType)


# Complex type faultreason with content type ELEMENT_ONLY
class faultreason (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'faultreason')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2003/05/soap-envelope}Text uses Python identifier Text
    __Text = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Text'), 'Text', '__httpwww_w3_org200305soap_envelope_faultreason_httpwww_w3_org200305soap_envelopeText', True)

    
    Text = property(__Text.value, __Text.set, None, None)


    _ElementMap = {
        __Text.name() : __Text
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'faultreason', faultreason)


# Complex type reasontext with content type SIMPLE
class reasontext (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'reasontext')
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute {http://www.w3.org/XML/1998/namespace}lang uses Python identifier lang
    __lang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.XML, 'lang'), 'lang', '__httpwww_w3_org200305soap_envelope_reasontext_httpwww_w3_orgXML1998namespacelang', pyxb.binding.xml_.STD_ANON_lang, required=True)
    
    lang = property(__lang.value, __lang.set, None, u'\n    \n    \n   ')


    _ElementMap = {
        
    }
    _AttributeMap = {
        __lang.name() : __lang
    }
Namespace.addCategoryObject('typeBinding', u'reasontext', reasontext)


# Complex type SupportedEnvType with content type EMPTY
class SupportedEnvType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SupportedEnvType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute qname uses Python identifier qname
    __qname = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'qname'), 'qname', '__httpwww_w3_org200305soap_envelope_SupportedEnvType_qname', pyxb.binding.datatypes.QName, required=True)
    
    qname = property(__qname.value, __qname.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __qname.name() : __qname
    }
Namespace.addCategoryObject('typeBinding', u'SupportedEnvType', SupportedEnvType)


# Complex type Envelope_ with content type ELEMENT_ONLY
class Envelope_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Envelope')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2003/05/soap-envelope}Body uses Python identifier Body
    __Body = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Body'), 'Body', '__httpwww_w3_org200305soap_envelope_Envelope__httpwww_w3_org200305soap_envelopeBody', False)

    
    Body = property(__Body.value, __Body.set, None, None)

    
    # Element {http://www.w3.org/2003/05/soap-envelope}Header uses Python identifier Header
    __Header = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Header'), 'Header', '__httpwww_w3_org200305soap_envelope_Envelope__httpwww_w3_org200305soap_envelopeHeader', False)

    
    Header = property(__Header.value, __Header.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2003/05/soap-envelope'))

    _ElementMap = {
        __Body.name() : __Body,
        __Header.name() : __Header
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Envelope', Envelope_)


NotUnderstood = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NotUnderstood'), NotUnderstoodType)
Namespace.addCategoryObject('elementBinding', NotUnderstood.name().localName(), NotUnderstood)

Header = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Header'), Header_)
Namespace.addCategoryObject('elementBinding', Header.name().localName(), Header)

Fault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Fault'), Fault_)
Namespace.addCategoryObject('elementBinding', Fault.name().localName(), Fault)

Upgrade = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Upgrade'), UpgradeType)
Namespace.addCategoryObject('elementBinding', Upgrade.name().localName(), Upgrade)

Body = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Body'), Body_)
Namespace.addCategoryObject('elementBinding', Body.name().localName(), Body)

Envelope = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Envelope'), Envelope_)
Namespace.addCategoryObject('elementBinding', Envelope.name().localName(), Envelope)



subcode._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Subcode'), subcode, scope=subcode))

subcode._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Value'), pyxb.binding.datatypes.QName, scope=subcode))
subcode._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=subcode._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Value'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=subcode._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Subcode'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})


Body_._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})


detail._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})


Header_._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})



Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Detail'), detail, scope=Fault_))

Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Code'), faultcode, scope=Fault_))

Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Reason'), faultreason, scope=Fault_))

Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Node'), pyxb.binding.datatypes.anyURI, scope=Fault_))

Fault_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Role'), pyxb.binding.datatypes.anyURI, scope=Fault_))
Fault_._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Code'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Reason'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Role'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Detail'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Node'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Detail'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Role'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=Fault_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Detail'))),
    ])
})



faultcode._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Subcode'), subcode, scope=faultcode))

faultcode._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Value'), faultcodeEnum, scope=faultcode))
faultcode._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=faultcode._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Value'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=faultcode._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Subcode'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



UpgradeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SupportedEnvelope'), SupportedEnvType, scope=UpgradeType))
UpgradeType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=UpgradeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupportedEnvelope'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=UpgradeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupportedEnvelope'))),
    ])
})



faultreason._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Text'), reasontext, scope=faultreason))
faultreason._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=faultreason._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Text'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=faultreason._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Text'))),
    ])
})



Envelope_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Body'), Body_, scope=Envelope_))

Envelope_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Header'), Header_, scope=Envelope_))
Envelope_._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=Envelope_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Header'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Envelope_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Body'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=Envelope_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Body'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})
