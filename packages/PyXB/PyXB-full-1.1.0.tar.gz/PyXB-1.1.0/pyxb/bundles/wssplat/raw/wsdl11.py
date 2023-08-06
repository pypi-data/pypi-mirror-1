# ./pyxb/bundles/wssplat/raw/wsdl11.py
# PyXB bindings for NamespaceModule
# NSM:d363f64a147eb09d66a961a815c9d842964c1c79
# Generated 2009-11-30 18:08:32.096046 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:a8f93c78-de0d-11de-a696-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/wsdl/', create_if_missing=True)
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


# Complex type tDocumented with content type ELEMENT_ONLY
class tDocumented (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tDocumented')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schemas.xmlsoap.org/wsdl/}documentation uses Python identifier documentation
    __documentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'documentation'), 'documentation', '__httpschemas_xmlsoap_orgwsdl_tDocumented_httpschemas_xmlsoap_orgwsdldocumentation', False)

    
    documentation = property(__documentation.value, __documentation.set, None, None)


    _ElementMap = {
        __documentation.name() : __documentation
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'tDocumented', tDocumented)


# Complex type tExtensibleDocumented with content type ELEMENT_ONLY
class tExtensibleDocumented (tDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tExtensibleDocumented')
    # Base type is tDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    _HasWildcardElement = True

    _ElementMap = tDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tDocumented._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tExtensibleDocumented', tExtensibleDocumented)


# Complex type tOperation with content type ELEMENT_ONLY
class tOperation (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tOperation')
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}fault uses Python identifier fault
    __fault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'fault'), 'fault', '__httpschemas_xmlsoap_orgwsdl_tOperation_httpschemas_xmlsoap_orgwsdlfault', True)

    
    fault = property(__fault.value, __fault.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}output uses Python identifier output
    __output = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'output'), 'output', '__httpschemas_xmlsoap_orgwsdl_tOperation_httpschemas_xmlsoap_orgwsdloutput', False)

    
    output = property(__output.value, __output.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}input uses Python identifier input
    __input = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'input'), 'input', '__httpschemas_xmlsoap_orgwsdl_tOperation_httpschemas_xmlsoap_orgwsdlinput', False)

    
    input = property(__input.value, __input.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tOperation_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute parameterOrder uses Python identifier parameterOrder
    __parameterOrder = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'parameterOrder'), 'parameterOrder', '__httpschemas_xmlsoap_orgwsdl_tOperation_parameterOrder', pyxb.binding.datatypes.NMTOKENS)
    
    parameterOrder = property(__parameterOrder.value, __parameterOrder.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __fault.name() : __fault,
        __output.name() : __output,
        __input.name() : __input
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name,
        __parameterOrder.name() : __parameterOrder
    })
Namespace.addCategoryObject('typeBinding', u'tOperation', tOperation)


# Complex type tBindingOperationMessage with content type ELEMENT_ONLY
class tBindingOperationMessage (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBindingOperationMessage')
    # Base type is tExtensibleDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tBindingOperationMessage_name', pyxb.binding.datatypes.NCName)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tBindingOperationMessage', tBindingOperationMessage)


# Complex type tDefinitions with content type ELEMENT_ONLY
class tDefinitions (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tDefinitions')
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}service uses Python identifier service
    __service = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'service'), 'service', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdlservice', True)

    
    service = property(__service.value, __service.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}binding uses Python identifier binding
    __binding = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'binding'), 'binding', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdlbinding', True)

    
    binding = property(__binding.value, __binding.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}types uses Python identifier types
    __types = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'types'), 'types', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdltypes', True)

    
    types = property(__types.value, __types.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}message uses Python identifier message
    __message = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'message'), 'message', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdlmessage', True)

    
    message = property(__message.value, __message.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}import uses Python identifier import_
    __import = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'import'), 'import_', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdlimport', True)

    
    import_ = property(__import.value, __import.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}portType uses Python identifier portType
    __portType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'portType'), 'portType', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdlportType', True)

    
    portType = property(__portType.value, __portType.set, None, None)

    
    # Attribute targetNamespace uses Python identifier targetNamespace
    __targetNamespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetNamespace'), 'targetNamespace', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_targetNamespace', pyxb.binding.datatypes.anyURI)
    
    targetNamespace = property(__targetNamespace.value, __targetNamespace.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_name', pyxb.binding.datatypes.NCName)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __service.name() : __service,
        __binding.name() : __binding,
        __types.name() : __types,
        __message.name() : __message,
        __import.name() : __import,
        __portType.name() : __portType
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __targetNamespace.name() : __targetNamespace,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tDefinitions', tDefinitions)


# Complex type tExtensibleAttributesDocumented with content type ELEMENT_ONLY
class tExtensibleAttributesDocumented (tDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tExtensibleAttributesDocumented')
    # Base type is tDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tDocumented._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tExtensibleAttributesDocumented', tExtensibleAttributesDocumented)


# Complex type tParam with content type ELEMENT_ONLY
class tParam (tExtensibleAttributesDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tParam')
    # Base type is tExtensibleAttributesDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute message uses Python identifier message
    __message = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'message'), 'message', '__httpschemas_xmlsoap_orgwsdl_tParam_message', pyxb.binding.datatypes.QName, required=True)
    
    message = property(__message.value, __message.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tParam_name', pyxb.binding.datatypes.NCName)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tExtensibleAttributesDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleAttributesDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __message.name() : __message,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tParam', tParam)


# Complex type tTypes with content type ELEMENT_ONLY
class tTypes (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tTypes')
    # Base type is tExtensibleDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tTypes', tTypes)


# Complex type tMessage with content type ELEMENT_ONLY
class tMessage (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tMessage')
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}part uses Python identifier part
    __part = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'part'), 'part', '__httpschemas_xmlsoap_orgwsdl_tMessage_httpschemas_xmlsoap_orgwsdlpart', True)

    
    part = property(__part.value, __part.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tMessage_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __part.name() : __part
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tMessage', tMessage)


# Complex type tPortType with content type ELEMENT_ONLY
class tPortType (tExtensibleAttributesDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPortType')
    # Base type is tExtensibleAttributesDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}operation uses Python identifier operation
    __operation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'operation'), 'operation', '__httpschemas_xmlsoap_orgwsdl_tPortType_httpschemas_xmlsoap_orgwsdloperation', True)

    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tPortType_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tExtensibleAttributesDocumented._ElementMap.copy()
    _ElementMap.update({
        __operation.name() : __operation
    })
    _AttributeMap = tExtensibleAttributesDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tPortType', tPortType)


