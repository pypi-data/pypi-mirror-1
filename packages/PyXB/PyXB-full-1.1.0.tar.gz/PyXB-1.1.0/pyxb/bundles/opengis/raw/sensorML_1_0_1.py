# ./pyxb/bundles/opengis/raw/sensorML_1_0_1.py
# PyXB bindings for NamespaceModule
# NSM:08166200600e134470ff8bd9e596fb5c78092003
# Generated 2009-11-30 18:10:37.556106 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:f1875812-de0d-11de-9282-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.misc.xlinks
import pyxb.bundles.opengis.gml
import pyxb.bundles.opengis.swe_1_0_1
import pyxb.bundles.opengis.ic_ism_2_1

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/sensorML/1.0.1', create_if_missing=True)
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
class linkRef (pyxb.binding.datatypes.token):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'linkRef')
    _Documentation = None
linkRef._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'linkRef', linkRef)

# Complex type CTD_ANON_1 with content type ELEMENT_ONLY
class CTD_ANON_1 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}Document uses Python identifier Document
    __Document = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Document'), 'Document', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_1_httpwww_opengis_netsensorML1_0_1Document', False)

    
    Document = property(__Document.value, __Document.set, None, u'Document record with date/time, version, author, etc. pointing to an online resource related to the enclosing object')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}DocumentList uses Python identifier DocumentList
    __DocumentList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DocumentList'), 'DocumentList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_1_httpwww_opengis_netsensorML1_0_1DocumentList', False)

    
    DocumentList = property(__DocumentList.value, __DocumentList.set, None, u'List of documents related to the enclosing object')

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_1_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_1_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_1_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_1_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_1_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_1_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_1_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_1_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        __Document.name() : __Document,
        __DocumentList.name() : __DocumentList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __href.name() : __href,
        __title.name() : __title,
        __type.name() : __type,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __actuate.name() : __actuate,
        __role.name() : __role
    }



# Complex type CTD_ANON_2 with content type EMPTY
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_2_ref', linkRef)
    
    ref = property(__ref.value, __ref.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __ref.name() : __ref
    }



# Complex type CTD_ANON_3 with content type ELEMENT_ONLY
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}Person uses Python identifier Person
    __Person = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Person'), 'Person', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_3_httpwww_opengis_netsensorML1_0_1Person', False)

    
    Person = property(__Person.value, __Person.set, None, u'based on IC:DMMS')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}ResponsibleParty uses Python identifier ResponsibleParty
    __ResponsibleParty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ResponsibleParty'), 'ResponsibleParty', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_3_httpwww_opengis_netsensorML1_0_1ResponsibleParty', False)

    
    ResponsibleParty = property(__ResponsibleParty.value, __ResponsibleParty.set, None, u'based on ISO 19115')

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_3_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_3_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_3_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_3_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_3_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_3_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_3_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_3_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        __Person.name() : __Person,
        __ResponsibleParty.name() : __ResponsibleParty
    }
    _AttributeMap = {
        __arcrole.name() : __arcrole,
        __remoteSchema.name() : __remoteSchema,
        __href.name() : __href,
        __show.name() : __show,
        __title.name() : __title,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __role.name() : __role
    }



# Complex type CTD_ANON_4 with content type ELEMENT_ONLY
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}Security uses Python identifier Security
    __Security = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Security'), 'Security', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_4_httpwww_opengis_netsensorML1_0_1Security', False)

    
    Security = property(__Security.value, __Security.set, None, u'based on IC:ISM definition')


    _ElementMap = {
        __Security.name() : __Security
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_5 with content type ELEMENT_ONLY
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}Event uses Python identifier Event
    __Event = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Event'), 'Event', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_5_httpwww_opengis_netsensorML1_0_1Event', False)

    
    Event = property(__Event.value, __Event.set, None, u'Event record (change to the object) including a date/time, description, identification and additional references and metadata')

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_5_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_5_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_5_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_5_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_5_name', pyxb.binding.datatypes.token, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_5_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_5_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_5_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_5_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")


    _ElementMap = {
        __Event.name() : __Event
    }
    _AttributeMap = {
        __title.name() : __title,
        __show.name() : __show,
        __type.name() : __type,
        __arcrole.name() : __arcrole,
        __name.name() : __name,
        __role.name() : __role,
        __href.name() : __href,
        __remoteSchema.name() : __remoteSchema,
        __actuate.name() : __actuate
    }



# Complex type AbstractSMLType with content type ELEMENT_ONLY
class AbstractSMLType (pyxb.bundles.opengis.gml.AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractSMLType')
    # Base type is pyxb.bundles.opengis.gml.AbstractFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractSMLType', AbstractSMLType)


# Complex type AbstractProcessType with content type ELEMENT_ONLY
class AbstractProcessType (AbstractSMLType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractProcessType')
    # Base type is AbstractSMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}history uses Python identifier history
    __history = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'history'), 'history', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1history', True)

    
    history = property(__history.value, __history.set, None, u'History of the object described (Recalibration, adjustments, etc...)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}contact uses Python identifier contact
    __contact = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'contact'), 'contact', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1contact', True)

    
    contact = property(__contact.value, __contact.set, None, u'Relevant contacts for that object')

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}classification uses Python identifier classification
    __classification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'classification'), 'classification', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1classification', True)

    
    classification = property(__classification.value, __classification.set, None, u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}keywords uses Python identifier keywords
    __keywords = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'keywords'), 'keywords', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1keywords', True)

    
    keywords = property(__keywords.value, __keywords.set, None, u'Means of providing a list of keywords (with a codeSpace) for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}legalConstraint uses Python identifier legalConstraint
    __legalConstraint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'), 'legalConstraint', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1legalConstraint', True)

    
    legalConstraint = property(__legalConstraint.value, __legalConstraint.set, None, u'Means of providing legal constraints of description')

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}identification uses Python identifier identification
    __identification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'identification'), 'identification', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1identification', True)

    
    identification = property(__identification.value, __identification.set, None, u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary')

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}characteristics uses Python identifier characteristics
    __characteristics = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'characteristics'), 'characteristics', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1characteristics', True)

    
    characteristics = property(__characteristics.value, __characteristics.set, None, u'Characteristic list for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}securityConstraint uses Python identifier securityConstraint
    __securityConstraint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'), 'securityConstraint', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1securityConstraint', False)

    
    securityConstraint = property(__securityConstraint.value, __securityConstraint.set, None, u'Means of providing security constraints of description')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}documentation uses Python identifier documentation
    __documentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'documentation'), 'documentation', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1documentation', True)

    
    documentation = property(__documentation.value, __documentation.set, None, u'Relevant documentation for that object')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}capabilities uses Python identifier capabilities
    __capabilities = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'capabilities'), 'capabilities', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1capabilities', True)

    
    capabilities = property(__capabilities.value, __capabilities.set, None, u'Capability list for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}validTime uses Python identifier validTime
    __validTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'validTime'), 'validTime', '__httpwww_opengis_netsensorML1_0_1_AbstractProcessType_httpwww_opengis_netsensorML1_0_1validTime', False)

    
    validTime = property(__validTime.value, __validTime.set, None, u'Means of providing time validity constraint of description')

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractSMLType._ElementMap.copy()
    _ElementMap.update({
        __history.name() : __history,
        __contact.name() : __contact,
        __classification.name() : __classification,
        __keywords.name() : __keywords,
        __legalConstraint.name() : __legalConstraint,
        __identification.name() : __identification,
        __characteristics.name() : __characteristics,
        __securityConstraint.name() : __securityConstraint,
        __documentation.name() : __documentation,
        __capabilities.name() : __capabilities,
        __validTime.name() : __validTime
    })
    _AttributeMap = AbstractSMLType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractProcessType', AbstractProcessType)


# Complex type AbstractRestrictedProcessType with content type ELEMENT_ONLY
class AbstractRestrictedProcessType (AbstractProcessType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractRestrictedProcessType')
    # Base type is AbstractProcessType
    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractProcessType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = AbstractProcessType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractRestrictedProcessType', AbstractRestrictedProcessType)


# Complex type AbstractPureProcessType with content type ELEMENT_ONLY
class AbstractPureProcessType (AbstractRestrictedProcessType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractPureProcessType')
    # Base type is AbstractRestrictedProcessType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}inputs uses Python identifier inputs
    __inputs = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'inputs'), 'inputs', '__httpwww_opengis_netsensorML1_0_1_AbstractPureProcessType_httpwww_opengis_netsensorML1_0_1inputs', False)

    
    inputs = property(__inputs.value, __inputs.set, None, u'list of input signals')

    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}outputs uses Python identifier outputs
    __outputs = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'outputs'), 'outputs', '__httpwww_opengis_netsensorML1_0_1_AbstractPureProcessType_httpwww_opengis_netsensorML1_0_1outputs', False)

    
    outputs = property(__outputs.value, __outputs.set, None, u'list of output signals')

    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}parameters uses Python identifier parameters
    __parameters = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'parameters'), 'parameters', '__httpwww_opengis_netsensorML1_0_1_AbstractPureProcessType_httpwww_opengis_netsensorML1_0_1parameters', False)

    
    parameters = property(__parameters.value, __parameters.set, None, u'list of parameters')

    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractRestrictedProcessType._ElementMap.copy()
    _ElementMap.update({
        __inputs.name() : __inputs,
        __outputs.name() : __outputs,
        __parameters.name() : __parameters
    })
    _AttributeMap = AbstractRestrictedProcessType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractPureProcessType', AbstractPureProcessType)


# Complex type ProcessModelType with content type ELEMENT_ONLY
class ProcessModelType (AbstractPureProcessType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ProcessModelType')
    # Base type is AbstractPureProcessType
    
    # Element parameters ({http://www.opengis.net/sensorML/1.0.1}parameters) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractPureProcessType
    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}method uses Python identifier method
    __method = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'method'), 'method', '__httpwww_opengis_netsensorML1_0_1_ProcessModelType_httpwww_opengis_netsensorML1_0_1method', False)

    
    method = property(__method.value, __method.set, None, u'process method')

    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element outputs ({http://www.opengis.net/sensorML/1.0.1}outputs) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractPureProcessType
    
    # Element inputs ({http://www.opengis.net/sensorML/1.0.1}inputs) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractPureProcessType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractPureProcessType._ElementMap.copy()
    _ElementMap.update({
        __method.name() : __method
    })
    _AttributeMap = AbstractPureProcessType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ProcessModelType', ProcessModelType)


# Complex type CTD_ANON_6 with content type ELEMENT_ONLY
class CTD_ANON_6 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}OutputList uses Python identifier OutputList
    __OutputList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OutputList'), 'OutputList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_6_httpwww_opengis_netsensorML1_0_1OutputList', False)

    
    OutputList = property(__OutputList.value, __OutputList.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_6_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_6_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_6_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_6_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_6_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_6_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_6_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_6_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)


    _ElementMap = {
        __OutputList.name() : __OutputList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __show.name() : __show,
        __role.name() : __role,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __title.name() : __title
    }



# Complex type CTD_ANON_7 with content type ELEMENT_ONLY
class CTD_ANON_7 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}ClassifierList uses Python identifier ClassifierList
    __ClassifierList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ClassifierList'), 'ClassifierList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_7_httpwww_opengis_netsensorML1_0_1ClassifierList', False)

    
    ClassifierList = property(__ClassifierList.value, __ClassifierList.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_7_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_7_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_7_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_7_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_7_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_7_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_7_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_7_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        __ClassifierList.name() : __ClassifierList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __type.name() : __type,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __actuate.name() : __actuate,
        __href.name() : __href,
        __role.name() : __role
    }



# Complex type CTD_ANON_8 with content type ELEMENT_ONLY
class CTD_ANON_8 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}IdentifierList uses Python identifier IdentifierList
    __IdentifierList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IdentifierList'), 'IdentifierList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_8_httpwww_opengis_netsensorML1_0_1IdentifierList', False)

    
    IdentifierList = property(__IdentifierList.value, __IdentifierList.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_8_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_8_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_8_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_8_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_8_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_8_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_8_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_8_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __IdentifierList.name() : __IdentifierList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __title.name() : __title,
        __actuate.name() : __actuate,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __role.name() : __role,
        __type.name() : __type
    }



# Complex type CTD_ANON_9 with content type ELEMENT_ONLY
class CTD_ANON_9 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}ProcessChain uses Python identifier ProcessChain
    __ProcessChain = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ProcessChain'), 'ProcessChain', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_9_httpwww_opengis_netsensorML1_0_1ProcessChain', False)

    
    ProcessChain = property(__ProcessChain.value, __ProcessChain.set, None, u'Process formed by chaining sub-processes')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}ImplementationCode uses Python identifier ImplementationCode
    __ImplementationCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ImplementationCode'), 'ImplementationCode', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_9_httpwww_opengis_netsensorML1_0_1ImplementationCode', False)

    
    ImplementationCode = property(__ImplementationCode.value, __ImplementationCode.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_9_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_9_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_9_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_9_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_9_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_9_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_9_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_9_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __ProcessChain.name() : __ProcessChain,
        __ImplementationCode.name() : __ImplementationCode
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __href.name() : __href,
        __actuate.name() : __actuate,
        __title.name() : __title,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __role.name() : __role,
        __type.name() : __type
    }



# Complex type CTD_ANON_10 with content type ELEMENT_ONLY
class CTD_ANON_10 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}ConnectionList uses Python identifier ConnectionList
    __ConnectionList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ConnectionList'), 'ConnectionList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_10_httpwww_opengis_netsensorML1_0_1ConnectionList', False)

    
    ConnectionList = property(__ConnectionList.value, __ConnectionList.set, None, None)


    _ElementMap = {
        __ConnectionList.name() : __ConnectionList
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_11 with content type ELEMENT_ONLY
class CTD_ANON_11 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/swe/1.0.1}AbstractDataRecord uses Python identifier AbstractDataRecord
    __AbstractDataRecord = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'), 'AbstractDataRecord', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_11_httpwww_opengis_netswe1_0_1AbstractDataRecord', False)

    
    AbstractDataRecord = property(__AbstractDataRecord.value, __AbstractDataRecord.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_11_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_11_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_11_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_11_name', pyxb.binding.datatypes.token)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_11_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_11_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_11_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_11_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_11_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        __AbstractDataRecord.name() : __AbstractDataRecord
    }
    _AttributeMap = {
        __arcrole.name() : __arcrole,
        __remoteSchema.name() : __remoteSchema,
        __actuate.name() : __actuate,
        __name.name() : __name,
        __type.name() : __type,
        __show.name() : __show,
        __title.name() : __title,
        __href.name() : __href,
        __role.name() : __role
    }



# Complex type CTD_ANON_12 with content type ELEMENT_ONLY
class CTD_ANON_12 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}ParameterList uses Python identifier ParameterList
    __ParameterList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ParameterList'), 'ParameterList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_12_httpwww_opengis_netsensorML1_0_1ParameterList', False)

    
    ParameterList = property(__ParameterList.value, __ParameterList.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_12_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_12_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_12_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_12_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_12_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_12_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_12_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_12_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        __ParameterList.name() : __ParameterList
    }
    _AttributeMap = {
        __role.name() : __role,
        __remoteSchema.name() : __remoteSchema,
        __show.name() : __show,
        __title.name() : __title,
        __actuate.name() : __actuate,
        __arcrole.name() : __arcrole,
        __type.name() : __type,
        __href.name() : __href
    }



# Complex type CTD_ANON_13 with content type ELEMENT_ONLY
class CTD_ANON_13 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}Person uses Python identifier Person
    __Person = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Person'), 'Person', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_opengis_netsensorML1_0_1Person', False)

    
    Person = property(__Person.value, __Person.set, None, u'based on IC:DMMS')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}ResponsibleParty uses Python identifier ResponsibleParty
    __ResponsibleParty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ResponsibleParty'), 'ResponsibleParty', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_opengis_netsensorML1_0_1ResponsibleParty', False)

    
    ResponsibleParty = property(__ResponsibleParty.value, __ResponsibleParty.set, None, u'based on ISO 19115')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}ContactList uses Python identifier ContactList
    __ContactList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ContactList'), 'ContactList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_opengis_netsensorML1_0_1ContactList', False)

    
    ContactList = property(__ContactList.value, __ContactList.set, None, u'Allows to group several contacts together in a list that can be referenced as a whole')

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_13_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __Person.name() : __Person,
        __ResponsibleParty.name() : __ResponsibleParty,
        __ContactList.name() : __ContactList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __href.name() : __href,
        __role.name() : __role,
        __show.name() : __show,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __actuate.name() : __actuate,
        __type.name() : __type
    }



# Complex type CTD_ANON_14 with content type ELEMENT_ONLY
class CTD_ANON_14 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/gml}TimeInstant uses Python identifier TimeInstant
    __TimeInstant = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TimeInstant'), 'TimeInstant', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_14_httpwww_opengis_netgmlTimeInstant', False)

    
    TimeInstant = property(__TimeInstant.value, __TimeInstant.set, None, None)

    
    # Element {http://www.opengis.net/gml}TimePeriod uses Python identifier TimePeriod
    __TimePeriod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TimePeriod'), 'TimePeriod', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_14_httpwww_opengis_netgmlTimePeriod', False)

    
    TimePeriod = property(__TimePeriod.value, __TimePeriod.set, None, None)


    _ElementMap = {
        __TimeInstant.name() : __TimeInstant,
        __TimePeriod.name() : __TimePeriod
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_15 with content type ELEMENT_ONLY
class CTD_ANON_15 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}output uses Python identifier output
    __output = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'output'), 'output', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_15_httpwww_opengis_netsensorML1_0_1output', True)

    
    output = property(__output.value, __output.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_15_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)


    _ElementMap = {
        __output.name() : __output
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type CTD_ANON_16 with content type ELEMENT_ONLY
class CTD_ANON_16 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/gml}EngineeringCRS uses Python identifier EngineeringCRS
    __EngineeringCRS = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'EngineeringCRS'), 'EngineeringCRS', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_16_httpwww_opengis_netgmlEngineeringCRS', False)

    
    EngineeringCRS = property(__EngineeringCRS.value, __EngineeringCRS.set, None, None)


    _ElementMap = {
        __EngineeringCRS.name() : __EngineeringCRS
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_17 with content type ELEMENT_ONLY
class CTD_ANON_17 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}connection uses Python identifier connection
    __connection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'connection'), 'connection', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_17_httpwww_opengis_netsensorML1_0_1connection', True)

    
    connection = property(__connection.value, __connection.set, None, u'Specify a connection between two elements')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}destinationIndex uses Python identifier destinationIndex
    __destinationIndex = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'destinationIndex'), 'destinationIndex', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_17_httpwww_opengis_netsensorML1_0_1destinationIndex', True)

    
    destinationIndex = property(__destinationIndex.value, __destinationIndex.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}sourceArray uses Python identifier sourceArray
    __sourceArray = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sourceArray'), 'sourceArray', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_17_httpwww_opengis_netsensorML1_0_1sourceArray', False)

    
    sourceArray = property(__sourceArray.value, __sourceArray.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}destinationArray uses Python identifier destinationArray
    __destinationArray = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'destinationArray'), 'destinationArray', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_17_httpwww_opengis_netsensorML1_0_1destinationArray', False)

    
    destinationArray = property(__destinationArray.value, __destinationArray.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}sourceIndex uses Python identifier sourceIndex
    __sourceIndex = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sourceIndex'), 'sourceIndex', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_17_httpwww_opengis_netsensorML1_0_1sourceIndex', False)

    
    sourceIndex = property(__sourceIndex.value, __sourceIndex.set, None, None)


    _ElementMap = {
        __connection.name() : __connection,
        __destinationIndex.name() : __destinationIndex,
        __sourceArray.name() : __sourceArray,
        __destinationArray.name() : __destinationArray,
        __sourceIndex.name() : __sourceIndex
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_18 with content type ELEMENT_ONLY
class CTD_ANON_18 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/swe/1.0.1}Count uses Python identifier Count
    __Count = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Count'), 'Count', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_18_httpwww_opengis_netswe1_0_1Count', False)

    
    Count = property(__Count.value, __Count.set, None, u'Integer number used for a counting value')

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_18_name', pyxb.binding.datatypes.token)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        __Count.name() : __Count
    }
    _AttributeMap = {
        __name.name() : __name
    }



# Complex type CTD_ANON_19 with content type ELEMENT_ONLY
class CTD_ANON_19 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/swe/1.0.1}AbstractDataRecord uses Python identifier AbstractDataRecord
    __AbstractDataRecord = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'), 'AbstractDataRecord', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_19_httpwww_opengis_netswe1_0_1AbstractDataRecord', False)

    
    AbstractDataRecord = property(__AbstractDataRecord.value, __AbstractDataRecord.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_19_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_19_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_19_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_19_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_19_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_19_name', pyxb.binding.datatypes.token)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_19_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_19_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_19_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        __AbstractDataRecord.name() : __AbstractDataRecord
    }
    _AttributeMap = {
        __title.name() : __title,
        __show.name() : __show,
        __remoteSchema.name() : __remoteSchema,
        __type.name() : __type,
        __actuate.name() : __actuate,
        __name.name() : __name,
        __arcrole.name() : __arcrole,
        __role.name() : __role,
        __href.name() : __href
    }



# Complex type CTD_ANON_20 with content type ELEMENT_ONLY
class CTD_ANON_20 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}value uses Python identifier value_
    __value = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'value'), 'value_', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_20_httpwww_opengis_netsensorML1_0_1value', False)

    
    value_ = property(__value.value, __value.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}codeSpace uses Python identifier codeSpace
    __codeSpace = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'codeSpace'), 'codeSpace', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_20_httpwww_opengis_netsensorML1_0_1codeSpace', False)

    
    codeSpace = property(__codeSpace.value, __codeSpace.set, None, None)

    
    # Attribute definition uses Python identifier definition
    __definition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'definition'), 'definition', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_20_definition', pyxb.binding.datatypes.anyURI)
    
    definition = property(__definition.value, __definition.set, None, u'Points to the term definition using a URI. Term definitions are things like uid, shortName, sensorType, application, etc...')


    _ElementMap = {
        __value.name() : __value,
        __codeSpace.name() : __codeSpace
    }
    _AttributeMap = {
        __definition.name() : __definition
    }



# Complex type CTD_ANON_21 with content type ELEMENT_ONLY
class CTD_ANON_21 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}KeywordList uses Python identifier KeywordList
    __KeywordList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeywordList'), 'KeywordList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_21_httpwww_opengis_netsensorML1_0_1KeywordList', False)

    
    KeywordList = property(__KeywordList.value, __KeywordList.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_21_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_21_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_21_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_21_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_21_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_21_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_21_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_21_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __KeywordList.name() : __KeywordList
    }
    _AttributeMap = {
        __role.name() : __role,
        __remoteSchema.name() : __remoteSchema,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __title.name() : __title,
        __show.name() : __show,
        __actuate.name() : __actuate,
        __type.name() : __type
    }



# Complex type CTD_ANON_22 with content type ELEMENT_ONLY
class CTD_ANON_22 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/gml}Point uses Python identifier Point
    __Point = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'Point'), 'Point', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_22_httpwww_opengis_netgmlPoint', False)

    
    Point = property(__Point.value, __Point.set, None, None)

    
    # Element {http://www.opengis.net/gml}_Curve uses Python identifier Curve
    __Curve = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Curve'), 'Curve', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_22_httpwww_opengis_netgml_Curve', False)

    
    Curve = property(__Curve.value, __Curve.set, None, u'The "_Curve" element is the abstract head of the substituition group for all (continuous) curve elements.')

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_22_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_22_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_22_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_22_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_22_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_22_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_22_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_22_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)


    _ElementMap = {
        __Point.name() : __Point,
        __Curve.name() : __Curve
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __show.name() : __show,
        __role.name() : __role,
        __type.name() : __type,
        __actuate.name() : __actuate,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __title.name() : __title
    }



