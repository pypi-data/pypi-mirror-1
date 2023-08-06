# ./pyxb/bundles/opengis/raw/_atom.py
# PyXB bindings for NamespaceModule
# NSM:741a4e51acfa398449878d8690bb692b0b09b93a
# Generated 2009-11-30 18:10:20.433825 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:e8791576-de0d-11de-8a2e-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom', create_if_missing=True)
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
class atomEmailAddress (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'atomEmailAddress')
    _Documentation = None
atomEmailAddress._CF_pattern = pyxb.binding.facets.CF_pattern()
atomEmailAddress._CF_pattern.addPattern(pattern=u'.+@.+')
atomEmailAddress._InitializeFacetMap(atomEmailAddress._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'atomEmailAddress', atomEmailAddress)

# Atomic SimpleTypeDefinition
class atomMediaType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'atomMediaType')
    _Documentation = None
atomMediaType._CF_pattern = pyxb.binding.facets.CF_pattern()
atomMediaType._CF_pattern.addPattern(pattern=u'.+/.+')
atomMediaType._InitializeFacetMap(atomMediaType._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'atomMediaType', atomMediaType)

# Atomic SimpleTypeDefinition
class atomLanguageTag (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'atomLanguageTag')
    _Documentation = None
atomLanguageTag._CF_pattern = pyxb.binding.facets.CF_pattern()
atomLanguageTag._CF_pattern.addPattern(pattern=u'[A-Za-z]{1,8}(-[A-Za-z0-9]{1,8})*')
atomLanguageTag._InitializeFacetMap(atomLanguageTag._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'atomLanguageTag', atomLanguageTag)

# Complex type atomPersonConstruct with content type ELEMENT_ONLY
class atomPersonConstruct (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'atomPersonConstruct')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2005/Atom}email uses Python identifier email
    __email = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'email'), 'email', '__httpwww_w3_org2005Atom_atomPersonConstruct_httpwww_w3_org2005Atomemail', True)

    
    email = property(__email.value, __email.set, None, None)

    
    # Element {http://www.w3.org/2005/Atom}uri uses Python identifier uri
    __uri = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'uri'), 'uri', '__httpwww_w3_org2005Atom_atomPersonConstruct_httpwww_w3_org2005Atomuri', True)

    
    uri = property(__uri.value, __uri.set, None, None)

    
    # Element {http://www.w3.org/2005/Atom}name uses Python identifier name
    __name = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'name'), 'name', '__httpwww_w3_org2005Atom_atomPersonConstruct_httpwww_w3_org2005Atomname', True)

    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        __email.name() : __email,
        __uri.name() : __uri,
        __name.name() : __name
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'atomPersonConstruct', atomPersonConstruct)


# Complex type CTD_ANON_1 with content type EMPTY
class CTD_ANON_1 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute hreflang uses Python identifier hreflang
    __hreflang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'hreflang'), 'hreflang', '__httpwww_w3_org2005Atom_CTD_ANON_1_hreflang', atomLanguageTag)
    
    hreflang = property(__hreflang.value, __hreflang.set, None, None)

    
    # Attribute rel uses Python identifier rel
    __rel = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'rel'), 'rel', '__httpwww_w3_org2005Atom_CTD_ANON_1_rel', pyxb.binding.datatypes.anySimpleType)
    
    rel = property(__rel.value, __rel.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpwww_w3_org2005Atom_CTD_ANON_1_type', atomMediaType)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'title'), 'title', '__httpwww_w3_org2005Atom_CTD_ANON_1_title', pyxb.binding.datatypes.anySimpleType)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute length uses Python identifier length
    __length = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'length'), 'length', '__httpwww_w3_org2005Atom_CTD_ANON_1_length', pyxb.binding.datatypes.anySimpleType)
    
    length = property(__length.value, __length.set, None, None)

    
    # Attribute href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'href'), 'href', '__httpwww_w3_org2005Atom_CTD_ANON_1_href', pyxb.binding.datatypes.anySimpleType, required=True)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __hreflang.name() : __hreflang,
        __rel.name() : __rel,
        __type.name() : __type,
        __title.name() : __title,
        __length.name() : __length,
        __href.name() : __href
    }



author = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'author'), atomPersonConstruct)
Namespace.addCategoryObject('elementBinding', author.name().localName(), author)

email = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'email'), atomEmailAddress)
Namespace.addCategoryObject('elementBinding', email.name().localName(), email)

uri = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'uri'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', uri.name().localName(), uri)

name = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'name'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', name.name().localName(), name)

link = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'link'), CTD_ANON_1)
Namespace.addCategoryObject('elementBinding', link.name().localName(), link)



atomPersonConstruct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'email'), atomEmailAddress, scope=atomPersonConstruct))

atomPersonConstruct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'uri'), pyxb.binding.datatypes.string, scope=atomPersonConstruct))

atomPersonConstruct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'name'), pyxb.binding.datatypes.string, scope=atomPersonConstruct))
atomPersonConstruct._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=atomPersonConstruct._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=atomPersonConstruct._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'email'))),
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=atomPersonConstruct._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'uri'))),
    ])
})