# Complex type tBinding with content type ELEMENT_ONLY
class tBinding (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBinding')
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}operation uses Python identifier operation
    __operation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'operation'), 'operation', '__httpschemas_xmlsoap_orgwsdl_tBinding_httpschemas_xmlsoap_orgwsdloperation', True)

    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpschemas_xmlsoap_orgwsdl_tBinding_type', pyxb.binding.datatypes.QName, required=True)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tBinding_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __operation.name() : __operation
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __type.name() : __type,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tBinding', tBinding)


# Complex type tImport with content type ELEMENT_ONLY
class tImport (tExtensibleAttributesDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tImport')
    # Base type is tExtensibleAttributesDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpschemas_xmlsoap_orgwsdl_tImport_namespace', pyxb.binding.datatypes.anyURI, required=True)
    
    namespace = property(__namespace.value, __namespace.set, None, None)

    
    # Attribute location uses Python identifier location
    __location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'location'), 'location', '__httpschemas_xmlsoap_orgwsdl_tImport_location', pyxb.binding.datatypes.anyURI, required=True)
    
    location = property(__location.value, __location.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tExtensibleAttributesDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleAttributesDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __namespace.name() : __namespace,
        __location.name() : __location
    })
Namespace.addCategoryObject('typeBinding', u'tImport', tImport)


# Complex type tFault with content type ELEMENT_ONLY
class tFault (tExtensibleAttributesDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFault')
    # Base type is tExtensibleAttributesDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute message uses Python identifier message
    __message = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'message'), 'message', '__httpschemas_xmlsoap_orgwsdl_tFault_message', pyxb.binding.datatypes.QName, required=True)
    
    message = property(__message.value, __message.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tFault_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tExtensibleAttributesDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleAttributesDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __message.name() : __message,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tFault', tFault)


# Complex type tService with content type ELEMENT_ONLY
class tService (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tService')
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}port uses Python identifier port
    __port = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'port'), 'port', '__httpschemas_xmlsoap_orgwsdl_tService_httpschemas_xmlsoap_orgwsdlport', True)

    
    port = property(__port.value, __port.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tService_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __port.name() : __port
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tService', tService)


# Complex type tExtensibilityElement with content type EMPTY
class tExtensibilityElement (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tExtensibilityElement')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://schemas.xmlsoap.org/wsdl/}required uses Python identifier required
    __required = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'required'), 'required', '__httpschemas_xmlsoap_orgwsdl_tExtensibilityElement_httpschemas_xmlsoap_orgwsdlrequired', pyxb.binding.datatypes.boolean)
    
    required = property(__required.value, __required.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __required.name() : __required
    }
Namespace.addCategoryObject('typeBinding', u'tExtensibilityElement', tExtensibilityElement)