# Complex type CTD_ANON_23 with content type ELEMENT_ONLY
class CTD_ANON_23 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}facsimile uses Python identifier facsimile
    __facsimile = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'facsimile'), 'facsimile', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_23_httpwww_opengis_netsensorML1_0_1facsimile', True)

    
    facsimile = property(__facsimile.value, __facsimile.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}voice uses Python identifier voice
    __voice = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'voice'), 'voice', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_23_httpwww_opengis_netsensorML1_0_1voice', True)

    
    voice = property(__voice.value, __voice.set, None, None)


    _ElementMap = {
        __facsimile.name() : __facsimile,
        __voice.name() : __voice
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_24 with content type ELEMENT_ONLY
class CTD_ANON_24 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}member uses Python identifier member
    __member = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'member'), 'member', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_24_httpwww_opengis_netsensorML1_0_1member', True)

    
    member = property(__member.value, __member.set, None, None)

    
    # Element {http://www.opengis.net/gml}description uses Python identifier description
    __description = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), 'description', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_24_httpwww_opengis_netgmldescription', False)

    
    description = property(__description.value, __description.set, None, u'Contains a simple text description of the object, or refers to an external description.')

    
    # Attribute {http://www.opengis.net/gml}id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_24_httpwww_opengis_netgmlid', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, u'Database handle for the object.  It is of XML type ID, so is constrained to be unique in the XML document within which it occurs.  An external identifier for the object in the form of a URI may be constructed using standard XML and XPointer methods.  This is done by concatenating the URI for the document, a fragment separator, and the value of the id attribute.')


    _ElementMap = {
        __member.name() : __member,
        __description.name() : __description
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type CTD_ANON_25 with content type ELEMENT_ONLY
class CTD_ANON_25 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}dataLinkLayer uses Python identifier dataLinkLayer
    __dataLinkLayer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'dataLinkLayer'), 'dataLinkLayer', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_25_httpwww_opengis_netsensorML1_0_1dataLinkLayer', False)

    
    dataLinkLayer = property(__dataLinkLayer.value, __dataLinkLayer.set, None, u'Layer 2 of the OSI model. Provides functional and procedural means of transfering data between network entities and detecting/correcting errors. (Ex: Ethernet, 802.11, Token ring, ATM, Fibre Channel)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}networkLayer uses Python identifier networkLayer
    __networkLayer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'networkLayer'), 'networkLayer', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_25_httpwww_opengis_netsensorML1_0_1networkLayer', False)

    
    networkLayer = property(__networkLayer.value, __networkLayer.set, None, u'Layer 3 of the OSI model. Provides functional and procedural means of transfering data from source to destination via one or more networks while insuring QoS. (Ex: IP, ICMP, ARP, IPSec, IPX)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}applicationLayer uses Python identifier applicationLayer
    __applicationLayer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'applicationLayer'), 'applicationLayer', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_25_httpwww_opengis_netsensorML1_0_1applicationLayer', False)

    
    applicationLayer = property(__applicationLayer.value, __applicationLayer.set, None, u'Layer 7 of the OSI model. Provides a means for the user to access information on the network through an application. (Ex: HTTP, SMTP, FTP, XMPP, Telnet, NTP, RTP, NFS)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}serviceLayer uses Python identifier serviceLayer
    __serviceLayer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'serviceLayer'), 'serviceLayer', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_25_httpwww_opengis_netsensorML1_0_1serviceLayer', False)

    
    serviceLayer = property(__serviceLayer.value, __serviceLayer.set, None, u'Layer 8 (not in OSI). Type of web service used to access the data. (Ex: SOS, WCS, WFS)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}presentationLayer uses Python identifier presentationLayer
    __presentationLayer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'presentationLayer'), 'presentationLayer', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_25_httpwww_opengis_netsensorML1_0_1presentationLayer', False)

    
    presentationLayer = property(__presentationLayer.value, __presentationLayer.set, None, u'Layer 6 of the OSI model. Transforms the data to provide a standard interface for the Application layer. (Ex: SSL, TLS, ASCII, MIDI, MPEG, SWECommon)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}physicalLayer uses Python identifier physicalLayer
    __physicalLayer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'physicalLayer'), 'physicalLayer', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_25_httpwww_opengis_netsensorML1_0_1physicalLayer', False)

    
    physicalLayer = property(__physicalLayer.value, __physicalLayer.set, None, u'Layer 1 of the OSI model. Provides all electrical and physical characteristics of the connection including pin layouts, voltages, cables specifcations, etc... (Ex: RS232, 100BASE-T, DSL, 802.11g)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}mechanicalLayer uses Python identifier mechanicalLayer
    __mechanicalLayer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'), 'mechanicalLayer', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_25_httpwww_opengis_netsensorML1_0_1mechanicalLayer', False)

    
    mechanicalLayer = property(__mechanicalLayer.value, __mechanicalLayer.set, None, u'Layer 0 (not is OSI). Type of connector used. (Ex: DB9, DB25, RJ45, RJ11, MINIDIN-8, USB-A, USB-B)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}sessionLayer uses Python identifier sessionLayer
    __sessionLayer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sessionLayer'), 'sessionLayer', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_25_httpwww_opengis_netsensorML1_0_1sessionLayer', False)

    
    sessionLayer = property(__sessionLayer.value, __sessionLayer.set, None, u'Layer 5 of the OSI model. Controls the dialogues (sessions) between computers by establishing, managing and terminating connections between the local and remote application. (Ex: NetBios, TCP session establishment)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}transportLayer uses Python identifier transportLayer
    __transportLayer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'transportLayer'), 'transportLayer', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_25_httpwww_opengis_netsensorML1_0_1transportLayer', False)

    
    transportLayer = property(__transportLayer.value, __transportLayer.set, None, u'Layer 4 of the OSI model. Provides transparent transfer of data between end users and can control reliability of a given link. (Ex: TCP, UDP, SPX)')

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_25_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)


    _ElementMap = {
        __dataLinkLayer.name() : __dataLinkLayer,
        __networkLayer.name() : __networkLayer,
        __applicationLayer.name() : __applicationLayer,
        __serviceLayer.name() : __serviceLayer,
        __presentationLayer.name() : __presentationLayer,
        __physicalLayer.name() : __physicalLayer,
        __mechanicalLayer.name() : __mechanicalLayer,
        __sessionLayer.name() : __sessionLayer,
        __transportLayer.name() : __transportLayer
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type CTD_ANON_26 with content type ELEMENT_ONLY
class CTD_ANON_26 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}EventList uses Python identifier EventList
    __EventList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EventList'), 'EventList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_26_httpwww_opengis_netsensorML1_0_1EventList', False)

    
    EventList = property(__EventList.value, __EventList.set, None, u'List of events related to the enclosing object')

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_26_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_26_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_26_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_26_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_26_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_26_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_26_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_26_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)


    _ElementMap = {
        __EventList.name() : __EventList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __actuate.name() : __actuate,
        __role.name() : __role,
        __href.name() : __href,
        __type.name() : __type,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __title.name() : __title
    }



# Complex type CTD_ANON_27 with content type ELEMENT_ONLY
class CTD_ANON_27 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}contactInstructions uses Python identifier contactInstructions
    __contactInstructions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'contactInstructions'), 'contactInstructions', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_27_httpwww_opengis_netsensorML1_0_1contactInstructions', False)

    
    contactInstructions = property(__contactInstructions.value, __contactInstructions.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}phone uses Python identifier phone
    __phone = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'phone'), 'phone', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_27_httpwww_opengis_netsensorML1_0_1phone', False)

    
    phone = property(__phone.value, __phone.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}address uses Python identifier address
    __address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'address'), 'address', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_27_httpwww_opengis_netsensorML1_0_1address', False)

    
    address = property(__address.value, __address.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}onlineResource uses Python identifier onlineResource
    __onlineResource = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'), 'onlineResource', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_27_httpwww_opengis_netsensorML1_0_1onlineResource', True)

    
    onlineResource = property(__onlineResource.value, __onlineResource.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}hoursOfService uses Python identifier hoursOfService
    __hoursOfService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'hoursOfService'), 'hoursOfService', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_27_httpwww_opengis_netsensorML1_0_1hoursOfService', False)

    
    hoursOfService = property(__hoursOfService.value, __hoursOfService.set, None, None)


    _ElementMap = {
        __contactInstructions.name() : __contactInstructions,
        __phone.name() : __phone,
        __address.name() : __address,
        __onlineResource.name() : __onlineResource,
        __hoursOfService.name() : __hoursOfService
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_28 with content type ELEMENT_ONLY
class CTD_ANON_28 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}InterfaceDefinition uses Python identifier InterfaceDefinition
    __InterfaceDefinition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'InterfaceDefinition'), 'InterfaceDefinition', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_28_httpwww_opengis_netsensorML1_0_1InterfaceDefinition', False)

    
    InterfaceDefinition = property(__InterfaceDefinition.value, __InterfaceDefinition.set, None, u'Interface definition based on the OSI model. (http://en.wikipedia.org/wiki/OSI_model)')

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_28_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_28_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_28_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_28_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_28_name', pyxb.binding.datatypes.token, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_28_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_28_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_28_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_28_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')


    _ElementMap = {
        __InterfaceDefinition.name() : __InterfaceDefinition
    }
    _AttributeMap = {
        __title.name() : __title,
        __actuate.name() : __actuate,
        __show.name() : __show,
        __type.name() : __type,
        __name.name() : __name,
        __role.name() : __role,
        __href.name() : __href,
        __arcrole.name() : __arcrole,
        __remoteSchema.name() : __remoteSchema
    }



# Complex type CTD_ANON_29 with content type EMPTY
class CTD_ANON_29 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_29_ref', linkRef)
    
    ref = property(__ref.value, __ref.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __ref.name() : __ref
    }



# Complex type CTD_ANON_30 with content type ELEMENT_ONLY
class CTD_ANON_30 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}userID uses Python identifier userID
    __userID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'userID'), 'userID', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_30_httpwww_opengis_netsensorML1_0_1userID', False)

    
    userID = property(__userID.value, __userID.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}surname uses Python identifier surname
    __surname = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'surname'), 'surname', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_30_httpwww_opengis_netsensorML1_0_1surname', False)

    
    surname = property(__surname.value, __surname.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}name uses Python identifier name
    __name = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_30_httpwww_opengis_netsensorML1_0_1name', False)

    
    name = property(__name.value, __name.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}affiliation uses Python identifier affiliation
    __affiliation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'affiliation'), 'affiliation', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_30_httpwww_opengis_netsensorML1_0_1affiliation', False)

    
    affiliation = property(__affiliation.value, __affiliation.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}phoneNumber uses Python identifier phoneNumber
    __phoneNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber'), 'phoneNumber', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_30_httpwww_opengis_netsensorML1_0_1phoneNumber', False)

    
    phoneNumber = property(__phoneNumber.value, __phoneNumber.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}email uses Python identifier email
    __email = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'email'), 'email', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_30_httpwww_opengis_netsensorML1_0_1email', False)

    
    email = property(__email.value, __email.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_30_httpwww_opengis_netgmlid', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, u'Database handle for the object.  It is of XML type ID, so is constrained to be unique in the XML document within which it occurs.  An external identifier for the object in the form of a URI may be constructed using standard XML and XPointer methods.  This is done by concatenating the URI for the document, a fragment separator, and the value of the id attribute.')


    _ElementMap = {
        __userID.name() : __userID,
        __surname.name() : __surname,
        __name.name() : __name,
        __affiliation.name() : __affiliation,
        __phoneNumber.name() : __phoneNumber,
        __email.name() : __email
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type ruleLanguageType with content type EMPTY
class ruleLanguageType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ruleLanguageType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_ruleLanguageType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_ruleLanguageType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_ruleLanguageType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_ruleLanguageType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_ruleLanguageType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_ruleLanguageType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_ruleLanguageType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_ruleLanguageType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __show.name() : __show,
        __remoteSchema.name() : __remoteSchema,
        __href.name() : __href,
        __title.name() : __title,
        __role.name() : __role,
        __arcrole.name() : __arcrole,
        __actuate.name() : __actuate,
        __type.name() : __type
    }
Namespace.addCategoryObject('typeBinding', u'ruleLanguageType', ruleLanguageType)


# Complex type AbstractListType with content type MIXED
class AbstractListType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractListType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_AbstractListType_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __id.name() : __id
    }
Namespace.addCategoryObject('typeBinding', u'AbstractListType', AbstractListType)


# Complex type LayerPropertyType with content type ELEMENT_ONLY
class LayerPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LayerPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/swe/1.0.1}AbstractDataRecord uses Python identifier AbstractDataRecord
    __AbstractDataRecord = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'), 'AbstractDataRecord', '__httpwww_opengis_netsensorML1_0_1_LayerPropertyType_httpwww_opengis_netswe1_0_1AbstractDataRecord', False)

    
    AbstractDataRecord = property(__AbstractDataRecord.value, __AbstractDataRecord.set, None, None)

    
    # Element {http://www.opengis.net/swe/1.0.1}Category uses Python identifier Category
    __Category = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Category'), 'Category', '__httpwww_opengis_netsensorML1_0_1_LayerPropertyType_httpwww_opengis_netswe1_0_1Category', False)

    
    Category = property(__Category.value, __Category.set, None, u'A simple token identifying a term or category (single spaces allowed); definition attribute should provide dictionary entry useful for interpretation of the value')

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_LayerPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_LayerPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_LayerPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_LayerPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_LayerPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_LayerPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_LayerPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_LayerPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __AbstractDataRecord.name() : __AbstractDataRecord,
        __Category.name() : __Category
    }
    _AttributeMap = {
        __href.name() : __href,
        __remoteSchema.name() : __remoteSchema,
        __title.name() : __title,
        __show.name() : __show,
        __role.name() : __role,
        __actuate.name() : __actuate,
        __arcrole.name() : __arcrole,
        __type.name() : __type
    }
Namespace.addCategoryObject('typeBinding', u'LayerPropertyType', LayerPropertyType)


# Complex type CTD_ANON_31 with content type ELEMENT_ONLY
class CTD_ANON_31 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}onlineResource uses Python identifier onlineResource
    __onlineResource = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'), 'onlineResource', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_31_httpwww_opengis_netsensorML1_0_1onlineResource', True)

    
    onlineResource = property(__onlineResource.value, __onlineResource.set, None, None)

    
    # Element {http://www.opengis.net/gml}description uses Python identifier description
    __description = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), 'description', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_31_httpwww_opengis_netgmldescription', False)

    
    description = property(__description.value, __description.set, None, u'Contains a simple text description of the object, or refers to an external description.')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}format uses Python identifier format
    __format = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'format'), 'format', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_31_httpwww_opengis_netsensorML1_0_1format', False)

    
    format = property(__format.value, __format.set, None, u'Specifies the fornat of the file pointed to by onlineResource')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}date uses Python identifier date
    __date = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'date'), 'date', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_31_httpwww_opengis_netsensorML1_0_1date', False)

    
    date = property(__date.value, __date.set, None, u'Date of creation')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}contact uses Python identifier contact
    __contact = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'contact'), 'contact', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_31_httpwww_opengis_netsensorML1_0_1contact', False)

    
    contact = property(__contact.value, __contact.set, None, u'Relevant contacts for that object')

    
    # Attribute version uses Python identifier version
    __version = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'version'), 'version', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_31_version', pyxb.binding.datatypes.token)
    
    version = property(__version.value, __version.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_31_httpwww_opengis_netgmlid', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, u'Database handle for the object.  It is of XML type ID, so is constrained to be unique in the XML document within which it occurs.  An external identifier for the object in the form of a URI may be constructed using standard XML and XPointer methods.  This is done by concatenating the URI for the document, a fragment separator, and the value of the id attribute.')


    _ElementMap = {
        __onlineResource.name() : __onlineResource,
        __description.name() : __description,
        __format.name() : __format,
        __date.name() : __date,
        __contact.name() : __contact
    }
    _AttributeMap = {
        __version.name() : __version,
        __id.name() : __id
    }



# Complex type CTD_ANON_32 with content type ELEMENT_ONLY
class CTD_ANON_32 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}AlgorithmDefinition uses Python identifier AlgorithmDefinition
    __AlgorithmDefinition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AlgorithmDefinition'), 'AlgorithmDefinition', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_32_httpwww_opengis_netsensorML1_0_1AlgorithmDefinition', False)

    
    AlgorithmDefinition = property(__AlgorithmDefinition.value, __AlgorithmDefinition.set, None, None)


    _ElementMap = {
        __AlgorithmDefinition.name() : __AlgorithmDefinition
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_33 with content type EMPTY
class CTD_ANON_33 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {urn:us:gov:ic:ism:v2}releasableTo uses Python identifier releasableTo
    __releasableTo = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'releasableTo'), 'releasableTo', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2releasableTo', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_4)
    
    releasableTo = property(__releasableTo.value, __releasableTo.set, None, u'\n        This attribute is used at both the resource and the portion levels.\n        \n        One or more indicators identifying the country or countries and/or international organization(s) to which classified information may be released based on the determination of an originator in accordance with established foreign disclosure procedures.  This element is used in conjunction with the Dissemination Controls element.\n        \n        It is manifested in portion marks and security banners.\n\n        PERMISSIBLE VALUES\n\n        The permissible values for this attribute are defined in the Implementation Profile Supplement: Value Enumerations in the value sets:\n\n        ISO 3166-1 Country Trigraph Codes\n        Registered International Organizations and Alliances Tetragraphs\n      ')

    
    # Attribute {urn:us:gov:ic:ism:v2}derivativelyClassifiedBy uses Python identifier derivativelyClassifiedBy
    __derivativelyClassifiedBy = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'derivativelyClassifiedBy'), 'derivativelyClassifiedBy', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2derivativelyClassifiedBy', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_2)
    
    derivativelyClassifiedBy = property(__derivativelyClassifiedBy.value, __derivativelyClassifiedBy.set, None, u"\n        This attribute is used primarily at the resource level.\n        \n        \n        The identity, by name or personal identifier, of the derivative classification authority.\n        \n        It is manifested only in the 'Classified By' line of a resource\u2019s Classification/Declassification block.\n      ")

    
    # Attribute {urn:us:gov:ic:ism:v2}SCIcontrols uses Python identifier SCIcontrols
    __SCIcontrols = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'SCIcontrols'), 'SCIcontrols', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2SCIcontrols', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_18)
    
    SCIcontrols = property(__SCIcontrols.value, __SCIcontrols.set, None, u'\n        This attribute is used at both the resource and the portion levels.\n        \n        One or more indicators identifying sensitive compartmented information control system(s).\n        \n        It is manifested in portion marks and security banners.                 \n                    \n                    For the "SI-ECI-XXX" permissible value, "XXX" is a placeholder for ECI program designator alphabetic trigraphs, which are classified and are therefore not included here. Additional classified and unpublished SCI control system abbreviations are not included here.\n\n        PERMISSIBLE VALUES\n\n        The permissible values for this attribute are defined in the Implementation Profile Supplement: Value Enumerations in the value set:\n\n        SCI Control System Markings - Authorized Portion Markings\n      ')

    
    # Attribute {urn:us:gov:ic:ism:v2}derivedFrom uses Python identifier derivedFrom
    __derivedFrom = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'derivedFrom'), 'derivedFrom', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2derivedFrom', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_11)
    
    derivedFrom = property(__derivedFrom.value, __derivedFrom.set, None, u"\n        This attribute is used primarily at the resource level.\n        \n        A citation of the authoritative source or reference to multiple sources of the classification markings used in a classified resource.\n        \n        It is manifested only in the 'Derived From' line of a document's classification/declassification block.\n      ")

    
    # Attribute {urn:us:gov:ic:ism:v2}nonICmarkings uses Python identifier nonICmarkings
    __nonICmarkings = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'nonICmarkings'), 'nonICmarkings', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2nonICmarkings', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_3)
    
    nonICmarkings = property(__nonICmarkings.value, __nonICmarkings.set, None, u'\n        This attribute is used at both the resource and the portion levels.\n        \n        One or more indicators of the expansion or limitation on the distribution of an information resource or portion within the domain of information originating from non-intelligence components.\n        \n        It is manifested in portion marks and security banners.\n        \n        LAW ENFORCEMENT SENSITIVE (LES) is not an authorized IC classification and control marking in the CAPCO Register. However, CAPCO has published interim marking guidance concerning the incorporation of LES information into IC products. "LES" has been included as a permissible value for attribute "nonICmarkings" in IC ISM in order to facilitate compliance with the CAPCO interim marking guidance in XML-based products.\n\n        PERMISSIBLE VALUES\n        1) The value "LES" is permited as described above.\n\n        2) Other permissible values for this attribute are defined in the Implementation Profile Supplement: Value Enumerations in the value set:\n\n        Non-IC Markings - Authorized Portion Markings\n      ')

    
    # Attribute {urn:us:gov:ic:ism:v2}SARIdentifier uses Python identifier SARIdentifier
    __SARIdentifier = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'SARIdentifier'), 'SARIdentifier', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2SARIdentifier', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_5)
    
    SARIdentifier = property(__SARIdentifier.value, __SARIdentifier.set, None, u'\n        This attribute is used at both the resource and the portion levels.\n        \n        One or more indicators identifying the defense or intelligence programs for which special access is required. \n        \n        It is manifested in portion marks and security banners.\n\n        PERMISSIBLE VALUES\n\n        The permissible values for this attribute are defined in the Implementation Profile Supplement: Value Enumerations in the value set:\n\n        Special Access Program Markings - Authorized Portion Markings\n      ')

    
    # Attribute {urn:us:gov:ic:ism:v2}classificationReason uses Python identifier classificationReason
    __classificationReason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'classificationReason'), 'classificationReason', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2classificationReason', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_17)
    
    classificationReason = property(__classificationReason.value, __classificationReason.set, None, u"\n        This attribute is used primarily at the resource level.\n        \n        One or more reason indicators or explanatory text describing the basis for an original classification decision.\n        \n        It is manifested only in the 'Reason' line of a resource\u2019s Classification/Declassification block.\n      ")

    
    # Attribute {urn:us:gov:ic:ism:v2}classifiedBy uses Python identifier classifiedBy
    __classifiedBy = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'classifiedBy'), 'classifiedBy', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2classifiedBy', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_7)
    
    classifiedBy = property(__classifiedBy.value, __classifiedBy.set, None, u"\n        This attribute is used primarily at the resource level.\n        \n        The identity, by name or personal identifier, and position title of the original classification authority for a resource.\n        \n        It is manifested only in the 'Classified By' line of a resource\u2019s Classification/Declassification block.\n      ")

    
    # Attribute {urn:us:gov:ic:ism:v2}classification uses Python identifier classification
    __classification = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'classification'), 'classification', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2classification', pyxb.bundles.opengis.ic_ism_2_1.ClassificationType)
    
    classification = property(__classification.value, __classification.set, None, u'\n        This attribute is used at both the resource and the portion levels. \n        \n        A single indicator of the highest level of classification applicable to an information resource or portion within the domain of classified national security information.  The Classification element is always used in conjunction with the Owner Producer element. Taken together, the two elements specify the classification category and the type of classification (US, non-US, or Joint).\n        \n        It is manifested in portion marks and security banners.\n\n        PERMISSIBLE VALUES\n\n        The permissible values for this attribute are defined in the Implementation Profile Supplement: Value Enumerations in the value set: \n\n        US Classification Markings - Authorized Portion Markings\n        NATO Classification Markings - Authorized Portion Markings\n\n      ')

    
    # Attribute {urn:us:gov:ic:ism:v2}disseminationControls uses Python identifier disseminationControls
    __disseminationControls = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'disseminationControls'), 'disseminationControls', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2disseminationControls', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_8)
    
    disseminationControls = property(__disseminationControls.value, __disseminationControls.set, None, u'\n        This attribute is used at both the resource and the portion levels.\n        \n        One or more indicators identifying the expansion or limitation on the distribution of information.\n        \n        It is manifested in portion marks and security banners.\n\n        PERMISSIBLE VALUES\n\n        The permissible values for this attribute are defined in the Implementation Profile Supplement: Value Enumerations in the value set:\n\n         Dissemination Control Markings - Authorized Portion Markings\n        ')

    
    # Attribute {urn:us:gov:ic:ism:v2}declassManualReview uses Python identifier declassManualReview
    __declassManualReview = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'declassManualReview'), 'declassManualReview', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2declassManualReview', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_1)
    
    declassManualReview = property(__declassManualReview.value, __declassManualReview.set, None, u'\n        This attribute is used primarily at the resource level.\n        \n        A single indicator of a requirement for manual review prior to declassification, over and above the usual programmatic determinations.\n        \n        The ability to indicate manual review was rescinded as of 1 February 2008 with complete removal from automated systems required by 31 March 2009 at which time this element will be deprecated.\n \n      ')

    
    # Attribute {urn:us:gov:ic:ism:v2}ownerProducer uses Python identifier ownerProducer
    __ownerProducer = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'ownerProducer'), 'ownerProducer', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2ownerProducer', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_15)
    
    ownerProducer = property(__ownerProducer.value, __ownerProducer.set, None, u'\n        This attribute is used at both the resource and the portion levels.\n        \n        One or more indicators identifying the national government or international organization that have purview over the classification marking of an information resource or portion therein.  This element is always used in conjunction with the Classification element.  Taken together, the two elements specify the classification category and the type of classification (US, non-US, or Joint). \n        \n        Within protected internal organizational spaces this element may include one or more indicators identifying information which qualifies as foreign government information for which the source(s) of the information must be concealed.  Measures must be taken prior to dissemination of the information to conceal the source(s) of the foreign government information.\n        \n        Specifically, under these specific circumstances, when data are moved to the shared spaces, the non-disclosable owner(s) and/or producer(s) listed in this data element\u2019s value should be removed and replaced with "FGI".\n        \n        The attribute value may be manifested in portion marks or security banners.\n\n        PERMISSIBLE VALUES\n\n        1) The value "FGI" is permited under the circumstances described above.\n\n        2) Other permissible values for this attribute are defined in the Implementation Profile Supplement: Value Enumerations in the value sets:\n\n        ISO 3166-1 Country Trigraphs Codes\n        Registered International Organizations and Alliances Tetragraphs\n      ')

    
    # Attribute {urn:us:gov:ic:ism:v2}FGIsourceOpen uses Python identifier FGIsourceOpen
    __FGIsourceOpen = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'FGIsourceOpen'), 'FGIsourceOpen', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2FGIsourceOpen', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_6)
    
    FGIsourceOpen = property(__FGIsourceOpen.value, __FGIsourceOpen.set, None, u'\n        This attribute is used at both the resource and the portion levels. \n        \n        One or more indicators identifying information which qualifies as foreign government information for which the source(s) of the information is not concealed.\n        \n        The attribute can indicate that the source of information of foreign origin is unknown.\n        \n        It is manifested in portion marks and security banners.\n\n        PERMISSIBLE VALUES\n\n        1) The value "UNKNOWN" is permited under the circumstances described above.\n\n        2) Other permissible values for this attribute are defined in the Implementation Profile Supplement: Value Enumerations in the value sets:\n\n        ISO 3166-1 Country Trigraph Codes\n        Registered International Organizations and Alliances Tetragraphs\n      ')

    
    # Attribute {urn:us:gov:ic:ism:v2}declassException uses Python identifier declassException
    __declassException = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'declassException'), 'declassException', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2declassException', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_9)
    
    declassException = property(__declassException.value, __declassException.set, None, u"\n        This attribute is used primarily at the resource level.\n        \n        A single indicator describing an exemption to the nominal 25-year point for automatic declassification.  This element is used in conjunction with the Declassification Date or Declassification Event.\n        \n        It is manifested in the 'Declassify On' line of a resource\u2019s classification/declassification block.\n        \n        This element is defined as NMTOKENS but ISOO has stated it should be a SINGLE value giving the longest protection.\n        PERMISSIBLE VALUE\n\n        The permissible value for this attribute is defined in the Implementation Profile Supplement: Value Enumerations in the value set:\n\n        Exemption from 25-Year Automatic Declassification Markings\n\n      ")

    
    # Attribute {urn:us:gov:ic:ism:v2}typeOfExemptedSource uses Python identifier typeOfExemptedSource
    __typeOfExemptedSource = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'typeOfExemptedSource'), 'typeOfExemptedSource', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2typeOfExemptedSource', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_12)
    
    typeOfExemptedSource = property(__typeOfExemptedSource.value, __typeOfExemptedSource.set, None, u"\n        This attribute is used primarily at the resource level.\n        \n        A declassification marking of a source document that causes the current, derivative document to be exempted from automatic declassification.  This element is always used in conjunction with the Date Of Exempted Source element.\n        \n       It is manifested only in the 'Declassify On' line of a document's classification/declassification block.\n       \n       This element is defined as NMTOKENS but ISOO has stated it should be a SINGLE value giving the longest protection.\n\n        PERMISSIBLE VALUE\n\n        The permissible value for this attribute is defined in the Implementation Profile Supplement: Value Enumerations in the value set:\n\n        Source Document Declassification Instruction Markings\n\n      ")

    
    # Attribute {urn:us:gov:ic:ism:v2}dateOfExemptedSource uses Python identifier dateOfExemptedSource
    __dateOfExemptedSource = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'dateOfExemptedSource'), 'dateOfExemptedSource', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2dateOfExemptedSource', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_16)
    
    dateOfExemptedSource = property(__dateOfExemptedSource.value, __dateOfExemptedSource.set, None, u"\n        This attribute is used primarily at the resource level.\n        \n        A specific year, month, and day of publication or release of a source document, or the most recent source document, that was itself marked with a declassification constraint.  This element is always used in conjunction with the Type Of Exempted Source element.  \n        \n        It is manifested only in the 'Declassify On' line of a resource\u2019s Classification/Declassification block.\n      ")

    
    # Attribute {urn:us:gov:ic:ism:v2}declassEvent uses Python identifier declassEvent
    __declassEvent = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'declassEvent'), 'declassEvent', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2declassEvent', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_13)
    
    declassEvent = property(__declassEvent.value, __declassEvent.set, None, u"\n        This attribute is used primarily at the resource level.\n        \n        A description of an event upon which the information shall be automatically declassified if not properly exempted from automatic declassification.\n        \n        It is manifested only in the 'Declassify On' line of a resource\u2019s classification/declassification block.\n      ")

    
    # Attribute {urn:us:gov:ic:ism:v2}FGIsourceProtected uses Python identifier FGIsourceProtected
    __FGIsourceProtected = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'FGIsourceProtected'), 'FGIsourceProtected', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2FGIsourceProtected', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_14)
    
    FGIsourceProtected = property(__FGIsourceProtected.value, __FGIsourceProtected.set, None, u'\n        This attribute is used at both the resource and the portion levels.\n        \n        This attribute has unique specific rules concerning its usage. \n        \n        A single indicator that information qualifies as foreign government information for which the source(s) of the information must be concealed.\n        \n        Within protected internal organizational spaces this element may be used to maintain a record of the one or more indicators identifying information which qualifies as foreign government information for which the source(s) of the information must be concealed.  Measures must be taken prior to dissemination of the information to conceal the source(s) of the foreign government information.\n        \n        An indication that information qualifies as foreign government information according to CAPCO guidelines for which the source(s) of the information must be concealed when the information is disseminated in shared spaces\n        \n        This data element has a dual purpose. Within shared spaces, the data element serves only to indicate the presence of information which is categorized as foreign government information according to CAPCO guidelines for which the source(s) of the information is concealed, in which case, this data element\u2019s value will always be "FGI". The data element may also be employed in this manner within protected internal organizational spaces. However, within protected internal organizational spaces this data element may alternatively be used to maintain a formal record of the foreign country or countries and/or registered international organization(s) that are the non-disclosable owner(s) and/or producer(s) of information which is categorized as foreign government information according to CAPCO guidelines for which the source(s) of the information must be concealed when the resource is disseminated to shared spaces. If the data element is employed in this manner, then additional measures must be taken prior to dissemination of the resource to shared spaces so that any indications of the non-disclosable owner(s) and/or producer(s) of information within the resource are eliminated.\n\n        In all cases, the corresponding portion marking or banner marking should be compliant with CAPCO guidelines for FGI when the source must be concealed. In other words, even if the data element is being employed within protected internal organizational spaces to maintain a formal record of the non-disclosable owner(s) and/or producer(s) within an XML resource, if the resource is rendered for display within the protected internal organizational spaces in any format by a stylesheet or as a result of any other transformation process, then the non-disclosable owner(s) and/or producer(s) should not be included in the corresponding portion marking or banner marking.\n\n        PERMISSIBLE VALUES\n\n        1) The value "FGI" is permited under the circumstances described above.\n\n        2) Other permissible values for this attribute are defined in the Implementation Profile Supplement: Value Enumerations in the value sets:\n\n        ISO 3166-1 Country Trigraph Codes\n        Registered International Organizations and Alliances Tetragraphs\n      ')

    
    # Attribute {urn:us:gov:ic:ism:v2}declassDate uses Python identifier declassDate
    __declassDate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:us:gov:ic:ism:v2'), u'declassDate'), 'declassDate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_33_urnusgovicismv2declassDate', pyxb.bundles.opengis.ic_ism_2_1.STD_ANON_10)
    
    declassDate = property(__declassDate.value, __declassDate.set, None, u"\n         This attribute is used primarily at the resource level.\n         \n         A specific year, month, and day upon which the information shall be automatically declassified if not properly exempted from automatic declassification.\n         \n         It is manifested in the 'Declassify On' line of a resource's classification/declassification block.\n      ")


    _ElementMap = {
        
    }
    _AttributeMap = {
        __releasableTo.name() : __releasableTo,
        __derivativelyClassifiedBy.name() : __derivativelyClassifiedBy,
        __SCIcontrols.name() : __SCIcontrols,
        __derivedFrom.name() : __derivedFrom,
        __nonICmarkings.name() : __nonICmarkings,
        __SARIdentifier.name() : __SARIdentifier,
        __classificationReason.name() : __classificationReason,
        __classifiedBy.name() : __classifiedBy,
        __classification.name() : __classification,
        __disseminationControls.name() : __disseminationControls,
        __declassManualReview.name() : __declassManualReview,
        __ownerProducer.name() : __ownerProducer,
        __FGIsourceOpen.name() : __FGIsourceOpen,
        __declassException.name() : __declassException,
        __typeOfExemptedSource.name() : __typeOfExemptedSource,
        __dateOfExemptedSource.name() : __dateOfExemptedSource,
        __declassEvent.name() : __declassEvent,
        __FGIsourceProtected.name() : __FGIsourceProtected,
        __declassDate.name() : __declassDate
    }



# Complex type CTD_ANON_34 with content type ELEMENT_ONLY
class CTD_ANON_34 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}ComponentList uses Python identifier ComponentList
    __ComponentList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ComponentList'), 'ComponentList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_34_httpwww_opengis_netsensorML1_0_1ComponentList', False)

    
    ComponentList = property(__ComponentList.value, __ComponentList.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_34_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_34_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_34_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_34_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_34_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_34_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_34_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_34_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __ComponentList.name() : __ComponentList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __role.name() : __role,
        __actuate.name() : __actuate,
        __title.name() : __title,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __type.name() : __type
    }



# Complex type CTD_ANON_35 with content type EMPTY
class CTD_ANON_35 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_35_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_35_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_35_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_35_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_35_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_35_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_35_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_35_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __actuate.name() : __actuate,
        __remoteSchema.name() : __remoteSchema,
        __type.name() : __type,
        __role.name() : __role,
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __href.name() : __href,
        __title.name() : __title
    }



# Complex type CTD_ANON_36 with content type EMPTY
class CTD_ANON_36 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_36_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_36_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_36_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_36_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_36_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_36_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_36_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_36_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")


    _ElementMap = {
        
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __href.name() : __href,
        __title.name() : __title,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __role.name() : __role,
        __type.name() : __type,
        __actuate.name() : __actuate
    }



# Complex type CTD_ANON_37 with content type ELEMENT_ONLY
class CTD_ANON_37 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}Link uses Python identifier Link
    __Link = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Link'), 'Link', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_37_httpwww_opengis_netsensorML1_0_1Link', False)

    
    Link = property(__Link.value, __Link.set, None, u'Link object used to make connections between processes')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}ArrayLink uses Python identifier ArrayLink
    __ArrayLink = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ArrayLink'), 'ArrayLink', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_37_httpwww_opengis_netsensorML1_0_1ArrayLink', False)

    
    ArrayLink = property(__ArrayLink.value, __ArrayLink.set, None, u'Special Link to handle accessing array elements sequentially')

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_37_name', pyxb.binding.datatypes.token)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        __Link.name() : __Link,
        __ArrayLink.name() : __ArrayLink
    }
    _AttributeMap = {
        __name.name() : __name
    }



# Complex type CTD_ANON_38 with content type ELEMENT_ONLY
class CTD_ANON_38 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}date uses Python identifier date
    __date = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'date'), 'date', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_38_httpwww_opengis_netsensorML1_0_1date', False)

    
    date = property(__date.value, __date.set, None, u'Date/Time of event')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}keywords uses Python identifier keywords
    __keywords = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'keywords'), 'keywords', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_38_httpwww_opengis_netsensorML1_0_1keywords', True)

    
    keywords = property(__keywords.value, __keywords.set, None, u'Means of providing a list of keywords (with a codeSpace) for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}contact uses Python identifier contact
    __contact = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'contact'), 'contact', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_38_httpwww_opengis_netsensorML1_0_1contact', True)

    
    contact = property(__contact.value, __contact.set, None, u'Relevant contacts for that object')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}identification uses Python identifier identification
    __identification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'identification'), 'identification', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_38_httpwww_opengis_netsensorML1_0_1identification', True)

    
    identification = property(__identification.value, __identification.set, None, u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}documentation uses Python identifier documentation
    __documentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'documentation'), 'documentation', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_38_httpwww_opengis_netsensorML1_0_1documentation', True)

    
    documentation = property(__documentation.value, __documentation.set, None, u'Relevant documentation for that object')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}classification uses Python identifier classification
    __classification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'classification'), 'classification', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_38_httpwww_opengis_netsensorML1_0_1classification', True)

    
    classification = property(__classification.value, __classification.set, None, u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary')

    
    # Element {http://www.opengis.net/gml}description uses Python identifier description
    __description = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), 'description', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_38_httpwww_opengis_netgmldescription', False)

    
    description = property(__description.value, __description.set, None, u'Contains a simple text description of the object, or refers to an external description.')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}property uses Python identifier property_
    __property = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'property'), 'property_', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_38_httpwww_opengis_netsensorML1_0_1property', True)

    
    property_ = property(__property.value, __property.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_38_httpwww_opengis_netgmlid', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, u'Database handle for the object.  It is of XML type ID, so is constrained to be unique in the XML document within which it occurs.  An external identifier for the object in the form of a URI may be constructed using standard XML and XPointer methods.  This is done by concatenating the URI for the document, a fragment separator, and the value of the id attribute.')


    _ElementMap = {
        __date.name() : __date,
        __keywords.name() : __keywords,
        __contact.name() : __contact,
        __identification.name() : __identification,
        __documentation.name() : __documentation,
        __classification.name() : __classification,
        __description.name() : __description,
        __property.name() : __property
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type CTD_ANON_39 with content type ELEMENT_ONLY
class CTD_ANON_39 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}InterfaceList uses Python identifier InterfaceList
    __InterfaceList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'InterfaceList'), 'InterfaceList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_39_httpwww_opengis_netsensorML1_0_1InterfaceList', False)

    
    InterfaceList = property(__InterfaceList.value, __InterfaceList.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_39_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_39_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_39_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_39_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_39_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_39_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_39_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_39_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        __InterfaceList.name() : __InterfaceList
    }
    _AttributeMap = {
        __show.name() : __show,
        __remoteSchema.name() : __remoteSchema,
        __actuate.name() : __actuate,
        __role.name() : __role,
        __type.name() : __type,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __href.name() : __href
    }



# Complex type CTD_ANON_40 with content type ELEMENT_ONLY
class CTD_ANON_40 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_40_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_40_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_40_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_40_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_40_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_40_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_40_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_40_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __show.name() : __show,
        __actuate.name() : __actuate,
        __role.name() : __role,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __type.name() : __type
    }



# Complex type CTD_ANON_41 with content type ELEMENT_ONLY
class CTD_ANON_41 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}connection uses Python identifier connection
    __connection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'connection'), 'connection', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_41_httpwww_opengis_netsensorML1_0_1connection', True)

    
    connection = property(__connection.value, __connection.set, None, u'Specify a connection between two elements')


    _ElementMap = {
        __connection.name() : __connection
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_42 with content type ELEMENT_ONLY
class CTD_ANON_42 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}contactInfo uses Python identifier contactInfo
    __contactInfo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'contactInfo'), 'contactInfo', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_42_httpwww_opengis_netsensorML1_0_1contactInfo', False)

    
    contactInfo = property(__contactInfo.value, __contactInfo.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}individualName uses Python identifier individualName
    __individualName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'individualName'), 'individualName', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_42_httpwww_opengis_netsensorML1_0_1individualName', False)

    
    individualName = property(__individualName.value, __individualName.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}positionName uses Python identifier positionName
    __positionName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'positionName'), 'positionName', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_42_httpwww_opengis_netsensorML1_0_1positionName', False)

    
    positionName = property(__positionName.value, __positionName.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}organizationName uses Python identifier organizationName
    __organizationName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'organizationName'), 'organizationName', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_42_httpwww_opengis_netsensorML1_0_1organizationName', False)

    
    organizationName = property(__organizationName.value, __organizationName.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_42_httpwww_opengis_netgmlid', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, u'Database handle for the object.  It is of XML type ID, so is constrained to be unique in the XML document within which it occurs.  An external identifier for the object in the form of a URI may be constructed using standard XML and XPointer methods.  This is done by concatenating the URI for the document, a fragment separator, and the value of the id attribute.')


    _ElementMap = {
        __contactInfo.name() : __contactInfo,
        __individualName.name() : __individualName,
        __positionName.name() : __positionName,
        __organizationName.name() : __organizationName
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type CTD_ANON_43 with content type ELEMENT_ONLY
class CTD_ANON_43 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}component uses Python identifier component
    __component = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'component'), 'component', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_43_httpwww_opengis_netsensorML1_0_1component', True)

    
    component = property(__component.value, __component.set, None, None)


    _ElementMap = {
        __component.name() : __component
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_44 with content type EMPTY
class CTD_ANON_44 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_44_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_44_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_44_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_44_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_44_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_44_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_44_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_44_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __role.name() : __role,
        __href.name() : __href,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __actuate.name() : __actuate,
        __title.name() : __title,
        __type.name() : __type
    }



# Complex type CTD_ANON_45 with content type ELEMENT_ONLY
class CTD_ANON_45 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}input uses Python identifier input
    __input = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'input'), 'input', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_45_httpwww_opengis_netsensorML1_0_1input', True)

    
    input = property(__input.value, __input.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_45_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)


    _ElementMap = {
        __input.name() : __input
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type methodPropertyType with content type ELEMENT_ONLY
class methodPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'methodPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}ProcessMethod uses Python identifier ProcessMethod
    __ProcessMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ProcessMethod'), 'ProcessMethod', '__httpwww_opengis_netsensorML1_0_1_methodPropertyType_httpwww_opengis_netsensorML1_0_1ProcessMethod', False)

    
    ProcessMethod = property(__ProcessMethod.value, __ProcessMethod.set, None, u'Method describing a process (Can also be a dictionary entry)')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_methodPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_methodPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_methodPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_methodPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_methodPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_methodPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_methodPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_methodPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        __ProcessMethod.name() : __ProcessMethod
    }
    _AttributeMap = {
        __actuate.name() : __actuate,
        __remoteSchema.name() : __remoteSchema,
        __type.name() : __type,
        __arcrole.name() : __arcrole,
        __title.name() : __title,
        __href.name() : __href,
        __show.name() : __show,
        __role.name() : __role
    }
Namespace.addCategoryObject('typeBinding', u'methodPropertyType', methodPropertyType)


# Complex type CTD_ANON_46 with content type ELEMENT_ONLY
class CTD_ANON_46 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/gml}TemporalCRS uses Python identifier TemporalCRS
    __TemporalCRS = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TemporalCRS'), 'TemporalCRS', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_46_httpwww_opengis_netgmlTemporalCRS', False)

    
    TemporalCRS = property(__TemporalCRS.value, __TemporalCRS.set, None, None)


    _ElementMap = {
        __TemporalCRS.name() : __TemporalCRS
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_47 with content type ELEMENT_ONLY
class CTD_ANON_47 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}member uses Python identifier member
    __member = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'member'), 'member', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_47_httpwww_opengis_netsensorML1_0_1member', True)

    
    member = property(__member.value, __member.set, None, None)

    
    # Element {http://www.opengis.net/gml}description uses Python identifier description
    __description = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), 'description', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_47_httpwww_opengis_netgmldescription', False)

    
    description = property(__description.value, __description.set, None, u'Contains a simple text description of the object, or refers to an external description.')

    
    # Attribute {http://www.opengis.net/gml}id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_47_httpwww_opengis_netgmlid', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, u'Database handle for the object.  It is of XML type ID, so is constrained to be unique in the XML document within which it occurs.  An external identifier for the object in the form of a URI may be constructed using standard XML and XPointer methods.  This is done by concatenating the URI for the document, a fragment separator, and the value of the id attribute.')


    _ElementMap = {
        __member.name() : __member,
        __description.name() : __description
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type CTD_ANON_48 with content type ELEMENT_ONLY
class CTD_ANON_48 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}Rights uses Python identifier Rights
    __Rights = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Rights'), 'Rights', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_48_httpwww_opengis_netsensorML1_0_1Rights', False)

    
    Rights = property(__Rights.value, __Rights.set, None, u'based on IC:DDMS definition')

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_48_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_48_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_48_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_48_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_48_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_48_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_48_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_48_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")


    _ElementMap = {
        __Rights.name() : __Rights
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __type.name() : __type,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __role.name() : __role,
        __href.name() : __href,
        __actuate.name() : __actuate
    }