# Complex type tBindingOperation with content type ELEMENT_ONLY
class tBindingOperation (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBindingOperation')
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}fault uses Python identifier fault
    __fault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'fault'), 'fault', '__httpschemas_xmlsoap_orgwsdl_tBindingOperation_httpschemas_xmlsoap_orgwsdlfault', True)

    
    fault = property(__fault.value, __fault.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}input uses Python identifier input
    __input = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'input'), 'input', '__httpschemas_xmlsoap_orgwsdl_tBindingOperation_httpschemas_xmlsoap_orgwsdlinput', False)

    
    input = property(__input.value, __input.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}output uses Python identifier output
    __output = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'output'), 'output', '__httpschemas_xmlsoap_orgwsdl_tBindingOperation_httpschemas_xmlsoap_orgwsdloutput', False)

    
    output = property(__output.value, __output.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tBindingOperation_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __fault.name() : __fault,
        __input.name() : __input,
        __output.name() : __output
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tBindingOperation', tBindingOperation)


# Complex type tPart with content type ELEMENT_ONLY
class tPart (tExtensibleAttributesDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPart')
    # Base type is tExtensibleAttributesDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpschemas_xmlsoap_orgwsdl_tPart_type', pyxb.binding.datatypes.QName)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tPart_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute element uses Python identifier element
    __element = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'element'), 'element', '__httpschemas_xmlsoap_orgwsdl_tPart_element', pyxb.binding.datatypes.QName)
    
    element = property(__element.value, __element.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tExtensibleAttributesDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleAttributesDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __type.name() : __type,
        __name.name() : __name,
        __element.name() : __element
    })
Namespace.addCategoryObject('typeBinding', u'tPart', tPart)


# Complex type tPort with content type ELEMENT_ONLY
class tPort (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPort')
    # Base type is tExtensibleDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute binding uses Python identifier binding
    __binding = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'binding'), 'binding', '__httpschemas_xmlsoap_orgwsdl_tPort_binding', pyxb.binding.datatypes.QName, required=True)
    
    binding = property(__binding.value, __binding.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tPort_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __binding.name() : __binding,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tPort', tPort)


# Complex type tDocumentation with content type MIXED
class tDocumentation (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tDocumentation')
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'tDocumentation', tDocumentation)


# Complex type tBindingOperationFault with content type ELEMENT_ONLY
class tBindingOperationFault (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBindingOperationFault')
    # Base type is tExtensibleDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tBindingOperationFault_name', pyxb.binding.datatypes.NCName, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tBindingOperationFault', tBindingOperationFault)


definitions = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'definitions'), tDefinitions)
Namespace.addCategoryObject('elementBinding', definitions.name().localName(), definitions)



tDocumented._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), tDocumentation, scope=tDocumented))
tDocumented._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tDocumented._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


tExtensibleDocumented._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tExtensibleDocumented._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
})



tOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'fault'), tFault, scope=tOperation))

tOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'output'), tParam, scope=tOperation))

tOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'input'), tParam, scope=tOperation))
tOperation._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input'))),
        pyxb.binding.content.ContentModelTransition(next_state=5, element_use=tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault'))),
    ])
    , 5 : pyxb.binding.content.ContentModelState(state=5, is_final=False, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=5, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output'))),
    ])
    , 6 : pyxb.binding.content.ContentModelState(state=6, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=6, element_use=tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault'))),
    ])
})


tBindingOperationMessage._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBindingOperationMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
})



tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'service'), tService, scope=tDefinitions))

tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'binding'), tBinding, scope=tDefinitions))

tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'types'), tTypes, scope=tDefinitions))

tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'message'), tMessage, scope=tDefinitions))

tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'import'), tImport, scope=tDefinitions))

tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'portType'), tPortType, scope=tDefinitions))
tDefinitions._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'service'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binding'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'types'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'message'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'import'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'portType'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'service'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binding'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'types'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'message'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'import'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'portType'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binding'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'service'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'types'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'message'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'import'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'portType'))),
    ])
})


tExtensibleAttributesDocumented._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tExtensibleAttributesDocumented._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


tParam._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tParam._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


tTypes._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tTypes._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
})



tMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'part'), tPart, scope=tMessage))
tMessage._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'part'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'part'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'part'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
})



tPortType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operation'), tOperation, scope=tPortType))
tPortType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tPortType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tPortType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tPortType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operation'))),
    ])
})



tBinding._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operation'), tBindingOperation, scope=tBinding))
tBinding._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tBinding._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBinding._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBinding._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operation'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBinding._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operation'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
})


tImport._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tImport._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


tFault._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tFault._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})



tService._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'port'), tPort, scope=tService))
tService._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tService._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tService._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'port'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tService._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'port'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tService._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'port'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
})



tBindingOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'fault'), tBindingOperationFault, scope=tBindingOperation))

tBindingOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'input'), tBindingOperationMessage, scope=tBindingOperation))

tBindingOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'output'), tBindingOperationMessage, scope=tBindingOperation))
tBindingOperation._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=4, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, element_use=tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault'))),
    ])
    , 4 : pyxb.binding.content.ContentModelState(state=4, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input'))),
        pyxb.binding.content.ContentModelTransition(next_state=4, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault'))),
    ])
})


tPart._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tPart._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
    ])
})


tPort._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tPort._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
})


tDocumentation._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)),
    ])
})


tBindingOperationFault._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=tBindingOperationFault._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation'))),
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))),
    ])
})