# Complex type CTD_ANON_49 with content type ELEMENT_ONLY
class CTD_ANON_49 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}binaryRef uses Python identifier binaryRef
    __binaryRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'binaryRef'), 'binaryRef', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1binaryRef', False)

    
    binaryRef = property(__binaryRef.value, __binaryRef.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}classification uses Python identifier classification
    __classification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'classification'), 'classification', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1classification', True)

    
    classification = property(__classification.value, __classification.set, None, u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary')

    
    # Element {http://www.opengis.net/gml}description uses Python identifier description
    __description = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), 'description', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netgmldescription', False)

    
    description = property(__description.value, __description.set, None, u'Contains a simple text description of the object, or refers to an external description.')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}capabilities uses Python identifier capabilities
    __capabilities = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'capabilities'), 'capabilities', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1capabilities', True)

    
    capabilities = property(__capabilities.value, __capabilities.set, None, u'Capability list for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}validTime uses Python identifier validTime
    __validTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'validTime'), 'validTime', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1validTime', False)

    
    validTime = property(__validTime.value, __validTime.set, None, u'Means of providing time validity constraint of description')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}characteristics uses Python identifier characteristics
    __characteristics = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'characteristics'), 'characteristics', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1characteristics', True)

    
    characteristics = property(__characteristics.value, __characteristics.set, None, u'Characteristic list for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}securityConstraint uses Python identifier securityConstraint
    __securityConstraint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'), 'securityConstraint', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1securityConstraint', False)

    
    securityConstraint = property(__securityConstraint.value, __securityConstraint.set, None, u'Means of providing security constraints of description')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}contact uses Python identifier contact
    __contact = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'contact'), 'contact', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1contact', True)

    
    contact = property(__contact.value, __contact.set, None, u'Relevant contacts for that object')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}history uses Python identifier history
    __history = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'history'), 'history', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1history', True)

    
    history = property(__history.value, __history.set, None, u'History of the object described (Recalibration, adjustments, etc...)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}sourceRef uses Python identifier sourceRef
    __sourceRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sourceRef'), 'sourceRef', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1sourceRef', False)

    
    sourceRef = property(__sourceRef.value, __sourceRef.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}legalConstraint uses Python identifier legalConstraint
    __legalConstraint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'), 'legalConstraint', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1legalConstraint', True)

    
    legalConstraint = property(__legalConstraint.value, __legalConstraint.set, None, u'Means of providing legal constraints of description')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}documentation uses Python identifier documentation
    __documentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'documentation'), 'documentation', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1documentation', True)

    
    documentation = property(__documentation.value, __documentation.set, None, u'Relevant documentation for that object')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}identification uses Python identifier identification
    __identification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'identification'), 'identification', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1identification', True)

    
    identification = property(__identification.value, __identification.set, None, u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}keywords uses Python identifier keywords
    __keywords = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'keywords'), 'keywords', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_httpwww_opengis_netsensorML1_0_1keywords', True)

    
    keywords = property(__keywords.value, __keywords.set, None, u'Means of providing a list of keywords (with a codeSpace) for quick discovery')

    
    # Attribute framework uses Python identifier framework
    __framework = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'framework'), 'framework', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_framework', pyxb.binding.datatypes.token)
    
    framework = property(__framework.value, __framework.set, None, None)

    
    # Attribute version uses Python identifier version
    __version = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'version'), 'version', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_version', pyxb.binding.datatypes.token)
    
    version = property(__version.value, __version.set, None, None)

    
    # Attribute language uses Python identifier language
    __language = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'language'), 'language', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_49_language', pyxb.binding.datatypes.token, required=True)
    
    language = property(__language.value, __language.set, None, None)


    _ElementMap = {
        __binaryRef.name() : __binaryRef,
        __classification.name() : __classification,
        __description.name() : __description,
        __capabilities.name() : __capabilities,
        __validTime.name() : __validTime,
        __characteristics.name() : __characteristics,
        __securityConstraint.name() : __securityConstraint,
        __contact.name() : __contact,
        __history.name() : __history,
        __sourceRef.name() : __sourceRef,
        __legalConstraint.name() : __legalConstraint,
        __documentation.name() : __documentation,
        __identification.name() : __identification,
        __keywords.name() : __keywords
    }
    _AttributeMap = {
        __framework.name() : __framework,
        __version.name() : __version,
        __language.name() : __language
    }



# Complex type connectionsPropertyType with content type ELEMENT_ONLY
class connectionsPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'connectionsPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}ConnectionList uses Python identifier ConnectionList
    __ConnectionList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ConnectionList'), 'ConnectionList', '__httpwww_opengis_netsensorML1_0_1_connectionsPropertyType_httpwww_opengis_netsensorML1_0_1ConnectionList', False)

    
    ConnectionList = property(__ConnectionList.value, __ConnectionList.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_connectionsPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_connectionsPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_connectionsPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_connectionsPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_connectionsPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_connectionsPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_connectionsPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_connectionsPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)


    _ElementMap = {
        __ConnectionList.name() : __ConnectionList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __arcrole.name() : __arcrole,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __role.name() : __role,
        __show.name() : __show,
        __href.name() : __href,
        __title.name() : __title
    }
Namespace.addCategoryObject('typeBinding', u'connectionsPropertyType', connectionsPropertyType)


# Complex type CTD_ANON_50 with content type ELEMENT_ONLY
class CTD_ANON_50 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}Term uses Python identifier Term
    __Term = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Term'), 'Term', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_50_httpwww_opengis_netsensorML1_0_1Term', False)

    
    Term = property(__Term.value, __Term.set, None, u'A well defined token used to specify identifier and classifier values (single spaces allowed)')

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_50_name', pyxb.binding.datatypes.token)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        __Term.name() : __Term
    }
    _AttributeMap = {
        __name.name() : __name
    }



# Complex type dataSourcesPropertyType with content type ELEMENT_ONLY
class dataSourcesPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'dataSourcesPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}DataSourceList uses Python identifier DataSourceList
    __DataSourceList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DataSourceList'), 'DataSourceList', '__httpwww_opengis_netsensorML1_0_1_dataSourcesPropertyType_httpwww_opengis_netsensorML1_0_1DataSourceList', False)

    
    DataSourceList = property(__DataSourceList.value, __DataSourceList.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_dataSourcesPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_dataSourcesPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_dataSourcesPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_dataSourcesPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_dataSourcesPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_dataSourcesPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_dataSourcesPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_dataSourcesPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        __DataSourceList.name() : __DataSourceList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __show.name() : __show,
        __actuate.name() : __actuate,
        __arcrole.name() : __arcrole,
        __type.name() : __type,
        __role.name() : __role,
        __title.name() : __title,
        __href.name() : __href
    }
Namespace.addCategoryObject('typeBinding', u'dataSourcesPropertyType', dataSourcesPropertyType)


# Complex type AbstractDerivableComponentType with content type ELEMENT_ONLY
class AbstractDerivableComponentType (AbstractProcessType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractDerivableComponentType')
    # Base type is AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}location uses Python identifier location_
    __location_ = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'location'), 'location_', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableComponentType_httpwww_opengis_netsensorML1_0_1location', False)

    
    location_ = property(__location_.value, __location_.set, None, u'Uses a gml:Point for a fixed location or a (time dependant) curve for time variable location')

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}position uses Python identifier position
    __position = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'position'), 'position', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableComponentType_httpwww_opengis_netsensorML1_0_1position', False)

    
    position = property(__position.value, __position.set, None, u'Full position (location + orientation) given by a swe:Position or a Process (if variable)')

    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}timePosition uses Python identifier timePosition
    __timePosition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'timePosition'), 'timePosition', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableComponentType_httpwww_opengis_netsensorML1_0_1timePosition', False)

    
    timePosition = property(__timePosition.value, __timePosition.set, None, u'Provide the ability to relate  a local time frame to a reference time frame')

    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}spatialReferenceFrame uses Python identifier spatialReferenceFrame
    __spatialReferenceFrame = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'), 'spatialReferenceFrame', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableComponentType_httpwww_opengis_netsensorML1_0_1spatialReferenceFrame', False)

    
    spatialReferenceFrame = property(__spatialReferenceFrame.value, __spatialReferenceFrame.set, None, u'Textual definition of a spatial frame axes (origin, orientation). Spatial frames can be related to one another by specifying relative positions.')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}interfaces uses Python identifier interfaces
    __interfaces = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'interfaces'), 'interfaces', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableComponentType_httpwww_opengis_netsensorML1_0_1interfaces', False)

    
    interfaces = property(__interfaces.value, __interfaces.set, None, u'List of interfaces useable to access System inputs and outputs')

    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}temporalReferenceFrame uses Python identifier temporalReferenceFrame
    __temporalReferenceFrame = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'), 'temporalReferenceFrame', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableComponentType_httpwww_opengis_netsensorML1_0_1temporalReferenceFrame', False)

    
    temporalReferenceFrame = property(__temporalReferenceFrame.value, __temporalReferenceFrame.set, None, u'Textual definition of a temporal frame (time origin). Temporal frames can be related to one another by specifying relative times.')

    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractProcessType._ElementMap.copy()
    _ElementMap.update({
        __location_.name() : __location_,
        __position.name() : __position,
        __timePosition.name() : __timePosition,
        __spatialReferenceFrame.name() : __spatialReferenceFrame,
        __interfaces.name() : __interfaces,
        __temporalReferenceFrame.name() : __temporalReferenceFrame
    })
    _AttributeMap = AbstractProcessType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractDerivableComponentType', AbstractDerivableComponentType)


# Complex type AbstractComponentType with content type ELEMENT_ONLY
class AbstractComponentType (AbstractDerivableComponentType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractComponentType')
    # Base type is AbstractDerivableComponentType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element spatialReferenceFrame ({http://www.opengis.net/sensorML/1.0.1}spatialReferenceFrame) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element temporalReferenceFrame ({http://www.opengis.net/sensorML/1.0.1}temporalReferenceFrame) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element position ({http://www.opengis.net/sensorML/1.0.1}position) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element timePosition ({http://www.opengis.net/sensorML/1.0.1}timePosition) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element interfaces ({http://www.opengis.net/sensorML/1.0.1}interfaces) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element location_ ({http://www.opengis.net/sensorML/1.0.1}location) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}inputs uses Python identifier inputs
    __inputs = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'inputs'), 'inputs', '__httpwww_opengis_netsensorML1_0_1_AbstractComponentType_httpwww_opengis_netsensorML1_0_1inputs', False)

    
    inputs = property(__inputs.value, __inputs.set, None, u'list of input signals')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}outputs uses Python identifier outputs
    __outputs = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'outputs'), 'outputs', '__httpwww_opengis_netsensorML1_0_1_AbstractComponentType_httpwww_opengis_netsensorML1_0_1outputs', False)

    
    outputs = property(__outputs.value, __outputs.set, None, u'list of output signals')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}parameters uses Python identifier parameters
    __parameters = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'parameters'), 'parameters', '__httpwww_opengis_netsensorML1_0_1_AbstractComponentType_httpwww_opengis_netsensorML1_0_1parameters', False)

    
    parameters = property(__parameters.value, __parameters.set, None, u'list of parameters')

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractDerivableComponentType._ElementMap.copy()
    _ElementMap.update({
        __inputs.name() : __inputs,
        __outputs.name() : __outputs,
        __parameters.name() : __parameters
    })
    _AttributeMap = AbstractDerivableComponentType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractComponentType', AbstractComponentType)


# Complex type ComponentType with content type ELEMENT_ONLY
class ComponentType (AbstractComponentType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ComponentType')
    # Base type is AbstractComponentType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}method uses Python identifier method
    __method = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'method'), 'method', '__httpwww_opengis_netsensorML1_0_1_ComponentType_httpwww_opengis_netsensorML1_0_1method', False)

    
    method = property(__method.value, __method.set, None, u'process method')

    
    # Element spatialReferenceFrame ({http://www.opengis.net/sensorML/1.0.1}spatialReferenceFrame) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element temporalReferenceFrame ({http://www.opengis.net/sensorML/1.0.1}temporalReferenceFrame) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element position ({http://www.opengis.net/sensorML/1.0.1}position) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element timePosition ({http://www.opengis.net/sensorML/1.0.1}timePosition) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element interfaces ({http://www.opengis.net/sensorML/1.0.1}interfaces) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element location_ ({http://www.opengis.net/sensorML/1.0.1}location) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element inputs ({http://www.opengis.net/sensorML/1.0.1}inputs) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractComponentType
    
    # Element outputs ({http://www.opengis.net/sensorML/1.0.1}outputs) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractComponentType
    
    # Element parameters ({http://www.opengis.net/sensorML/1.0.1}parameters) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractComponentType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractComponentType._ElementMap.copy()
    _ElementMap.update({
        __method.name() : __method
    })
    _AttributeMap = AbstractComponentType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ComponentType', ComponentType)


# Complex type CTD_ANON_51 with content type ELEMENT_ONLY
class CTD_ANON_51 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}keyword uses Python identifier keyword
    __keyword = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'keyword'), 'keyword', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_51_httpwww_opengis_netsensorML1_0_1keyword', True)

    
    keyword = property(__keyword.value, __keyword.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_51_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)

    
    # Attribute codeSpace uses Python identifier codeSpace
    __codeSpace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'codeSpace'), 'codeSpace', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_51_codeSpace', pyxb.binding.datatypes.anyURI)
    
    codeSpace = property(__codeSpace.value, __codeSpace.set, None, None)


    _ElementMap = {
        __keyword.name() : __keyword
    }
    _AttributeMap = {
        __id.name() : __id,
        __codeSpace.name() : __codeSpace
    }



# Complex type CTD_ANON_52 with content type ELEMENT_ONLY
class CTD_ANON_52 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}Document uses Python identifier Document
    __Document = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Document'), 'Document', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_52_httpwww_opengis_netsensorML1_0_1Document', False)

    
    Document = property(__Document.value, __Document.set, None, u'Document record with date/time, version, author, etc. pointing to an online resource related to the enclosing object')

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_52_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_52_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_52_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_52_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_52_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_52_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_52_name', pyxb.binding.datatypes.token, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_52_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_52_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __Document.name() : __Document
    }
    _AttributeMap = {
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __title.name() : __title,
        __role.name() : __role,
        __href.name() : __href,
        __remoteSchema.name() : __remoteSchema,
        __name.name() : __name,
        __actuate.name() : __actuate,
        __type.name() : __type
    }



# Complex type CTD_ANON_53 with content type EMPTY
class CTD_ANON_53 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_53_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_53_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_53_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_53_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_53_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_53_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_53_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_53_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __actuate.name() : __actuate,
        __remoteSchema.name() : __remoteSchema,
        __type.name() : __type,
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __href.name() : __href,
        __title.name() : __title,
        __role.name() : __role
    }



# Complex type CTD_ANON_54 with content type ELEMENT_ONLY
class CTD_ANON_54 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}capabilities uses Python identifier capabilities
    __capabilities = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'capabilities'), 'capabilities', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1capabilities', True)

    
    capabilities = property(__capabilities.value, __capabilities.set, None, u'Capability list for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}validTime uses Python identifier validTime
    __validTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'validTime'), 'validTime', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1validTime', False)

    
    validTime = property(__validTime.value, __validTime.set, None, u'Means of providing time validity constraint of description')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}characteristics uses Python identifier characteristics
    __characteristics = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'characteristics'), 'characteristics', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1characteristics', True)

    
    characteristics = property(__characteristics.value, __characteristics.set, None, u'Characteristic list for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}keywords uses Python identifier keywords
    __keywords = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'keywords'), 'keywords', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1keywords', True)

    
    keywords = property(__keywords.value, __keywords.set, None, u'Means of providing a list of keywords (with a codeSpace) for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}securityConstraint uses Python identifier securityConstraint
    __securityConstraint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'), 'securityConstraint', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1securityConstraint', False)

    
    securityConstraint = property(__securityConstraint.value, __securityConstraint.set, None, u'Means of providing security constraints of description')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}contact uses Python identifier contact
    __contact = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'contact'), 'contact', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1contact', True)

    
    contact = property(__contact.value, __contact.set, None, u'Relevant contacts for that object')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}member uses Python identifier member
    __member = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'member'), 'member', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1member', True)

    
    member = property(__member.value, __member.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}legalConstraint uses Python identifier legalConstraint
    __legalConstraint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'), 'legalConstraint', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1legalConstraint', True)

    
    legalConstraint = property(__legalConstraint.value, __legalConstraint.set, None, u'Means of providing legal constraints of description')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}documentation uses Python identifier documentation
    __documentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'documentation'), 'documentation', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1documentation', True)

    
    documentation = property(__documentation.value, __documentation.set, None, u'Relevant documentation for that object')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}identification uses Python identifier identification
    __identification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'identification'), 'identification', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1identification', True)

    
    identification = property(__identification.value, __identification.set, None, u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}classification uses Python identifier classification
    __classification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'classification'), 'classification', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1classification', True)

    
    classification = property(__classification.value, __classification.set, None, u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}history uses Python identifier history
    __history = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'history'), 'history', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_httpwww_opengis_netsensorML1_0_1history', True)

    
    history = property(__history.value, __history.set, None, u'History of the object described (Recalibration, adjustments, etc...)')

    
    # Attribute version uses Python identifier version
    __version = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'version'), 'version', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_54_version', pyxb.binding.datatypes.token, fixed=True, unicode_default=u'1.0.1', required=True)
    
    version = property(__version.value, __version.set, None, None)


    _ElementMap = {
        __capabilities.name() : __capabilities,
        __validTime.name() : __validTime,
        __characteristics.name() : __characteristics,
        __keywords.name() : __keywords,
        __securityConstraint.name() : __securityConstraint,
        __contact.name() : __contact,
        __member.name() : __member,
        __legalConstraint.name() : __legalConstraint,
        __documentation.name() : __documentation,
        __identification.name() : __identification,
        __classification.name() : __classification,
        __history.name() : __history
    }
    _AttributeMap = {
        __version.name() : __version
    }



# Complex type CTD_ANON_55 with content type ELEMENT_ONLY
class CTD_ANON_55 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}_Process uses Python identifier Process
    __Process = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_Process'), 'Process', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_opengis_netsensorML1_0_1_Process', False)

    
    Process = property(__Process.value, __Process.set, None, u'base substitution group for all processes')

    
    # Element {http://www.opengis.net/swe/1.0.1}Position uses Python identifier Position
    __Position = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Position'), 'Position', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_opengis_netswe1_0_1Position', False)

    
    Position = property(__Position.value, __Position.set, None, u'Position is given as a group of Vectors/Matrices, each of which can specify location, orientation, velocity, angularVelocity, acceleration or angularAcceleration or a combination of those in a composite state Vector. Each Vector can have a separate frame of reference or inherit the frame from the parent Position object.')

    
    # Element {http://www.opengis.net/swe/1.0.1}Vector uses Python identifier Vector
    __Vector = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Vector'), 'Vector', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_opengis_netswe1_0_1Vector', False)

    
    Vector = property(__Vector.value, __Vector.set, None, u'A Vector is a special type of DataRecord that takes a list of numerical scalars called coordinates. The Vector has a referenceFrame in which the coordinates are expressed')

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_name', pyxb.binding.datatypes.token, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_55_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)


    _ElementMap = {
        __Process.name() : __Process,
        __Position.name() : __Position,
        __Vector.name() : __Vector
    }
    _AttributeMap = {
        __show.name() : __show,
        __role.name() : __role,
        __href.name() : __href,
        __title.name() : __title,
        __remoteSchema.name() : __remoteSchema,
        __name.name() : __name,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __arcrole.name() : __arcrole
    }



# Complex type outputsPropertyType with content type ELEMENT_ONLY
class outputsPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'outputsPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}OutputList uses Python identifier OutputList
    __OutputList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OutputList'), 'OutputList', '__httpwww_opengis_netsensorML1_0_1_outputsPropertyType_httpwww_opengis_netsensorML1_0_1OutputList', False)

    
    OutputList = property(__OutputList.value, __OutputList.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_outputsPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_outputsPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_outputsPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_outputsPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_outputsPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_outputsPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_outputsPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_outputsPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)


    _ElementMap = {
        __OutputList.name() : __OutputList
    }
    _AttributeMap = {
        __actuate.name() : __actuate,
        __remoteSchema.name() : __remoteSchema,
        __type.name() : __type,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __show.name() : __show,
        __role.name() : __role,
        __title.name() : __title
    }
Namespace.addCategoryObject('typeBinding', u'outputsPropertyType', outputsPropertyType)


# Complex type IoComponentPropertyType with content type ELEMENT_ONLY
class IoComponentPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IoComponentPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/swe/1.0.1}QuantityRange uses Python identifier QuantityRange
    __QuantityRange = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'QuantityRange'), 'QuantityRange', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1QuantityRange', False)

    
    QuantityRange = property(__QuantityRange.value, __QuantityRange.set, None, u'Decimal pair for specifying a quantity range with constraints')

    
    # Element {http://www.opengis.net/swe/1.0.1}Quantity uses Python identifier Quantity
    __Quantity = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Quantity'), 'Quantity', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1Quantity', False)

    
    Quantity = property(__Quantity.value, __Quantity.set, None, u'Decimal number with optional unit and constraints')

    
    # Element {http://www.opengis.net/swe/1.0.1}Time uses Python identifier Time
    __Time = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Time'), 'Time', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1Time', False)

    
    Time = property(__Time.value, __Time.set, None, u'Either ISO 8601 (e.g. 2004-04-18T12:03:04.6Z) or time relative to a time origin')

    
    # Element {http://www.opengis.net/swe/1.0.1}CountRange uses Python identifier CountRange
    __CountRange = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'CountRange'), 'CountRange', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1CountRange', False)

    
    CountRange = property(__CountRange.value, __CountRange.set, None, u'Integer pair used for specifying a count range')

    
    # Element {http://www.opengis.net/swe/1.0.1}AbstractDataArray uses Python identifier AbstractDataArray
    __AbstractDataArray = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataArray'), 'AbstractDataArray', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1AbstractDataArray', False)

    
    AbstractDataArray = property(__AbstractDataArray.value, __AbstractDataArray.set, None, u'Implemetation of ISO-11404 Array datatype. This defines an array of identical data components with a elementCount. Values are given as a block and can be encoded in different ways')

    
    # Element {http://www.opengis.net/swe/1.0.1}Boolean uses Python identifier Boolean
    __Boolean = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Boolean'), 'Boolean', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1Boolean', False)

    
    Boolean = property(__Boolean.value, __Boolean.set, None, u'Scalar component used to express truth: True or False, 0 or 1')

    
    # Element {http://www.opengis.net/swe/1.0.1}TimeRange uses Python identifier TimeRange
    __TimeRange = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'TimeRange'), 'TimeRange', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1TimeRange', False)

    
    TimeRange = property(__TimeRange.value, __TimeRange.set, None, u'Time value pair for specifying a time range (can be a decimal or ISO 8601)')

    
    # Element {http://www.opengis.net/swe/1.0.1}Count uses Python identifier Count
    __Count = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Count'), 'Count', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1Count', False)

    
    Count = property(__Count.value, __Count.set, None, u'Integer number used for a counting value')

    
    # Element {http://www.opengis.net/swe/1.0.1}Category uses Python identifier Category
    __Category = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Category'), 'Category', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1Category', False)

    
    Category = property(__Category.value, __Category.set, None, u'A simple token identifying a term or category (single spaces allowed); definition attribute should provide dictionary entry useful for interpretation of the value')

    
    # Element {http://www.opengis.net/swe/1.0.1}AbstractDataRecord uses Python identifier AbstractDataRecord
    __AbstractDataRecord = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'), 'AbstractDataRecord', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1AbstractDataRecord', False)

    
    AbstractDataRecord = property(__AbstractDataRecord.value, __AbstractDataRecord.set, None, None)

    
    # Element {http://www.opengis.net/swe/1.0.1}Text uses Python identifier Text
    __Text = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Text'), 'Text', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1Text', False)

    
    Text = property(__Text.value, __Text.set, None, u'Free textual component')

    
    # Element {http://www.opengis.net/swe/1.0.1}ObservableProperty uses Python identifier ObservableProperty
    __ObservableProperty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'ObservableProperty'), 'ObservableProperty', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netswe1_0_1ObservableProperty', False)

    
    ObservableProperty = property(__ObservableProperty.value, __ObservableProperty.set, None, u'ObservableProperty should be used to identify (through reference only) stimuli or measurable property types. The consequence is that it does not have a uom because it has not been measured yet.  This is used to define sensor/detector/actuator inputs and outputs, for instance.')

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_name', pyxb.binding.datatypes.token, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_IoComponentPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)


    _ElementMap = {
        __QuantityRange.name() : __QuantityRange,
        __Quantity.name() : __Quantity,
        __Time.name() : __Time,
        __CountRange.name() : __CountRange,
        __AbstractDataArray.name() : __AbstractDataArray,
        __Boolean.name() : __Boolean,
        __TimeRange.name() : __TimeRange,
        __Count.name() : __Count,
        __Category.name() : __Category,
        __AbstractDataRecord.name() : __AbstractDataRecord,
        __Text.name() : __Text,
        __ObservableProperty.name() : __ObservableProperty
    }
    _AttributeMap = {
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __href.name() : __href,
        __role.name() : __role,
        __remoteSchema.name() : __remoteSchema,
        __name.name() : __name,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __title.name() : __title
    }
Namespace.addCategoryObject('typeBinding', u'IoComponentPropertyType', IoComponentPropertyType)


# Complex type CTD_ANON_56 with content type ELEMENT_ONLY
class CTD_ANON_56 (ruleLanguageType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is ruleLanguageType
    
    # Attribute show inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute href inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute title inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute role inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute arcrole inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute actuate inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute type inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    _HasWildcardElement = True

    _ElementMap = ruleLanguageType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ruleLanguageType._AttributeMap.copy()
    _AttributeMap.update({
        
    })



# Complex type CTD_ANON_57 with content type ELEMENT_ONLY
class CTD_ANON_57 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/swe/1.0.1}DataBlockDefinition uses Python identifier DataBlockDefinition
    __DataBlockDefinition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataBlockDefinition'), 'DataBlockDefinition', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_57_httpwww_opengis_netswe1_0_1DataBlockDefinition', False)

    
    DataBlockDefinition = property(__DataBlockDefinition.value, __DataBlockDefinition.set, None, None)

    
    # Element {http://www.opengis.net/swe/1.0.1}DataStreamDefinition uses Python identifier DataStreamDefinition
    __DataStreamDefinition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataStreamDefinition'), 'DataStreamDefinition', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_57_httpwww_opengis_netswe1_0_1DataStreamDefinition', False)

    
    DataStreamDefinition = property(__DataStreamDefinition.value, __DataStreamDefinition.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_57_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_57_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_57_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_57_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_57_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_57_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_57_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_57_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __DataBlockDefinition.name() : __DataBlockDefinition,
        __DataStreamDefinition.name() : __DataStreamDefinition
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __actuate.name() : __actuate,
        __role.name() : __role,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __title.name() : __title,
        __type.name() : __type
    }



# Complex type CTD_ANON_58 with content type ELEMENT_ONLY
class CTD_ANON_58 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}member uses Python identifier member
    __member = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'member'), 'member', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_58_httpwww_opengis_netsensorML1_0_1member', True)

    
    member = property(__member.value, __member.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_58_httpwww_opengis_netgmlid', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, u'Database handle for the object.  It is of XML type ID, so is constrained to be unique in the XML document within which it occurs.  An external identifier for the object in the form of a URI may be constructed using standard XML and XPointer methods.  This is done by concatenating the URI for the document, a fragment separator, and the value of the id attribute.')


    _ElementMap = {
        __member.name() : __member
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type ProcessChainType with content type ELEMENT_ONLY
class ProcessChainType (AbstractPureProcessType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ProcessChainType')
    # Base type is AbstractPureProcessType
    
    # Element parameters ({http://www.opengis.net/sensorML/1.0.1}parameters) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractPureProcessType
    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}components uses Python identifier components
    __components = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'components'), 'components', '__httpwww_opengis_netsensorML1_0_1_ProcessChainType_httpwww_opengis_netsensorML1_0_1components', False)

    
    components = property(__components.value, __components.set, None, u'Collection of subprocesses that can be chained using connections')

    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}connections uses Python identifier connections
    __connections = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'connections'), 'connections', '__httpwww_opengis_netsensorML1_0_1_ProcessChainType_httpwww_opengis_netsensorML1_0_1connections', False)

    
    connections = property(__connections.value, __connections.set, None, u'provides links between processes or between data sources and processes')

    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element outputs ({http://www.opengis.net/sensorML/1.0.1}outputs) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractPureProcessType
    
    # Element inputs ({http://www.opengis.net/sensorML/1.0.1}inputs) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractPureProcessType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractPureProcessType._ElementMap.copy()
    _ElementMap.update({
        __components.name() : __components,
        __connections.name() : __connections
    })
    _AttributeMap = AbstractPureProcessType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ProcessChainType', ProcessChainType)


# Complex type CTD_ANON_59 with content type ELEMENT_ONLY
class CTD_ANON_59 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}position uses Python identifier position
    __position = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'position'), 'position', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_59_httpwww_opengis_netsensorML1_0_1position', True)

    
    position = property(__position.value, __position.set, None, u'Full position (location + orientation) given by a swe:Position or a Process (if variable)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}timePosition uses Python identifier timePosition
    __timePosition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'timePosition'), 'timePosition', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_59_httpwww_opengis_netsensorML1_0_1timePosition', False)

    
    timePosition = property(__timePosition.value, __timePosition.set, None, u'Provide the ability to relate  a local time frame to a reference time frame')

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_59_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)


    _ElementMap = {
        __position.name() : __position,
        __timePosition.name() : __timePosition
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type ComponentArrayType with content type ELEMENT_ONLY
class ComponentArrayType (AbstractDerivableComponentType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ComponentArrayType')
    # Base type is AbstractDerivableComponentType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}inputs uses Python identifier inputs
    __inputs = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'inputs'), 'inputs', '__httpwww_opengis_netsensorML1_0_1_ComponentArrayType_httpwww_opengis_netsensorML1_0_1inputs', False)

    
    inputs = property(__inputs.value, __inputs.set, None, u'list of input signals')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}outputs uses Python identifier outputs
    __outputs = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'outputs'), 'outputs', '__httpwww_opengis_netsensorML1_0_1_ComponentArrayType_httpwww_opengis_netsensorML1_0_1outputs', False)

    
    outputs = property(__outputs.value, __outputs.set, None, u'list of output signals')

    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}connections uses Python identifier connections
    __connections = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'connections'), 'connections', '__httpwww_opengis_netsensorML1_0_1_ComponentArrayType_httpwww_opengis_netsensorML1_0_1connections', False)

    
    connections = property(__connections.value, __connections.set, None, u'provides links between processes or between data sources and processes')

    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}components uses Python identifier components
    __components = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'components'), 'components', '__httpwww_opengis_netsensorML1_0_1_ComponentArrayType_httpwww_opengis_netsensorML1_0_1components', False)

    
    components = property(__components.value, __components.set, None, u'Collection of subprocesses that can be chained using connections')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}positions uses Python identifier positions
    __positions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'positions'), 'positions', '__httpwww_opengis_netsensorML1_0_1_ComponentArrayType_httpwww_opengis_netsensorML1_0_1positions', False)

    
    positions = property(__positions.value, __positions.set, None, u'Relative positions of the System components')

    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element spatialReferenceFrame ({http://www.opengis.net/sensorML/1.0.1}spatialReferenceFrame) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element temporalReferenceFrame ({http://www.opengis.net/sensorML/1.0.1}temporalReferenceFrame) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}parameters uses Python identifier parameters
    __parameters = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'parameters'), 'parameters', '__httpwww_opengis_netsensorML1_0_1_ComponentArrayType_httpwww_opengis_netsensorML1_0_1parameters', False)

    
    parameters = property(__parameters.value, __parameters.set, None, None)

    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element position ({http://www.opengis.net/sensorML/1.0.1}position) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element timePosition ({http://www.opengis.net/sensorML/1.0.1}timePosition) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element interfaces ({http://www.opengis.net/sensorML/1.0.1}interfaces) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element location_ ({http://www.opengis.net/sensorML/1.0.1}location) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractDerivableComponentType._ElementMap.copy()
    _ElementMap.update({
        __inputs.name() : __inputs,
        __outputs.name() : __outputs,
        __connections.name() : __connections,
        __components.name() : __components,
        __positions.name() : __positions,
        __parameters.name() : __parameters
    })
    _AttributeMap = AbstractDerivableComponentType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ComponentArrayType', ComponentArrayType)


# Complex type AbstractDerivableProcessType with content type ELEMENT_ONLY
class AbstractDerivableProcessType (AbstractProcessType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractDerivableProcessType')
    # Base type is AbstractProcessType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}outputs uses Python identifier outputs
    __outputs = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'outputs'), 'outputs', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableProcessType_httpwww_opengis_netsensorML1_0_1outputs', False)

    
    outputs = property(__outputs.value, __outputs.set, None, None)

    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}method uses Python identifier method
    __method = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'method'), 'method', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableProcessType_httpwww_opengis_netsensorML1_0_1method', False)

    
    method = property(__method.value, __method.set, None, u'process method')

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}inputs uses Python identifier inputs
    __inputs = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'inputs'), 'inputs', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableProcessType_httpwww_opengis_netsensorML1_0_1inputs', False)

    
    inputs = property(__inputs.value, __inputs.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}dataSources uses Python identifier dataSources
    __dataSources = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'dataSources'), 'dataSources', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableProcessType_httpwww_opengis_netsensorML1_0_1dataSources', False)

    
    dataSources = property(__dataSources.value, __dataSources.set, None, None)

    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}parameters uses Python identifier parameters
    __parameters = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'parameters'), 'parameters', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableProcessType_httpwww_opengis_netsensorML1_0_1parameters', False)

    
    parameters = property(__parameters.value, __parameters.set, None, None)

    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}connections uses Python identifier connections
    __connections = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'connections'), 'connections', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableProcessType_httpwww_opengis_netsensorML1_0_1connections', False)

    
    connections = property(__connections.value, __connections.set, None, None)

    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}components uses Python identifier components
    __components = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'components'), 'components', '__httpwww_opengis_netsensorML1_0_1_AbstractDerivableProcessType_httpwww_opengis_netsensorML1_0_1components', False)

    
    components = property(__components.value, __components.set, None, None)

    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractProcessType._ElementMap.copy()
    _ElementMap.update({
        __outputs.name() : __outputs,
        __method.name() : __method,
        __inputs.name() : __inputs,
        __dataSources.name() : __dataSources,
        __parameters.name() : __parameters,
        __connections.name() : __connections,
        __components.name() : __components
    })
    _AttributeMap = AbstractProcessType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractDerivableProcessType', AbstractDerivableProcessType)


# Complex type parametersPropertyType with content type ELEMENT_ONLY
class parametersPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'parametersPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}ParameterList uses Python identifier ParameterList
    __ParameterList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ParameterList'), 'ParameterList', '__httpwww_opengis_netsensorML1_0_1_parametersPropertyType_httpwww_opengis_netsensorML1_0_1ParameterList', False)

    
    ParameterList = property(__ParameterList.value, __ParameterList.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_parametersPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_parametersPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_parametersPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_parametersPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_parametersPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_parametersPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_parametersPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_parametersPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")


    _ElementMap = {
        __ParameterList.name() : __ParameterList
    }
    _AttributeMap = {
        __type.name() : __type,
        __remoteSchema.name() : __remoteSchema,
        __role.name() : __role,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __title.name() : __title,
        __show.name() : __show,
        __actuate.name() : __actuate
    }
Namespace.addCategoryObject('typeBinding', u'parametersPropertyType', parametersPropertyType)


# Complex type CTD_ANON_60 with content type EMPTY
class CTD_ANON_60 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_60_ref', linkRef)
    
    ref = property(__ref.value, __ref.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __ref.name() : __ref
    }



# Complex type CTD_ANON_61 with content type ELEMENT_ONLY
class CTD_ANON_61 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}InputList uses Python identifier InputList
    __InputList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'InputList'), 'InputList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_61_httpwww_opengis_netsensorML1_0_1InputList', False)

    
    InputList = property(__InputList.value, __InputList.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_61_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_61_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_61_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_61_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_61_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_61_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_61_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_61_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        __InputList.name() : __InputList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __actuate.name() : __actuate,
        __role.name() : __role,
        __type.name() : __type,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __title.name() : __title,
        __href.name() : __href
    }



# Complex type CTD_ANON_62 with content type ELEMENT_ONLY
class CTD_ANON_62 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}interface uses Python identifier interface
    __interface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'interface'), 'interface', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_62_httpwww_opengis_netsensorML1_0_1interface', True)

    
    interface = property(__interface.value, __interface.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_62_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)


    _ElementMap = {
        __interface.name() : __interface
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type CTD_ANON_63 with content type EMPTY
class CTD_ANON_63 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_63_ref', linkRef, required=True)
    
    ref = property(__ref.value, __ref.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __ref.name() : __ref
    }



# Complex type CTD_ANON_64 with content type ELEMENT_ONLY
class CTD_ANON_64 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}_Process uses Python identifier Process
    __Process = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_Process'), 'Process', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_64_httpwww_opengis_netsensorML1_0_1_Process', False)

    
    Process = property(__Process.value, __Process.set, None, u'base substitution group for all processes')

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_64_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_64_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_64_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_64_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_64_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_64_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_64_name', pyxb.binding.datatypes.token, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_64_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_64_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')


    _ElementMap = {
        __Process.name() : __Process
    }
    _AttributeMap = {
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __actuate.name() : __actuate,
        __show.name() : __show,
        __type.name() : __type,
        __name.name() : __name,
        __role.name() : __role,
        __remoteSchema.name() : __remoteSchema
    }



# Complex type CTD_ANON_65 with content type ELEMENT_ONLY
class CTD_ANON_65 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}documentation uses Python identifier documentation
    __documentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'documentation'), 'documentation', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_65_httpwww_opengis_netsensorML1_0_1documentation', False)

    
    documentation = property(__documentation.value, __documentation.set, None, u'Relevant documentation for that object')

    
    # Attribute copyRights uses Python identifier copyRights
    __copyRights = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'copyRights'), 'copyRights', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_65_copyRights', pyxb.binding.datatypes.boolean)
    
    copyRights = property(__copyRights.value, __copyRights.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_65_httpwww_opengis_netgmlid', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, u'Database handle for the object.  It is of XML type ID, so is constrained to be unique in the XML document within which it occurs.  An external identifier for the object in the form of a URI may be constructed using standard XML and XPointer methods.  This is done by concatenating the URI for the document, a fragment separator, and the value of the id attribute.')

    
    # Attribute privacyAct uses Python identifier privacyAct
    __privacyAct = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'privacyAct'), 'privacyAct', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_65_privacyAct', pyxb.binding.datatypes.boolean)
    
    privacyAct = property(__privacyAct.value, __privacyAct.set, None, None)

    
    # Attribute intellectualPropertyRights uses Python identifier intellectualPropertyRights
    __intellectualPropertyRights = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'intellectualPropertyRights'), 'intellectualPropertyRights', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_65_intellectualPropertyRights', pyxb.binding.datatypes.boolean)
    
    intellectualPropertyRights = property(__intellectualPropertyRights.value, __intellectualPropertyRights.set, None, None)


    _ElementMap = {
        __documentation.name() : __documentation
    }
    _AttributeMap = {
        __copyRights.name() : __copyRights,
        __id.name() : __id,
        __privacyAct.name() : __privacyAct,
        __intellectualPropertyRights.name() : __intellectualPropertyRights
    }



# Complex type CTD_ANON_66 with content type ELEMENT_ONLY
class CTD_ANON_66 (AbstractListType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is AbstractListType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}parameter uses Python identifier parameter
    __parameter = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'parameter'), 'parameter', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_66_httpwww_opengis_netsensorML1_0_1parameter', True)

    
    parameter = property(__parameter.value, __parameter.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}index uses Python identifier index
    __index = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'index'), 'index', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_66_httpwww_opengis_netsensorML1_0_1index', True)

    
    index = property(__index.value, __index.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractListType

    _ElementMap = AbstractListType._ElementMap.copy()
    _ElementMap.update({
        __parameter.name() : __parameter,
        __index.name() : __index
    })
    _AttributeMap = AbstractListType._AttributeMap.copy()
    _AttributeMap.update({
        
    })



# Complex type ProcessMethodType with content type ELEMENT_ONLY
class ProcessMethodType (pyxb.bundles.opengis.gml.AbstractGMLType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ProcessMethodType')
    # Base type is pyxb.bundles.opengis.gml.AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}documentation uses Python identifier documentation
    __documentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'documentation'), 'documentation', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1documentation', True)

    
    documentation = property(__documentation.value, __documentation.set, None, u'Relevant documentation for that object')

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}history uses Python identifier history
    __history = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'history'), 'history', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1history', True)

    
    history = property(__history.value, __history.set, None, u'History of the object described (Recalibration, adjustments, etc...)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}identification uses Python identifier identification
    __identification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'identification'), 'identification', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1identification', True)

    
    identification = property(__identification.value, __identification.set, None, u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary')

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}validTime uses Python identifier validTime
    __validTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'validTime'), 'validTime', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1validTime', False)

    
    validTime = property(__validTime.value, __validTime.set, None, u'Means of providing time validity constraint of description')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}characteristics uses Python identifier characteristics
    __characteristics = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'characteristics'), 'characteristics', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1characteristics', True)

    
    characteristics = property(__characteristics.value, __characteristics.set, None, u'Characteristic list for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}keywords uses Python identifier keywords
    __keywords = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'keywords'), 'keywords', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1keywords', True)

    
    keywords = property(__keywords.value, __keywords.set, None, u'Means of providing a list of keywords (with a codeSpace) for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}classification uses Python identifier classification
    __classification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'classification'), 'classification', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1classification', True)

    
    classification = property(__classification.value, __classification.set, None, u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}capabilities uses Python identifier capabilities
    __capabilities = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'capabilities'), 'capabilities', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1capabilities', True)

    
    capabilities = property(__capabilities.value, __capabilities.set, None, u'Capability list for quick discovery')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}implementation uses Python identifier implementation
    __implementation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'implementation'), 'implementation', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1implementation', True)

    
    implementation = property(__implementation.value, __implementation.set, None, u'Points to the reference implementation of this process in the specified programming language (can be a SensorML process chain)')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}legalConstraint uses Python identifier legalConstraint
    __legalConstraint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'), 'legalConstraint', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1legalConstraint', True)

    
    legalConstraint = property(__legalConstraint.value, __legalConstraint.set, None, u'Means of providing legal constraints of description')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}rules uses Python identifier rules
    __rules = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'rules'), 'rules', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1rules', False)

    
    rules = property(__rules.value, __rules.set, None, u'Text and/or language defining rules for process profile (e.g. inputs, outputs, parameters, and metadata)')

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}contact uses Python identifier contact
    __contact = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'contact'), 'contact', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1contact', True)

    
    contact = property(__contact.value, __contact.set, None, u'Relevant contacts for that object')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}securityConstraint uses Python identifier securityConstraint
    __securityConstraint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'), 'securityConstraint', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1securityConstraint', False)

    
    securityConstraint = property(__securityConstraint.value, __securityConstraint.set, None, u'Means of providing security constraints of description')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}algorithm uses Python identifier algorithm
    __algorithm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'algorithm'), 'algorithm', '__httpwww_opengis_netsensorML1_0_1_ProcessMethodType_httpwww_opengis_netsensorML1_0_1algorithm', False)

    
    algorithm = property(__algorithm.value, __algorithm.set, None, u'Textual and/or MathML description of the algorithm')

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractGMLType._ElementMap.copy()
    _ElementMap.update({
        __documentation.name() : __documentation,
        __history.name() : __history,
        __identification.name() : __identification,
        __validTime.name() : __validTime,
        __characteristics.name() : __characteristics,
        __keywords.name() : __keywords,
        __classification.name() : __classification,
        __capabilities.name() : __capabilities,
        __implementation.name() : __implementation,
        __legalConstraint.name() : __legalConstraint,
        __rules.name() : __rules,
        __contact.name() : __contact,
        __securityConstraint.name() : __securityConstraint,
        __algorithm.name() : __algorithm
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractGMLType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ProcessMethodType', ProcessMethodType)


# Complex type SystemType with content type ELEMENT_ONLY
class SystemType (AbstractComponentType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SystemType')
    # Base type is AbstractComponentType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element spatialReferenceFrame ({http://www.opengis.net/sensorML/1.0.1}spatialReferenceFrame) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}positions uses Python identifier positions
    __positions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'positions'), 'positions', '__httpwww_opengis_netsensorML1_0_1_SystemType_httpwww_opengis_netsensorML1_0_1positions', False)

    
    positions = property(__positions.value, __positions.set, None, u'Relative positions of the System components')

    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element temporalReferenceFrame ({http://www.opengis.net/sensorML/1.0.1}temporalReferenceFrame) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element position ({http://www.opengis.net/sensorML/1.0.1}position) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element timePosition ({http://www.opengis.net/sensorML/1.0.1}timePosition) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element interfaces ({http://www.opengis.net/sensorML/1.0.1}interfaces) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}components uses Python identifier components
    __components = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'components'), 'components', '__httpwww_opengis_netsensorML1_0_1_SystemType_httpwww_opengis_netsensorML1_0_1components', False)

    
    components = property(__components.value, __components.set, None, u'Collection of subprocesses that can be chained using connections')

    
    # Element location_ ({http://www.opengis.net/sensorML/1.0.1}location) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractDerivableComponentType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}connections uses Python identifier connections
    __connections = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'connections'), 'connections', '__httpwww_opengis_netsensorML1_0_1_SystemType_httpwww_opengis_netsensorML1_0_1connections', False)

    
    connections = property(__connections.value, __connections.set, None, u'provides links between processes or between data sources and processes')

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element inputs ({http://www.opengis.net/sensorML/1.0.1}inputs) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractComponentType
    
    # Element outputs ({http://www.opengis.net/sensorML/1.0.1}outputs) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractComponentType
    
    # Element parameters ({http://www.opengis.net/sensorML/1.0.1}parameters) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractComponentType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractComponentType._ElementMap.copy()
    _ElementMap.update({
        __positions.name() : __positions,
        __components.name() : __components,
        __connections.name() : __connections
    })
    _AttributeMap = AbstractComponentType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SystemType', SystemType)


# Complex type CTD_ANON_67 with content type ELEMENT_ONLY
class CTD_ANON_67 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}mathML uses Python identifier mathML
    __mathML = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'mathML'), 'mathML', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_67_httpwww_opengis_netsensorML1_0_1mathML', False)

    
    mathML = property(__mathML.value, __mathML.set, None, u'Includes or reference a MathML doc specifying the maths of the algorithm')

    
    # Element {http://www.opengis.net/gml}description uses Python identifier description
    __description = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), 'description', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_67_httpwww_opengis_netgmldescription', False)

    
    description = property(__description.value, __description.set, None, u'Contains a simple text description of the object, or refers to an external description.')


    _ElementMap = {
        __mathML.name() : __mathML,
        __description.name() : __description
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_68 with content type ELEMENT_ONLY
class CTD_ANON_68 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/swe/1.0.1}Time uses Python identifier Time
    __Time = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Time'), 'Time', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_httpwww_opengis_netswe1_0_1Time', False)

    
    Time = property(__Time.value, __Time.set, None, u'Either ISO 8601 (e.g. 2004-04-18T12:03:04.6Z) or time relative to a time origin')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}_Process uses Python identifier Process
    __Process = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_Process'), 'Process', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_httpwww_opengis_netsensorML1_0_1_Process', False)

    
    Process = property(__Process.value, __Process.set, None, u'base substitution group for all processes')

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_name', pyxb.binding.datatypes.token, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_68_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __Time.name() : __Time,
        __Process.name() : __Process
    }
    _AttributeMap = {
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __role.name() : __role,
        __title.name() : __title,
        __remoteSchema.name() : __remoteSchema,
        __name.name() : __name,
        __href.name() : __href,
        __actuate.name() : __actuate,
        __type.name() : __type
    }



# Complex type CTD_ANON_69 with content type ELEMENT_ONLY
class CTD_ANON_69 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}classifier uses Python identifier classifier
    __classifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'classifier'), 'classifier', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_69_httpwww_opengis_netsensorML1_0_1classifier', True)

    
    classifier = property(__classifier.value, __classifier.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_69_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)


    _ElementMap = {
        __classifier.name() : __classifier
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type CTD_ANON_70 with content type ELEMENT_ONLY
class CTD_ANON_70 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}destination uses Python identifier destination
    __destination = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'destination'), 'destination', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_70_httpwww_opengis_netsensorML1_0_1destination', False)

    
    destination = property(__destination.value, __destination.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}source uses Python identifier source
    __source = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'source'), 'source', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_70_httpwww_opengis_netsensorML1_0_1source', False)

    
    source = property(__source.value, __source.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_70_type', pyxb.binding.datatypes.anyURI)
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        __destination.name() : __destination,
        __source.name() : __source
    }
    _AttributeMap = {
        __type.name() : __type
    }



# Complex type CTD_ANON_71 with content type ELEMENT_ONLY
class CTD_ANON_71 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}PositionList uses Python identifier PositionList
    __PositionList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PositionList'), 'PositionList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_71_httpwww_opengis_netsensorML1_0_1PositionList', False)

    
    PositionList = property(__PositionList.value, __PositionList.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_71_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_71_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_71_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_71_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_71_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_71_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_71_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_71_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        __PositionList.name() : __PositionList
    }
    _AttributeMap = {
        __actuate.name() : __actuate,
        __remoteSchema.name() : __remoteSchema,
        __role.name() : __role,
        __type.name() : __type,
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __title.name() : __title,
        __href.name() : __href
    }



# Complex type CTD_ANON_72 with content type ELEMENT_ONLY
class CTD_ANON_72 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}_Process uses Python identifier Process
    __Process = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_Process'), 'Process', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_opengis_netsensorML1_0_1_Process', False)

    
    Process = property(__Process.value, __Process.set, None, u'base substitution group for all processes')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}DocumentList uses Python identifier DocumentList
    __DocumentList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DocumentList'), 'DocumentList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_opengis_netsensorML1_0_1DocumentList', False)

    
    DocumentList = property(__DocumentList.value, __DocumentList.set, None, u'List of documents related to the enclosing object')

    
    # Element {http://www.opengis.net/sensorML/1.0.1}ContactList uses Python identifier ContactList
    __ContactList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ContactList'), 'ContactList', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_opengis_netsensorML1_0_1ContactList', False)

    
    ContactList = property(__ContactList.value, __ContactList.set, None, u'Allows to group several contacts together in a list that can be referenced as a whole')

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_72_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        __Process.name() : __Process,
        __DocumentList.name() : __DocumentList,
        __ContactList.name() : __ContactList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __href.name() : __href,
        __title.name() : __title,
        __role.name() : __role
    }



# Complex type componentsPropertyType with content type ELEMENT_ONLY
class componentsPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'componentsPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}ProcessList uses Python identifier ProcessList
    __ProcessList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ProcessList'), 'ProcessList', '__httpwww_opengis_netsensorML1_0_1_componentsPropertyType_httpwww_opengis_netsensorML1_0_1ProcessList', False)

    
    ProcessList = property(__ProcessList.value, __ProcessList.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_componentsPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_componentsPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_componentsPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_componentsPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_componentsPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_componentsPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_componentsPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_componentsPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)


    _ElementMap = {
        __ProcessList.name() : __ProcessList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __href.name() : __href,
        __title.name() : __title,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __role.name() : __role
    }
Namespace.addCategoryObject('typeBinding', u'componentsPropertyType', componentsPropertyType)


# Complex type CTD_ANON_73 with content type EMPTY
class CTD_ANON_73 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_73_ref', linkRef, required=True)
    
    ref = property(__ref.value, __ref.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __ref.name() : __ref
    }



# Complex type CTD_ANON_74 with content type EMPTY
class CTD_ANON_74 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_74_ref', linkRef)
    
    ref = property(__ref.value, __ref.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __ref.name() : __ref
    }



# Complex type PresentationLayerPropertyType with content type ELEMENT_ONLY
class PresentationLayerPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PresentationLayerPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/swe/1.0.1}AbstractDataRecord uses Python identifier AbstractDataRecord
    __AbstractDataRecord = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'), 'AbstractDataRecord', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_opengis_netswe1_0_1AbstractDataRecord', False)

    
    AbstractDataRecord = property(__AbstractDataRecord.value, __AbstractDataRecord.set, None, None)

    
    # Element {http://www.opengis.net/swe/1.0.1}Category uses Python identifier Category
    __Category = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Category'), 'Category', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_opengis_netswe1_0_1Category', False)

    
    Category = property(__Category.value, __Category.set, None, u'A simple token identifying a term or category (single spaces allowed); definition attribute should provide dictionary entry useful for interpretation of the value')

    
    # Element {http://www.opengis.net/swe/1.0.1}DataStreamDefinition uses Python identifier DataStreamDefinition
    __DataStreamDefinition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataStreamDefinition'), 'DataStreamDefinition', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_opengis_netswe1_0_1DataStreamDefinition', False)

    
    DataStreamDefinition = property(__DataStreamDefinition.value, __DataStreamDefinition.set, None, None)

    
    # Element {http://www.opengis.net/swe/1.0.1}DataBlockDefinition uses Python identifier DataBlockDefinition
    __DataBlockDefinition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataBlockDefinition'), 'DataBlockDefinition', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_opengis_netswe1_0_1DataBlockDefinition', False)

    
    DataBlockDefinition = property(__DataBlockDefinition.value, __DataBlockDefinition.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_PresentationLayerPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")


    _ElementMap = {
        __AbstractDataRecord.name() : __AbstractDataRecord,
        __Category.name() : __Category,
        __DataStreamDefinition.name() : __DataStreamDefinition,
        __DataBlockDefinition.name() : __DataBlockDefinition
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __type.name() : __type,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __show.name() : __show,
        __role.name() : __role,
        __actuate.name() : __actuate
    }
Namespace.addCategoryObject('typeBinding', u'PresentationLayerPropertyType', PresentationLayerPropertyType)


# Complex type CTD_ANON_75 with content type ELEMENT_ONLY
class CTD_ANON_75 (parametersPropertyType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is parametersPropertyType
    
    # Element ParameterList ({http://www.opengis.net/sensorML/1.0.1}ParameterList) inherited from {http://www.opengis.net/sensorML/1.0.1}parametersPropertyType
    
    # Attribute type inherited from {http://www.opengis.net/sensorML/1.0.1}parametersPropertyType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/sensorML/1.0.1}parametersPropertyType
    
    # Attribute role inherited from {http://www.opengis.net/sensorML/1.0.1}parametersPropertyType
    
    # Attribute arcrole inherited from {http://www.opengis.net/sensorML/1.0.1}parametersPropertyType
    
    # Attribute href inherited from {http://www.opengis.net/sensorML/1.0.1}parametersPropertyType
    
    # Attribute title inherited from {http://www.opengis.net/sensorML/1.0.1}parametersPropertyType
    
    # Attribute show inherited from {http://www.opengis.net/sensorML/1.0.1}parametersPropertyType
    
    # Attribute actuate inherited from {http://www.opengis.net/sensorML/1.0.1}parametersPropertyType

    _ElementMap = parametersPropertyType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = parametersPropertyType._AttributeMap.copy()
    _AttributeMap.update({
        
    })



# Complex type CTD_ANON_76 with content type ELEMENT_ONLY
class CTD_ANON_76 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}RulesDefinition uses Python identifier RulesDefinition
    __RulesDefinition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RulesDefinition'), 'RulesDefinition', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_76_httpwww_opengis_netsensorML1_0_1RulesDefinition', False)

    
    RulesDefinition = property(__RulesDefinition.value, __RulesDefinition.set, None, None)


    _ElementMap = {
        __RulesDefinition.name() : __RulesDefinition
    }
    _AttributeMap = {
        
    }



# Complex type DataSourceType with content type ELEMENT_ONLY
class DataSourceType (AbstractProcessType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DataSourceType')
    # Base type is AbstractProcessType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element contact ({http://www.opengis.net/sensorML/1.0.1}contact) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element history ({http://www.opengis.net/sensorML/1.0.1}history) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element keywords ({http://www.opengis.net/sensorML/1.0.1}keywords) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element legalConstraint ({http://www.opengis.net/sensorML/1.0.1}legalConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element identification ({http://www.opengis.net/sensorML/1.0.1}identification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}dataDefinition uses Python identifier dataDefinition
    __dataDefinition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'), 'dataDefinition', '__httpwww_opengis_netsensorML1_0_1_DataSourceType_httpwww_opengis_netsensorML1_0_1dataDefinition', False)

    
    dataDefinition = property(__dataDefinition.value, __dataDefinition.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}observationReference uses Python identifier observationReference
    __observationReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'observationReference'), 'observationReference', '__httpwww_opengis_netsensorML1_0_1_DataSourceType_httpwww_opengis_netsensorML1_0_1observationReference', False)

    
    observationReference = property(__observationReference.value, __observationReference.set, None, None)

    
    # Element characteristics ({http://www.opengis.net/sensorML/1.0.1}characteristics) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}values uses Python identifier values
    __values = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'values'), 'values', '__httpwww_opengis_netsensorML1_0_1_DataSourceType_httpwww_opengis_netsensorML1_0_1values', False)

    
    values = property(__values.value, __values.set, None, None)

    
    # Element securityConstraint ({http://www.opengis.net/sensorML/1.0.1}securityConstraint) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element documentation ({http://www.opengis.net/sensorML/1.0.1}documentation) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element validTime ({http://www.opengis.net/sensorML/1.0.1}validTime) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element capabilities ({http://www.opengis.net/sensorML/1.0.1}capabilities) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Element classification ({http://www.opengis.net/sensorML/1.0.1}classification) inherited from {http://www.opengis.net/sensorML/1.0.1}AbstractProcessType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractProcessType._ElementMap.copy()
    _ElementMap.update({
        __dataDefinition.name() : __dataDefinition,
        __observationReference.name() : __observationReference,
        __values.name() : __values
    })
    _AttributeMap = AbstractProcessType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'DataSourceType', DataSourceType)


# Complex type CTD_ANON_77 with content type ELEMENT_ONLY
class CTD_ANON_77 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}city uses Python identifier city
    __city = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'city'), 'city', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_77_httpwww_opengis_netsensorML1_0_1city', False)

    
    city = property(__city.value, __city.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}administrativeArea uses Python identifier administrativeArea
    __administrativeArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'administrativeArea'), 'administrativeArea', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_77_httpwww_opengis_netsensorML1_0_1administrativeArea', False)

    
    administrativeArea = property(__administrativeArea.value, __administrativeArea.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}postalCode uses Python identifier postalCode
    __postalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'postalCode'), 'postalCode', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_77_httpwww_opengis_netsensorML1_0_1postalCode', False)

    
    postalCode = property(__postalCode.value, __postalCode.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}country uses Python identifier country
    __country = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'country'), 'country', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_77_httpwww_opengis_netsensorML1_0_1country', False)

    
    country = property(__country.value, __country.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}deliveryPoint uses Python identifier deliveryPoint
    __deliveryPoint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'deliveryPoint'), 'deliveryPoint', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_77_httpwww_opengis_netsensorML1_0_1deliveryPoint', True)

    
    deliveryPoint = property(__deliveryPoint.value, __deliveryPoint.set, None, None)

    
    # Element {http://www.opengis.net/sensorML/1.0.1}electronicMailAddress uses Python identifier electronicMailAddress
    __electronicMailAddress = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'electronicMailAddress'), 'electronicMailAddress', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_77_httpwww_opengis_netsensorML1_0_1electronicMailAddress', False)

    
    electronicMailAddress = property(__electronicMailAddress.value, __electronicMailAddress.set, None, None)


    _ElementMap = {
        __city.name() : __city,
        __administrativeArea.name() : __administrativeArea,
        __postalCode.name() : __postalCode,
        __country.name() : __country,
        __deliveryPoint.name() : __deliveryPoint,
        __electronicMailAddress.name() : __electronicMailAddress
    }
    _AttributeMap = {
        
    }



# Complex type inputsPropertyType with content type ELEMENT_ONLY
class inputsPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'inputsPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}InputList uses Python identifier InputList
    __InputList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'InputList'), 'InputList', '__httpwww_opengis_netsensorML1_0_1_inputsPropertyType_httpwww_opengis_netsensorML1_0_1InputList', False)

    
    InputList = property(__InputList.value, __InputList.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netsensorML1_0_1_inputsPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netsensorML1_0_1_inputsPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_1)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netsensorML1_0_1_inputsPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netsensorML1_0_1_inputsPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netsensorML1_0_1_inputsPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netsensorML1_0_1_inputsPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netsensorML1_0_1_inputsPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON_2)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netsensorML1_0_1_inputsPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        __InputList.name() : __InputList
    }
    _AttributeMap = {
        __remoteSchema.name() : __remoteSchema,
        __show.name() : __show,
        __role.name() : __role,
        __type.name() : __type,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __actuate.name() : __actuate,
        __href.name() : __href
    }
Namespace.addCategoryObject('typeBinding', u'inputsPropertyType', inputsPropertyType)


# Complex type CTD_ANON_78 with content type ELEMENT_ONLY
class CTD_ANON_78 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}ruleLanguage uses Python identifier ruleLanguage
    __ruleLanguage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ruleLanguage'), 'ruleLanguage', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_78_httpwww_opengis_netsensorML1_0_1ruleLanguage', False)

    
    ruleLanguage = property(__ruleLanguage.value, __ruleLanguage.set, None, u'substitutionGroup for languages that define rules')

    
    # Element {http://www.opengis.net/gml}description uses Python identifier description
    __description = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), 'description', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_78_httpwww_opengis_netgmldescription', False)

    
    description = property(__description.value, __description.set, None, u'Contains a simple text description of the object, or refers to an external description.')


    _ElementMap = {
        __ruleLanguage.name() : __ruleLanguage,
        __description.name() : __description
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_79 with content type ELEMENT_ONLY
class CTD_ANON_79 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}identifier uses Python identifier identifier
    __identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'identifier'), 'identifier', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_79_httpwww_opengis_netsensorML1_0_1identifier', True)

    
    identifier = property(__identifier.value, __identifier.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_79_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)


    _ElementMap = {
        __identifier.name() : __identifier
    }
    _AttributeMap = {
        __id.name() : __id
    }



# Complex type CTD_ANON_80 with content type MIXED
class CTD_ANON_80 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_81 with content type ELEMENT_ONLY
class CTD_ANON_81 (ruleLanguageType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is ruleLanguageType
    
    # Attribute show inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute href inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute title inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute role inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute arcrole inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute actuate inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    
    # Attribute type inherited from {http://www.opengis.net/sensorML/1.0.1}ruleLanguageType
    _HasWildcardElement = True

    _ElementMap = ruleLanguageType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ruleLanguageType._AttributeMap.copy()
    _AttributeMap.update({
        
    })



# Complex type CTD_ANON_82 with content type ELEMENT_ONLY
class CTD_ANON_82 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}Term uses Python identifier Term
    __Term = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Term'), 'Term', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_82_httpwww_opengis_netsensorML1_0_1Term', False)

    
    Term = property(__Term.value, __Term.set, None, u'A well defined token used to specify identifier and classifier values (single spaces allowed)')

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_82_name', pyxb.binding.datatypes.token)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        __Term.name() : __Term
    }
    _AttributeMap = {
        __name.name() : __name
    }



# Complex type CTD_ANON_83 with content type ELEMENT_ONLY
class CTD_ANON_83 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/sensorML/1.0.1}parameter uses Python identifier parameter
    __parameter = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'parameter'), 'parameter', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_83_httpwww_opengis_netsensorML1_0_1parameter', True)

    
    parameter = property(__parameter.value, __parameter.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netsensorML1_0_1_CTD_ANON_83_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)


    _ElementMap = {
        __parameter.name() : __parameter
    }
    _AttributeMap = {
        __id.name() : __id
    }



ProcessModel = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProcessModel'), ProcessModelType, documentation=u'Simple atomic process defined using a ProcessMethod')
Namespace.addCategoryObject('elementBinding', ProcessModel.name().localName(), ProcessModel)

outputs = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outputs'), CTD_ANON_6, documentation=u'list of output signals')
Namespace.addCategoryObject('elementBinding', outputs.name().localName(), outputs)

spatialReferenceFrame = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'), CTD_ANON_16, documentation=u'Textual definition of a spatial frame axes (origin, orientation). Spatial frames can be related to one another by specifying relative positions.')
Namespace.addCategoryObject('elementBinding', spatialReferenceFrame.name().localName(), spatialReferenceFrame)

Term = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Term'), CTD_ANON_20, documentation=u'A well defined token used to specify identifier and classifier values (single spaces allowed)')
Namespace.addCategoryObject('elementBinding', Term.name().localName(), Term)

location = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'location'), CTD_ANON_22, documentation=u'Uses a gml:Point for a fixed location or a (time dependant) curve for time variable location')
Namespace.addCategoryObject('elementBinding', location.name().localName(), location)

contact = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'contact'), CTD_ANON_13, documentation=u'Relevant contacts for that object')
Namespace.addCategoryObject('elementBinding', contact.name().localName(), contact)

DocumentList = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DocumentList'), CTD_ANON_24, documentation=u'List of documents related to the enclosing object')
Namespace.addCategoryObject('elementBinding', DocumentList.name().localName(), DocumentList)

ruleLanguage = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ruleLanguage'), ruleLanguageType, abstract=pyxb.binding.datatypes.boolean(1), documentation=u'substitutionGroup for languages that define rules')
Namespace.addCategoryObject('elementBinding', ruleLanguage.name().localName(), ruleLanguage)

Document = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Document'), CTD_ANON_31, documentation=u'Document record with date/time, version, author, etc. pointing to an online resource related to the enclosing object')
Namespace.addCategoryObject('elementBinding', Document.name().localName(), Document)

Security = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Security'), CTD_ANON_33, documentation=u'based on IC:ISM definition')
Namespace.addCategoryObject('elementBinding', Security.name().localName(), Security)

Process = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Process'), AbstractProcessType, abstract=pyxb.binding.datatypes.boolean(1), documentation=u'base substitution group for all processes')
Namespace.addCategoryObject('elementBinding', Process.name().localName(), Process)

connection = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'connection'), CTD_ANON_37, documentation=u'Specify a connection between two elements')
Namespace.addCategoryObject('elementBinding', connection.name().localName(), connection)

Event = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Event'), CTD_ANON_38, documentation=u'Event record (change to the object) including a date/time, description, identification and additional references and metadata')
Namespace.addCategoryObject('elementBinding', Event.name().localName(), Event)

classification = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'classification'), CTD_ANON_7, documentation=u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary')
Namespace.addCategoryObject('elementBinding', classification.name().localName(), classification)

connections = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'connections'), CTD_ANON_10, documentation=u'provides links between processes or between data sources and processes')
Namespace.addCategoryObject('elementBinding', connections.name().localName(), connections)

components = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'components'), CTD_ANON_34, documentation=u'Collection of subprocesses that can be chained using connections')
Namespace.addCategoryObject('elementBinding', components.name().localName(), components)

contactInfo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'contactInfo'), CTD_ANON_27)
Namespace.addCategoryObject('elementBinding', contactInfo.name().localName(), contactInfo)

Component = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Component'), ComponentType, documentation=u'Atomic SensorML Component')
Namespace.addCategoryObject('elementBinding', Component.name().localName(), Component)

SensorML = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SensorML'), CTD_ANON_54, documentation=u'SensorML document root')
Namespace.addCategoryObject('elementBinding', SensorML.name().localName(), SensorML)

ArrayLink = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ArrayLink'), CTD_ANON_17, documentation=u'Special Link to handle accessing array elements sequentially')
Namespace.addCategoryObject('elementBinding', ArrayLink.name().localName(), ArrayLink)

ResponsibleParty = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResponsibleParty'), CTD_ANON_42, documentation=u'based on ISO 19115')
Namespace.addCategoryObject('elementBinding', ResponsibleParty.name().localName(), ResponsibleParty)

history = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'history'), CTD_ANON_26, documentation=u'History of the object described (Recalibration, adjustments, etc...)')
Namespace.addCategoryObject('elementBinding', history.name().localName(), history)

identification = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'identification'), CTD_ANON_8, documentation=u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary')
Namespace.addCategoryObject('elementBinding', identification.name().localName(), identification)

securityConstraint = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'), CTD_ANON_4, documentation=u'Means of providing security constraints of description')
Namespace.addCategoryObject('elementBinding', securityConstraint.name().localName(), securityConstraint)

schematron = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'schematron'), CTD_ANON_56, documentation=u'Includes or references a schematron doc for enforcing process constraints')
Namespace.addCategoryObject('elementBinding', schematron.name().localName(), schematron)

EventList = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EventList'), CTD_ANON_58, documentation=u'List of events related to the enclosing object')
Namespace.addCategoryObject('elementBinding', EventList.name().localName(), EventList)

parameters = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'parameters'), CTD_ANON_12, documentation=u'list of parameters')
Namespace.addCategoryObject('elementBinding', parameters.name().localName(), parameters)

InterfaceDefinition = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InterfaceDefinition'), CTD_ANON_25, documentation=u'Interface definition based on the OSI model. (http://en.wikipedia.org/wiki/OSI_model)')
Namespace.addCategoryObject('elementBinding', InterfaceDefinition.name().localName(), InterfaceDefinition)

ComponentArray = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ComponentArray'), ComponentArrayType, documentation=u'Special Type of system used to describe large arrays of almost identical components. An indexing mechanism can be used to vary certain parameters according to one or more indices value')
Namespace.addCategoryObject('elementBinding', ComponentArray.name().localName(), ComponentArray)

ProcessChain = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProcessChain'), ProcessChainType, documentation=u'Process formed by chaining sub-processes')
Namespace.addCategoryObject('elementBinding', ProcessChain.name().localName(), ProcessChain)

capabilities = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'capabilities'), CTD_ANON_11, documentation=u'Capability list for quick discovery')
Namespace.addCategoryObject('elementBinding', capabilities.name().localName(), capabilities)

temporalReferenceFrame = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'), CTD_ANON_46, documentation=u'Textual definition of a temporal frame (time origin). Temporal frames can be related to one another by specifying relative times.')
Namespace.addCategoryObject('elementBinding', temporalReferenceFrame.name().localName(), temporalReferenceFrame)

inputs = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'inputs'), CTD_ANON_61, documentation=u'list of input signals')
Namespace.addCategoryObject('elementBinding', inputs.name().localName(), inputs)

method = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'method'), methodPropertyType, documentation=u'process method')
Namespace.addCategoryObject('elementBinding', method.name().localName(), method)

interfaces = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interfaces'), CTD_ANON_39, documentation=u'List of interfaces useable to access System inputs and outputs')
Namespace.addCategoryObject('elementBinding', interfaces.name().localName(), interfaces)

System = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'System'), SystemType, documentation=u'System is a composite component containing sub-components.')
Namespace.addCategoryObject('elementBinding', System.name().localName(), System)

position = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'position'), CTD_ANON_55, documentation=u'Full position (location + orientation) given by a swe:Position or a Process (if variable)')
Namespace.addCategoryObject('elementBinding', position.name().localName(), position)

ContactList = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ContactList'), CTD_ANON_47, documentation=u'Allows to group several contacts together in a list that can be referenced as a whole')
Namespace.addCategoryObject('elementBinding', ContactList.name().localName(), ContactList)

Person = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Person'), CTD_ANON_30, documentation=u'based on IC:DMMS')
Namespace.addCategoryObject('elementBinding', Person.name().localName(), Person)

onlineResource = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'), CTD_ANON_44)
Namespace.addCategoryObject('elementBinding', onlineResource.name().localName(), onlineResource)

legalConstraint = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'), CTD_ANON_48, documentation=u'Means of providing legal constraints of description')
Namespace.addCategoryObject('elementBinding', legalConstraint.name().localName(), legalConstraint)

documentation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), CTD_ANON_1, documentation=u'Relevant documentation for that object')
Namespace.addCategoryObject('elementBinding', documentation.name().localName(), documentation)

Rights = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Rights'), CTD_ANON_65, documentation=u'based on IC:DDMS definition')
Namespace.addCategoryObject('elementBinding', Rights.name().localName(), Rights)

ProcessMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProcessMethod'), ProcessMethodType, documentation=u'Method describing a process (Can also be a dictionary entry)')
Namespace.addCategoryObject('elementBinding', ProcessMethod.name().localName(), ProcessMethod)

interface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interface'), CTD_ANON_28)
Namespace.addCategoryObject('elementBinding', interface.name().localName(), interface)

Link = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Link'), CTD_ANON_70, documentation=u'Link object used to make connections between processes')
Namespace.addCategoryObject('elementBinding', Link.name().localName(), Link)

keywords = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'keywords'), CTD_ANON_21, documentation=u'Means of providing a list of keywords (with a codeSpace) for quick discovery')
Namespace.addCategoryObject('elementBinding', keywords.name().localName(), keywords)

characteristics = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'characteristics'), CTD_ANON_19, documentation=u'Characteristic list for quick discovery')
Namespace.addCategoryObject('elementBinding', characteristics.name().localName(), characteristics)

DataSource = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DataSource'), DataSourceType, documentation=u'Process with no inputs representing a source of data (Tables, Observations...) for other processes to connect to.')
Namespace.addCategoryObject('elementBinding', DataSource.name().localName(), DataSource)

validTime = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'validTime'), CTD_ANON_14, documentation=u'Means of providing time validity constraint of description')
Namespace.addCategoryObject('elementBinding', validTime.name().localName(), validTime)

timePosition = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'timePosition'), CTD_ANON_68, documentation=u'Provide the ability to relate  a local time frame to a reference time frame')
Namespace.addCategoryObject('elementBinding', timePosition.name().localName(), timePosition)

positions = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'positions'), CTD_ANON_71, documentation=u'Relative positions of the System components')
Namespace.addCategoryObject('elementBinding', positions.name().localName(), positions)

relaxNG = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'relaxNG'), CTD_ANON_81, documentation=u'Includes or references a relaxNG doc for enforcing process constraints')
Namespace.addCategoryObject('elementBinding', relaxNG.name().localName(), relaxNG)



CTD_ANON_1._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Document'), CTD_ANON_31, scope=CTD_ANON_1, documentation=u'Document record with date/time, version, author, etc. pointing to an online resource related to the enclosing object'))

CTD_ANON_1._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DocumentList'), CTD_ANON_24, scope=CTD_ANON_1, documentation=u'List of documents related to the enclosing object'))
CTD_ANON_1._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_1._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Document'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_1._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DocumentList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Person'), CTD_ANON_30, scope=CTD_ANON_3, documentation=u'based on IC:DMMS'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResponsibleParty'), CTD_ANON_42, scope=CTD_ANON_3, documentation=u'based on ISO 19115'))
CTD_ANON_3._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Person'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ResponsibleParty'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Security'), CTD_ANON_33, scope=CTD_ANON_4, documentation=u'based on IC:ISM definition'))
CTD_ANON_4._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Security'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Event'), CTD_ANON_38, scope=CTD_ANON_5, documentation=u'Event record (change to the object) including a date/time, description, identification and additional references and metadata'))
CTD_ANON_5._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Event'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


AbstractSMLType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractSMLType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractSMLType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractSMLType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractSMLType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractSMLType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractSMLType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
    ])
})



AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'history'), CTD_ANON_26, scope=AbstractProcessType, documentation=u'History of the object described (Recalibration, adjustments, etc...)'))

AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'contact'), CTD_ANON_13, scope=AbstractProcessType, documentation=u'Relevant contacts for that object'))

AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'classification'), CTD_ANON_7, scope=AbstractProcessType, documentation=u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary'))

AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'keywords'), CTD_ANON_21, scope=AbstractProcessType, documentation=u'Means of providing a list of keywords (with a codeSpace) for quick discovery'))

AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'), CTD_ANON_48, scope=AbstractProcessType, documentation=u'Means of providing legal constraints of description'))

AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'identification'), CTD_ANON_8, scope=AbstractProcessType, documentation=u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary'))

AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'characteristics'), CTD_ANON_19, scope=AbstractProcessType, documentation=u'Characteristic list for quick discovery'))

AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'), CTD_ANON_4, scope=AbstractProcessType, documentation=u'Means of providing security constraints of description'))

AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), CTD_ANON_1, scope=AbstractProcessType, documentation=u'Relevant documentation for that object'))

AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'capabilities'), CTD_ANON_11, scope=AbstractProcessType, documentation=u'Capability list for quick discovery'))

AbstractProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'validTime'), CTD_ANON_14, scope=AbstractProcessType, documentation=u'Means of providing time validity constraint of description'))
AbstractProcessType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
})


AbstractRestrictedProcessType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractRestrictedProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
})



AbstractPureProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'inputs'), CTD_ANON_61, scope=AbstractPureProcessType, documentation=u'list of input signals'))

AbstractPureProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outputs'), CTD_ANON_6, scope=AbstractPureProcessType, documentation=u'list of output signals'))

AbstractPureProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'parameters'), CTD_ANON_12, scope=AbstractPureProcessType, documentation=u'list of parameters'))
AbstractPureProcessType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractPureProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
})



ProcessModelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'method'), methodPropertyType, scope=ProcessModelType, documentation=u'process method'))
ProcessModelType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
})



CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OutputList'), CTD_ANON_15, scope=CTD_ANON_6))
CTD_ANON_6._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OutputList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_7._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ClassifierList'), CTD_ANON_69, scope=CTD_ANON_7))
CTD_ANON_7._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ClassifierList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IdentifierList'), CTD_ANON_79, scope=CTD_ANON_8))
CTD_ANON_8._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IdentifierList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProcessChain'), ProcessChainType, scope=CTD_ANON_9, documentation=u'Process formed by chaining sub-processes'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ImplementationCode'), CTD_ANON_49, scope=CTD_ANON_9))
CTD_ANON_9._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ProcessChain'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ImplementationCode'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ConnectionList'), CTD_ANON_41, scope=CTD_ANON_10))
CTD_ANON_10._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ConnectionList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'), pyxb.bundles.opengis.swe_1_0_1.AbstractDataRecordType, abstract=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_11))
CTD_ANON_11._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ParameterList'), CTD_ANON_83, scope=CTD_ANON_12))
CTD_ANON_12._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ParameterList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_13._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Person'), CTD_ANON_30, scope=CTD_ANON_13, documentation=u'based on IC:DMMS'))

CTD_ANON_13._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResponsibleParty'), CTD_ANON_42, scope=CTD_ANON_13, documentation=u'based on ISO 19115'))

CTD_ANON_13._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ContactList'), CTD_ANON_47, scope=CTD_ANON_13, documentation=u'Allows to group several contacts together in a list that can be referenced as a whole'))
CTD_ANON_13._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_13._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Person'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_13._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ContactList'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_13._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ResponsibleParty'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TimeInstant'), pyxb.bundles.opengis.gml.TimeInstantType, scope=CTD_ANON_14))

CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TimePeriod'), pyxb.bundles.opengis.gml.TimePeriodType, scope=CTD_ANON_14))
CTD_ANON_14._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TimeInstant'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TimePeriod'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'output'), IoComponentPropertyType, scope=CTD_ANON_15))
CTD_ANON_15._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output'))),
    ])
})



CTD_ANON_16._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'EngineeringCRS'), pyxb.bundles.opengis.gml.EngineeringCRSType, scope=CTD_ANON_16))
CTD_ANON_16._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_16._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'EngineeringCRS'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'connection'), CTD_ANON_37, scope=CTD_ANON_17, documentation=u'Specify a connection between two elements'))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'destinationIndex'), CTD_ANON_60, scope=CTD_ANON_17))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sourceArray'), CTD_ANON_29, scope=CTD_ANON_17))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'destinationArray'), CTD_ANON_2, scope=CTD_ANON_17))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sourceIndex'), CTD_ANON_74, scope=CTD_ANON_17))
CTD_ANON_17._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'destinationArray'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sourceArray'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connection'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sourceIndex'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connection'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connection'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'destinationIndex'))),
    ])
})



CTD_ANON_18._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Count'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_7, scope=CTD_ANON_18, documentation=u'Integer number used for a counting value'))
CTD_ANON_18._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_18._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Count'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_19._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'), pyxb.bundles.opengis.swe_1_0_1.AbstractDataRecordType, abstract=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_19))
CTD_ANON_19._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_19._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_20._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'value'), pyxb.binding.datatypes.token, scope=CTD_ANON_20))

CTD_ANON_20._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'codeSpace'), pyxb.bundles.opengis.swe_1_0_1.CodeSpacePropertyType, scope=CTD_ANON_20))
CTD_ANON_20._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_20._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'codeSpace'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_20._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'value'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_20._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'value'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



CTD_ANON_21._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeywordList'), CTD_ANON_51, scope=CTD_ANON_21))
CTD_ANON_21._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_21._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeywordList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_22._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'Point'), pyxb.bundles.opengis.gml.PointType, scope=CTD_ANON_22))

CTD_ANON_22._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Curve'), pyxb.bundles.opengis.gml.AbstractCurveType, abstract=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_22, documentation=u'The "_Curve" element is the abstract head of the substituition group for all (continuous) curve elements.'))
CTD_ANON_22._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_22._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'Point'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_22._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Curve'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'facsimile'), pyxb.binding.datatypes.string, scope=CTD_ANON_23))

CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'voice'), pyxb.binding.datatypes.string, scope=CTD_ANON_23))
CTD_ANON_23._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'voice'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'facsimile'))),
    ])
})



CTD_ANON_24._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'member'), CTD_ANON_52, scope=CTD_ANON_24))

CTD_ANON_24._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), pyxb.bundles.opengis.gml.StringOrRefType, scope=CTD_ANON_24, documentation=u'Contains a simple text description of the object, or refers to an external description.'))
CTD_ANON_24._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_24._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_24._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_24._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_24._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
})



CTD_ANON_25._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'dataLinkLayer'), LayerPropertyType, scope=CTD_ANON_25, documentation=u'Layer 2 of the OSI model. Provides functional and procedural means of transfering data between network entities and detecting/correcting errors. (Ex: Ethernet, 802.11, Token ring, ATM, Fibre Channel)'))

CTD_ANON_25._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'networkLayer'), LayerPropertyType, scope=CTD_ANON_25, documentation=u'Layer 3 of the OSI model. Provides functional and procedural means of transfering data from source to destination via one or more networks while insuring QoS. (Ex: IP, ICMP, ARP, IPSec, IPX)'))

CTD_ANON_25._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'applicationLayer'), LayerPropertyType, scope=CTD_ANON_25, documentation=u'Layer 7 of the OSI model. Provides a means for the user to access information on the network through an application. (Ex: HTTP, SMTP, FTP, XMPP, Telnet, NTP, RTP, NFS)'))

CTD_ANON_25._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'serviceLayer'), LayerPropertyType, scope=CTD_ANON_25, documentation=u'Layer 8 (not in OSI). Type of web service used to access the data. (Ex: SOS, WCS, WFS)'))

CTD_ANON_25._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'presentationLayer'), PresentationLayerPropertyType, scope=CTD_ANON_25, documentation=u'Layer 6 of the OSI model. Transforms the data to provide a standard interface for the Application layer. (Ex: SSL, TLS, ASCII, MIDI, MPEG, SWECommon)'))

CTD_ANON_25._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'physicalLayer'), LayerPropertyType, scope=CTD_ANON_25, documentation=u'Layer 1 of the OSI model. Provides all electrical and physical characteristics of the connection including pin layouts, voltages, cables specifcations, etc... (Ex: RS232, 100BASE-T, DSL, 802.11g)'))

CTD_ANON_25._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'), LayerPropertyType, scope=CTD_ANON_25, documentation=u'Layer 0 (not is OSI). Type of connector used. (Ex: DB9, DB25, RJ45, RJ11, MINIDIN-8, USB-A, USB-B)'))

CTD_ANON_25._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sessionLayer'), LayerPropertyType, scope=CTD_ANON_25, documentation=u'Layer 5 of the OSI model. Controls the dialogues (sessions) between computers by establishing, managing and terminating connections between the local and remote application. (Ex: NetBios, TCP session establishment)'))

CTD_ANON_25._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'transportLayer'), LayerPropertyType, scope=CTD_ANON_25, documentation=u'Layer 4 of the OSI model. Provides transparent transfer of data between end users and can control reliability of a given link. (Ex: TCP, UDP, SPX)'))
CTD_ANON_25._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'serviceLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'applicationLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataLinkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'networkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'presentationLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'physicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sessionLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'transportLayer'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'networkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataLinkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'presentationLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'physicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sessionLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'transportLayer'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataLinkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'physicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'networkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataLinkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'physicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'transportLayer'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'physicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'networkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataLinkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'physicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataLinkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'applicationLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'networkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'presentationLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'physicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sessionLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'transportLayer'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'networkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataLinkLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'physicalLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sessionLayer'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'transportLayer'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_25._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mechanicalLayer'))),
    ])
})



CTD_ANON_26._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EventList'), CTD_ANON_58, scope=CTD_ANON_26, documentation=u'List of events related to the enclosing object'))
CTD_ANON_26._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_26._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EventList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_27._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'contactInstructions'), pyxb.binding.datatypes.string, scope=CTD_ANON_27))

CTD_ANON_27._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'phone'), CTD_ANON_23, scope=CTD_ANON_27))

CTD_ANON_27._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), CTD_ANON_77, scope=CTD_ANON_27))

CTD_ANON_27._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'), CTD_ANON_44, scope=CTD_ANON_27))

CTD_ANON_27._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'hoursOfService'), pyxb.binding.datatypes.string, scope=CTD_ANON_27))
CTD_ANON_27._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phone'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'hoursOfService'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contactInstructions'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'hoursOfService'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contactInstructions'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contactInstructions'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'hoursOfService'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_27._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contactInstructions'))),
    ])
})



CTD_ANON_28._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InterfaceDefinition'), CTD_ANON_25, scope=CTD_ANON_28, documentation=u'Interface definition based on the OSI model. (http://en.wikipedia.org/wiki/OSI_model)'))
CTD_ANON_28._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_28._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'InterfaceDefinition'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_30._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'userID'), pyxb.binding.datatypes.token, scope=CTD_ANON_30))

CTD_ANON_30._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'surname'), pyxb.binding.datatypes.token, scope=CTD_ANON_30))

CTD_ANON_30._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'name'), pyxb.binding.datatypes.token, scope=CTD_ANON_30))

CTD_ANON_30._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'affiliation'), pyxb.binding.datatypes.token, scope=CTD_ANON_30))

CTD_ANON_30._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber'), pyxb.binding.datatypes.token, scope=CTD_ANON_30))

CTD_ANON_30._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'email'), pyxb.binding.datatypes.token, scope=CTD_ANON_30))
CTD_ANON_30._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_30._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surname'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_30._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_30._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'userID'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_30._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'affiliation'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_30._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_30._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'email'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
    ])
})


AbstractListType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})



LayerPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'), pyxb.bundles.opengis.swe_1_0_1.AbstractDataRecordType, abstract=pyxb.binding.datatypes.boolean(1), scope=LayerPropertyType))

LayerPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Category'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_5, scope=LayerPropertyType, documentation=u'A simple token identifying a term or category (single spaces allowed); definition attribute should provide dictionary entry useful for interpretation of the value'))
LayerPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LayerPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=LayerPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Category'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_31._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'), CTD_ANON_44, scope=CTD_ANON_31))

CTD_ANON_31._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), pyxb.bundles.opengis.gml.StringOrRefType, scope=CTD_ANON_31, documentation=u'Contains a simple text description of the object, or refers to an external description.'))

CTD_ANON_31._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'format'), pyxb.binding.datatypes.token, scope=CTD_ANON_31, documentation=u'Specifies the fornat of the file pointed to by onlineResource'))

CTD_ANON_31._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'date'), pyxb.bundles.opengis.swe_1_0_1.timeIso8601, scope=CTD_ANON_31, documentation=u'Date of creation'))

CTD_ANON_31._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'contact'), CTD_ANON_13, scope=CTD_ANON_31, documentation=u'Relevant contacts for that object'))
CTD_ANON_31._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'date'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'format'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'format'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onlineResource'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_31._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'format'))),
    ])
})



CTD_ANON_32._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AlgorithmDefinition'), CTD_ANON_67, scope=CTD_ANON_32))
CTD_ANON_32._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_32._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AlgorithmDefinition'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_34._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ComponentList'), CTD_ANON_43, scope=CTD_ANON_34))
CTD_ANON_34._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_34._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ComponentList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_37._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Link'), CTD_ANON_70, scope=CTD_ANON_37, documentation=u'Link object used to make connections between processes'))

CTD_ANON_37._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ArrayLink'), CTD_ANON_17, scope=CTD_ANON_37, documentation=u'Special Link to handle accessing array elements sequentially'))
CTD_ANON_37._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_37._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Link'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_37._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ArrayLink'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_38._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'date'), pyxb.bundles.opengis.swe_1_0_1.timeIso8601, scope=CTD_ANON_38, documentation=u'Date/Time of event'))

CTD_ANON_38._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'keywords'), CTD_ANON_21, scope=CTD_ANON_38, documentation=u'Means of providing a list of keywords (with a codeSpace) for quick discovery'))

CTD_ANON_38._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'contact'), CTD_ANON_13, scope=CTD_ANON_38, documentation=u'Relevant contacts for that object'))

CTD_ANON_38._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'identification'), CTD_ANON_8, scope=CTD_ANON_38, documentation=u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary'))

CTD_ANON_38._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), CTD_ANON_1, scope=CTD_ANON_38, documentation=u'Relevant documentation for that object'))

CTD_ANON_38._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'classification'), CTD_ANON_7, scope=CTD_ANON_38, documentation=u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary'))

CTD_ANON_38._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), pyxb.bundles.opengis.gml.StringOrRefType, scope=CTD_ANON_38, documentation=u'Contains a simple text description of the object, or refers to an external description.'))

CTD_ANON_38._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'property'), pyxb.bundles.opengis.swe_1_0_1.DataComponentPropertyType, scope=CTD_ANON_38))
CTD_ANON_38._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'date'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'property'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'property'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'property'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'property'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_38._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'property'))),
    ])
})



CTD_ANON_39._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InterfaceList'), CTD_ANON_62, scope=CTD_ANON_39))
CTD_ANON_39._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_39._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'InterfaceList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


CTD_ANON_40._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_41._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'connection'), CTD_ANON_37, scope=CTD_ANON_41, documentation=u'Specify a connection between two elements'))
CTD_ANON_41._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_41._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connection'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_41._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connection'))),
    ])
})



CTD_ANON_42._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'contactInfo'), CTD_ANON_27, scope=CTD_ANON_42))

CTD_ANON_42._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'individualName'), pyxb.binding.datatypes.string, scope=CTD_ANON_42))

CTD_ANON_42._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'positionName'), pyxb.binding.datatypes.string, scope=CTD_ANON_42))

CTD_ANON_42._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'organizationName'), pyxb.binding.datatypes.string, scope=CTD_ANON_42))
CTD_ANON_42._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_42._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'individualName'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_42._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionName'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_42._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'organizationName'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_42._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contactInfo'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_42._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionName'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_42._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'organizationName'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_42._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contactInfo'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_42._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contactInfo'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_42._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positionName'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_42._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contactInfo'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
    ])
})



CTD_ANON_43._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'component'), CTD_ANON_64, scope=CTD_ANON_43))
CTD_ANON_43._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_43._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'component'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_43._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'component'))),
    ])
})



CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'input'), IoComponentPropertyType, scope=CTD_ANON_45))
CTD_ANON_45._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input'))),
    ])
})



methodPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProcessMethod'), ProcessMethodType, scope=methodPropertyType, documentation=u'Method describing a process (Can also be a dictionary entry)'))
methodPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=methodPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ProcessMethod'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_46._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TemporalCRS'), pyxb.bundles.opengis.gml.TemporalCRSType, scope=CTD_ANON_46))
CTD_ANON_46._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_46._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TemporalCRS'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_47._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'member'), CTD_ANON_3, scope=CTD_ANON_47))

CTD_ANON_47._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), pyxb.bundles.opengis.gml.StringOrRefType, scope=CTD_ANON_47, documentation=u'Contains a simple text description of the object, or refers to an external description.'))
CTD_ANON_47._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_47._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_47._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_47._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_47._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
})



CTD_ANON_48._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Rights'), CTD_ANON_65, scope=CTD_ANON_48, documentation=u'based on IC:DDMS definition'))
CTD_ANON_48._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_48._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Rights'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'binaryRef'), CTD_ANON_53, scope=CTD_ANON_49))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'classification'), CTD_ANON_7, scope=CTD_ANON_49, documentation=u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), pyxb.bundles.opengis.gml.StringOrRefType, scope=CTD_ANON_49, documentation=u'Contains a simple text description of the object, or refers to an external description.'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'capabilities'), CTD_ANON_11, scope=CTD_ANON_49, documentation=u'Capability list for quick discovery'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'validTime'), CTD_ANON_14, scope=CTD_ANON_49, documentation=u'Means of providing time validity constraint of description'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'characteristics'), CTD_ANON_19, scope=CTD_ANON_49, documentation=u'Characteristic list for quick discovery'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'), CTD_ANON_4, scope=CTD_ANON_49, documentation=u'Means of providing security constraints of description'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'contact'), CTD_ANON_13, scope=CTD_ANON_49, documentation=u'Relevant contacts for that object'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'history'), CTD_ANON_26, scope=CTD_ANON_49, documentation=u'History of the object described (Recalibration, adjustments, etc...)'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sourceRef'), CTD_ANON_36, scope=CTD_ANON_49))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'), CTD_ANON_48, scope=CTD_ANON_49, documentation=u'Means of providing legal constraints of description'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), CTD_ANON_1, scope=CTD_ANON_49, documentation=u'Relevant documentation for that object'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'identification'), CTD_ANON_8, scope=CTD_ANON_49, documentation=u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary'))

CTD_ANON_49._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'keywords'), CTD_ANON_21, scope=CTD_ANON_49, documentation=u'Means of providing a list of keywords (with a codeSpace) for quick discovery'))
CTD_ANON_49._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binaryRef'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sourceRef'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binaryRef'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sourceRef'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binaryRef'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sourceRef'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binaryRef'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sourceRef'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binaryRef'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sourceRef'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binaryRef'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sourceRef'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binaryRef'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binaryRef'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=CTD_ANON_49._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sourceRef'))),
    ])
})



connectionsPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ConnectionList'), AbstractListType, scope=connectionsPropertyType))
connectionsPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=connectionsPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ConnectionList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_50._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Term'), CTD_ANON_20, scope=CTD_ANON_50, documentation=u'A well defined token used to specify identifier and classifier values (single spaces allowed)'))
CTD_ANON_50._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_50._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Term'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



dataSourcesPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DataSourceList'), AbstractListType, scope=dataSourcesPropertyType))
dataSourcesPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=dataSourcesPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DataSourceList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



AbstractDerivableComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'location'), CTD_ANON_22, scope=AbstractDerivableComponentType, documentation=u'Uses a gml:Point for a fixed location or a (time dependant) curve for time variable location'))

AbstractDerivableComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'position'), CTD_ANON_55, scope=AbstractDerivableComponentType, documentation=u'Full position (location + orientation) given by a swe:Position or a Process (if variable)'))

AbstractDerivableComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'timePosition'), CTD_ANON_68, scope=AbstractDerivableComponentType, documentation=u'Provide the ability to relate  a local time frame to a reference time frame'))

AbstractDerivableComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'), CTD_ANON_16, scope=AbstractDerivableComponentType, documentation=u'Textual definition of a spatial frame axes (origin, orientation). Spatial frames can be related to one another by specifying relative positions.'))

AbstractDerivableComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interfaces'), CTD_ANON_39, scope=AbstractDerivableComponentType, documentation=u'List of interfaces useable to access System inputs and outputs'))

AbstractDerivableComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'), CTD_ANON_46, scope=AbstractDerivableComponentType, documentation=u'Textual definition of a temporal frame (time origin). Temporal frames can be related to one another by specifying relative times.'))
AbstractDerivableComponentType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
    ])
})



AbstractComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'inputs'), CTD_ANON_61, scope=AbstractComponentType, documentation=u'list of input signals'))

AbstractComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outputs'), CTD_ANON_6, scope=AbstractComponentType, documentation=u'list of output signals'))

AbstractComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'parameters'), CTD_ANON_12, scope=AbstractComponentType, documentation=u'list of parameters'))
AbstractComponentType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 16 : pyxb.binding.content.ContentModelState(state=16, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=AbstractComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 17 : pyxb.binding.content.ContentModelState(state=17, is_final=True, transitions=[
    ])
})



ComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'method'), methodPropertyType, scope=ComponentType, documentation=u'process method'))
ComponentType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 16 : pyxb.binding.content.ContentModelState(state=16, is_final=True, transitions=[
    ])
    , 17 : pyxb.binding.content.ContentModelState(state=17, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 18 : pyxb.binding.content.ContentModelState(state=18, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
})



CTD_ANON_51._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'keyword'), pyxb.binding.datatypes.token, scope=CTD_ANON_51))
CTD_ANON_51._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_51._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keyword'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_51._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keyword'))),
    ])
})



CTD_ANON_52._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Document'), CTD_ANON_31, scope=CTD_ANON_52, documentation=u'Document record with date/time, version, author, etc. pointing to an online resource related to the enclosing object'))
CTD_ANON_52._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_52._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Document'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'capabilities'), CTD_ANON_11, scope=CTD_ANON_54, documentation=u'Capability list for quick discovery'))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'validTime'), CTD_ANON_14, scope=CTD_ANON_54, documentation=u'Means of providing time validity constraint of description'))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'characteristics'), CTD_ANON_19, scope=CTD_ANON_54, documentation=u'Characteristic list for quick discovery'))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'keywords'), CTD_ANON_21, scope=CTD_ANON_54, documentation=u'Means of providing a list of keywords (with a codeSpace) for quick discovery'))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'), CTD_ANON_4, scope=CTD_ANON_54, documentation=u'Means of providing security constraints of description'))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'contact'), CTD_ANON_13, scope=CTD_ANON_54, documentation=u'Relevant contacts for that object'))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'member'), CTD_ANON_72, scope=CTD_ANON_54))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'), CTD_ANON_48, scope=CTD_ANON_54, documentation=u'Means of providing legal constraints of description'))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), CTD_ANON_1, scope=CTD_ANON_54, documentation=u'Relevant documentation for that object'))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'identification'), CTD_ANON_8, scope=CTD_ANON_54, documentation=u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary'))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'classification'), CTD_ANON_7, scope=CTD_ANON_54, documentation=u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary'))

CTD_ANON_54._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'history'), CTD_ANON_26, scope=CTD_ANON_54, documentation=u'History of the object described (Recalibration, adjustments, etc...)'))
CTD_ANON_54._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=CTD_ANON_54._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
})



CTD_ANON_55._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Process'), AbstractProcessType, abstract=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_55, documentation=u'base substitution group for all processes'))

CTD_ANON_55._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Position'), pyxb.bundles.opengis.swe_1_0_1.PositionType, scope=CTD_ANON_55, documentation=u'Position is given as a group of Vectors/Matrices, each of which can specify location, orientation, velocity, angularVelocity, acceleration or angularAcceleration or a combination of those in a composite state Vector. Each Vector can have a separate frame of reference or inherit the frame from the parent Position object.'))

CTD_ANON_55._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Vector'), pyxb.bundles.opengis.swe_1_0_1.VectorType, scope=CTD_ANON_55, documentation=u'A Vector is a special type of DataRecord that takes a list of numerical scalars called coordinates. The Vector has a referenceFrame in which the coordinates are expressed'))
CTD_ANON_55._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_55._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_Process'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_55._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Position'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_55._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Vector'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



outputsPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OutputList'), AbstractListType, scope=outputsPropertyType))
outputsPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=outputsPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OutputList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'QuantityRange'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_8, scope=IoComponentPropertyType, documentation=u'Decimal pair for specifying a quantity range with constraints'))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Quantity'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_1, scope=IoComponentPropertyType, documentation=u'Decimal number with optional unit and constraints'))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Time'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_15, scope=IoComponentPropertyType, documentation=u'Either ISO 8601 (e.g. 2004-04-18T12:03:04.6Z) or time relative to a time origin'))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'CountRange'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_2, scope=IoComponentPropertyType, documentation=u'Integer pair used for specifying a count range'))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataArray'), pyxb.bundles.opengis.swe_1_0_1.AbstractDataArrayType, abstract=pyxb.binding.datatypes.boolean(1), scope=IoComponentPropertyType, documentation=u'Implemetation of ISO-11404 Array datatype. This defines an array of identical data components with a elementCount. Values are given as a block and can be encoded in different ways'))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Boolean'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_9, scope=IoComponentPropertyType, documentation=u'Scalar component used to express truth: True or False, 0 or 1'))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'TimeRange'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_6, scope=IoComponentPropertyType, documentation=u'Time value pair for specifying a time range (can be a decimal or ISO 8601)'))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Count'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_7, scope=IoComponentPropertyType, documentation=u'Integer number used for a counting value'))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Category'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_5, scope=IoComponentPropertyType, documentation=u'A simple token identifying a term or category (single spaces allowed); definition attribute should provide dictionary entry useful for interpretation of the value'))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'), pyxb.bundles.opengis.swe_1_0_1.AbstractDataRecordType, abstract=pyxb.binding.datatypes.boolean(1), scope=IoComponentPropertyType))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Text'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_11, scope=IoComponentPropertyType, documentation=u'Free textual component'))

IoComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'ObservableProperty'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_14, scope=IoComponentPropertyType, documentation=u'ObservableProperty should be used to identify (through reference only) stimuli or measurable property types. The consequence is that it does not have a uom because it has not been measured yet.  This is used to define sensor/detector/actuator inputs and outputs, for instance.'))
IoComponentPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'QuantityRange'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'CountRange'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Boolean'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'TimeRange'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Text'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Time'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Category'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataArray'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Count'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'ObservableProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=IoComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Quantity'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


CTD_ANON_56._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=set(u'http://www.ascc.net/xml/schematron'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_57._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataBlockDefinition'), pyxb.bundles.opengis.swe_1_0_1.DataBlockDefinitionType, scope=CTD_ANON_57))

CTD_ANON_57._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataStreamDefinition'), pyxb.bundles.opengis.swe_1_0_1.DataStreamDefinitionType, scope=CTD_ANON_57))
CTD_ANON_57._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_57._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataBlockDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_57._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataStreamDefinition'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_58._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'member'), CTD_ANON_5, scope=CTD_ANON_58))
CTD_ANON_58._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_58._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_58._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'member'))),
    ])
})



ProcessChainType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'components'), CTD_ANON_34, scope=ProcessChainType, documentation=u'Collection of subprocesses that can be chained using connections'))

ProcessChainType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'connections'), CTD_ANON_10, scope=ProcessChainType, documentation=u'provides links between processes or between data sources and processes'))
ProcessChainType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ProcessChainType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
})



CTD_ANON_59._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'position'), CTD_ANON_55, scope=CTD_ANON_59, documentation=u'Full position (location + orientation) given by a swe:Position or a Process (if variable)'))

CTD_ANON_59._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'timePosition'), CTD_ANON_68, scope=CTD_ANON_59, documentation=u'Provide the ability to relate  a local time frame to a reference time frame'))
CTD_ANON_59._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_59._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_59._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_59._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



ComponentArrayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'inputs'), CTD_ANON_61, scope=ComponentArrayType, documentation=u'list of input signals'))

ComponentArrayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outputs'), CTD_ANON_6, scope=ComponentArrayType, documentation=u'list of output signals'))

ComponentArrayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'connections'), CTD_ANON_10, scope=ComponentArrayType, documentation=u'provides links between processes or between data sources and processes'))

ComponentArrayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'components'), CTD_ANON_34, scope=ComponentArrayType, documentation=u'Collection of subprocesses that can be chained using connections'))

ComponentArrayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'positions'), CTD_ANON_71, scope=ComponentArrayType, documentation=u'Relative positions of the System components'))

ComponentArrayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'parameters'), CTD_ANON_75, scope=ComponentArrayType))
ComponentArrayType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
    ])
    , 16 : pyxb.binding.content.ContentModelState(state=16, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
    ])
    , 17 : pyxb.binding.content.ContentModelState(state=17, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 18 : pyxb.binding.content.ContentModelState(state=18, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
    ])
    , 19 : pyxb.binding.content.ContentModelState(state=19, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
    ])
    , 20 : pyxb.binding.content.ContentModelState(state=20, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=ComponentArrayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
})



AbstractDerivableProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outputs'), outputsPropertyType, scope=AbstractDerivableProcessType))

AbstractDerivableProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'method'), methodPropertyType, scope=AbstractDerivableProcessType, documentation=u'process method'))

AbstractDerivableProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'inputs'), inputsPropertyType, scope=AbstractDerivableProcessType))

AbstractDerivableProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'dataSources'), dataSourcesPropertyType, scope=AbstractDerivableProcessType))

AbstractDerivableProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'parameters'), parametersPropertyType, scope=AbstractDerivableProcessType))

AbstractDerivableProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'connections'), connectionsPropertyType, scope=AbstractDerivableProcessType))

AbstractDerivableProcessType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'components'), componentsPropertyType, scope=AbstractDerivableProcessType))
AbstractDerivableProcessType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataSources'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'method'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=AbstractDerivableProcessType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
})



parametersPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ParameterList'), AbstractListType, scope=parametersPropertyType))
parametersPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=parametersPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ParameterList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_61._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InputList'), CTD_ANON_45, scope=CTD_ANON_61))
CTD_ANON_61._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_61._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'InputList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_62._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interface'), CTD_ANON_28, scope=CTD_ANON_62))
CTD_ANON_62._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_62._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interface'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_62._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interface'))),
    ])
})



CTD_ANON_64._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Process'), AbstractProcessType, abstract=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_64, documentation=u'base substitution group for all processes'))
CTD_ANON_64._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_64._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_Process'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_65._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), CTD_ANON_1, scope=CTD_ANON_65, documentation=u'Relevant documentation for that object'))
CTD_ANON_65._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_65._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_66._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'parameter'), pyxb.bundles.opengis.swe_1_0_1.DataComponentPropertyType, scope=CTD_ANON_66))

CTD_ANON_66._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'index'), CTD_ANON_18, scope=CTD_ANON_66))
CTD_ANON_66._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_66._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'index'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_66._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'index'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_66._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameter'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_66._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameter'))),
    ])
})



ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), CTD_ANON_1, scope=ProcessMethodType, documentation=u'Relevant documentation for that object'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'history'), CTD_ANON_26, scope=ProcessMethodType, documentation=u'History of the object described (Recalibration, adjustments, etc...)'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'identification'), CTD_ANON_8, scope=ProcessMethodType, documentation=u'Means of providing various identity and alias values, with types such as "longName", "abbreviation", "modelNumber", "serialNumber", whose terms can be defined in a dictionary'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'validTime'), CTD_ANON_14, scope=ProcessMethodType, documentation=u'Means of providing time validity constraint of description'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'characteristics'), CTD_ANON_19, scope=ProcessMethodType, documentation=u'Characteristic list for quick discovery'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'keywords'), CTD_ANON_21, scope=ProcessMethodType, documentation=u'Means of providing a list of keywords (with a codeSpace) for quick discovery'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'classification'), CTD_ANON_7, scope=ProcessMethodType, documentation=u'Means of specifying classification values with types such as "sensorType", "intendedApplication", etc., whose terms can be defined in a dictionary'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'capabilities'), CTD_ANON_11, scope=ProcessMethodType, documentation=u'Capability list for quick discovery'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'implementation'), CTD_ANON_9, scope=ProcessMethodType, documentation=u'Points to the reference implementation of this process in the specified programming language (can be a SensorML process chain)'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'), CTD_ANON_48, scope=ProcessMethodType, documentation=u'Means of providing legal constraints of description'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'rules'), CTD_ANON_76, scope=ProcessMethodType, documentation=u'Text and/or language defining rules for process profile (e.g. inputs, outputs, parameters, and metadata)'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'contact'), CTD_ANON_13, scope=ProcessMethodType, documentation=u'Relevant contacts for that object'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'), CTD_ANON_4, scope=ProcessMethodType, documentation=u'Means of providing security constraints of description'))

ProcessMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'algorithm'), CTD_ANON_32, scope=ProcessMethodType, documentation=u'Textual and/or MathML description of the algorithm'))
ProcessMethodType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rules'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rules'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rules'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rules'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rules'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rules'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rules'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rules'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'algorithm'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'implementation'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=ProcessMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'implementation'))),
    ])
})



SystemType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'positions'), CTD_ANON_71, scope=SystemType, documentation=u'Relative positions of the System components'))

SystemType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'components'), CTD_ANON_34, scope=SystemType, documentation=u'Collection of subprocesses that can be chained using connections'))

SystemType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'connections'), CTD_ANON_10, scope=SystemType, documentation=u'provides links between processes or between data sources and processes'))
SystemType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=13, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 12 : pyxb.binding.content.ContentModelState(state=12, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 13 : pyxb.binding.content.ContentModelState(state=13, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=16, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 14 : pyxb.binding.content.ContentModelState(state=14, is_final=True, transitions=[
    ])
    , 15 : pyxb.binding.content.ContentModelState(state=15, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
    ])
    , 16 : pyxb.binding.content.ContentModelState(state=16, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 17 : pyxb.binding.content.ContentModelState(state=17, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
    ])
    , 18 : pyxb.binding.content.ContentModelState(state=18, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=18, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 19 : pyxb.binding.content.ContentModelState(state=19, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'location'))),
        pyxb.binding.content.ContentModelTransition(next_state=20, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'positions'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=12, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'timePosition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'position'))),
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
        pyxb.binding.content.ContentModelTransition(next_state=15, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'components'))),
        pyxb.binding.content.ContentModelTransition(next_state=17, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'inputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interfaces'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outputs'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'temporalReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=19, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'spatialReferenceFrame'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameters'))),
    ])
    , 20 : pyxb.binding.content.ContentModelState(state=20, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=14, element_use=SystemType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'connections'))),
    ])
})



CTD_ANON_67._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'mathML'), CTD_ANON_40, scope=CTD_ANON_67, documentation=u'Includes or reference a MathML doc specifying the maths of the algorithm'))

CTD_ANON_67._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), pyxb.bundles.opengis.gml.StringOrRefType, scope=CTD_ANON_67, documentation=u'Contains a simple text description of the object, or refers to an external description.'))
CTD_ANON_67._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_67._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_67._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mathML'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_67._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mathML'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



CTD_ANON_68._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Time'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_15, scope=CTD_ANON_68, documentation=u'Either ISO 8601 (e.g. 2004-04-18T12:03:04.6Z) or time relative to a time origin'))

CTD_ANON_68._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Process'), AbstractProcessType, abstract=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_68, documentation=u'base substitution group for all processes'))
CTD_ANON_68._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_68._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Time'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_68._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_Process'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_69._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'classifier'), CTD_ANON_50, scope=CTD_ANON_69))
CTD_ANON_69._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_69._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_69._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classifier'))),
    ])
})



CTD_ANON_70._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'destination'), CTD_ANON_63, scope=CTD_ANON_70))

CTD_ANON_70._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'source'), CTD_ANON_73, scope=CTD_ANON_70))
CTD_ANON_70._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_70._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_70._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'destination'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



CTD_ANON_71._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PositionList'), CTD_ANON_59, scope=CTD_ANON_71))
CTD_ANON_71._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_71._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PositionList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_72._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Process'), AbstractProcessType, abstract=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_72, documentation=u'base substitution group for all processes'))

CTD_ANON_72._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DocumentList'), CTD_ANON_24, scope=CTD_ANON_72, documentation=u'List of documents related to the enclosing object'))

CTD_ANON_72._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ContactList'), CTD_ANON_47, scope=CTD_ANON_72, documentation=u'Allows to group several contacts together in a list that can be referenced as a whole'))
CTD_ANON_72._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_72._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_Process'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_72._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ContactList'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_72._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DocumentList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



componentsPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProcessList'), AbstractListType, scope=componentsPropertyType))
componentsPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=componentsPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ProcessList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



PresentationLayerPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'), pyxb.bundles.opengis.swe_1_0_1.AbstractDataRecordType, abstract=pyxb.binding.datatypes.boolean(1), scope=PresentationLayerPropertyType))

PresentationLayerPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Category'), pyxb.bundles.opengis.swe_1_0_1.CTD_ANON_5, scope=PresentationLayerPropertyType, documentation=u'A simple token identifying a term or category (single spaces allowed); definition attribute should provide dictionary entry useful for interpretation of the value'))

PresentationLayerPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataStreamDefinition'), pyxb.bundles.opengis.swe_1_0_1.DataStreamDefinitionType, scope=PresentationLayerPropertyType))

PresentationLayerPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataBlockDefinition'), pyxb.bundles.opengis.swe_1_0_1.DataBlockDefinitionType, scope=PresentationLayerPropertyType))
PresentationLayerPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PresentationLayerPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'AbstractDataRecord'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PresentationLayerPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataStreamDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PresentationLayerPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'Category'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=PresentationLayerPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/swe/1.0.1'), u'DataBlockDefinition'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


CTD_ANON_75._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_75._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ParameterList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_76._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RulesDefinition'), CTD_ANON_78, scope=CTD_ANON_76))
CTD_ANON_76._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_76._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RulesDefinition'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



DataSourceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'), CTD_ANON_57, scope=DataSourceType))

DataSourceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'observationReference'), CTD_ANON_35, scope=DataSourceType))

DataSourceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'values'), CTD_ANON_80, scope=DataSourceType))
DataSourceType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'observationReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'observationReference'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'values'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'observationReference'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=7, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'observationReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 7 : pyxb.binding.content.ContentModelState(state=7, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'observationReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 8 : pyxb.binding.content.ContentModelState(state=8, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'observationReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
    , 9 : pyxb.binding.content.ContentModelState(state=9, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'keywords'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'classification'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=9, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identification'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'observationReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
        pyxb.binding.content.ContentModelTransition(next_state=10, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'validTime'))),
    ])
    , 10 : pyxb.binding.content.ContentModelState(state=10, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'securityConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'observationReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
    , 11 : pyxb.binding.content.ContentModelState(state=11, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'history'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'contact'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'dataDefinition'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'characteristics'))),
        pyxb.binding.content.ContentModelTransition(next_state=11, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'legalConstraint'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'observationReference'))),
        pyxb.binding.content.ContentModelTransition(next_state=8, element_use=DataSourceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'capabilities'))),
    ])
})



CTD_ANON_77._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'city'), pyxb.binding.datatypes.string, scope=CTD_ANON_77))

CTD_ANON_77._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'administrativeArea'), pyxb.binding.datatypes.string, scope=CTD_ANON_77))

CTD_ANON_77._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'postalCode'), pyxb.binding.datatypes.string, scope=CTD_ANON_77))

CTD_ANON_77._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'country'), pyxb.binding.datatypes.string, scope=CTD_ANON_77))

CTD_ANON_77._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'deliveryPoint'), pyxb.binding.datatypes.string, scope=CTD_ANON_77))

CTD_ANON_77._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'electronicMailAddress'), pyxb.binding.datatypes.string, scope=CTD_ANON_77))
CTD_ANON_77._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'city'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'administrativeArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'postalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'country'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'deliveryPoint'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'electronicMailAddress'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'electronicMailAddress'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'administrativeArea'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'postalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'country'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'electronicMailAddress'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'postalCode'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'country'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'electronicMailAddress'))),
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'country'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_77._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'electronicMailAddress'))),
    ])
})



inputsPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InputList'), AbstractListType, scope=inputsPropertyType))
inputsPropertyType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=inputsPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'InputList'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_78._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ruleLanguage'), ruleLanguageType, abstract=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_78, documentation=u'substitutionGroup for languages that define rules'))

CTD_ANON_78._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'), pyxb.bundles.opengis.gml.StringOrRefType, scope=CTD_ANON_78, documentation=u'Contains a simple text description of the object, or refers to an external description.'))
CTD_ANON_78._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_78._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_78._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ruleLanguage'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=CTD_ANON_78._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ruleLanguage'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
    ])
})



CTD_ANON_79._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'identifier'), CTD_ANON_82, scope=CTD_ANON_79))
CTD_ANON_79._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_79._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identifier'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_79._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'identifier'))),
    ])
})


CTD_ANON_80._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})


CTD_ANON_81._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=set(u'http://relaxng.org/ns/structure/1.0'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_82._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Term'), CTD_ANON_20, scope=CTD_ANON_82, documentation=u'A well defined token used to specify identifier and classifier values (single spaces allowed)'))
CTD_ANON_82._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_82._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Term'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



CTD_ANON_83._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'parameter'), pyxb.bundles.opengis.swe_1_0_1.DataComponentPropertyType, scope=CTD_ANON_83))
CTD_ANON_83._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_83._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameter'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=CTD_ANON_83._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parameter'))),
    ])
})

ProcessModel._setSubstitutionGroup(Process)

Component._setSubstitutionGroup(Process)

schematron._setSubstitutionGroup(ruleLanguage)

ComponentArray._setSubstitutionGroup(Process)

ProcessChain._setSubstitutionGroup(Process)

System._setSubstitutionGroup(Process)

DataSource._setSubstitutionGroup(Process)

relaxNG._setSubstitutionGroup(ruleLanguage)
