# ./pyxb/bundles/opengis/raw/_smil20.py
# PyXB bindings for NamespaceModule
# NSM:21ae4a2357cfe334f6a0ce0b0ea28423d22a1453
# Generated 2009-11-30 18:09:46.502356 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:d19fe820-de0d-11de-8fc5-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.bundles.opengis.raw._nsgroup_

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/SMIL20/', create_if_missing=True)
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

from pyxb.bundles.opengis.raw._nsgroup_ import animateColor # {http://www.w3.org/2001/SMIL20/}animateColor
from pyxb.bundles.opengis.raw._nsgroup_ import animateMotion_ as animateMotion # {http://www.w3.org/2001/SMIL20/}animateMotion
from pyxb.bundles.opengis.raw._nsgroup_ import set_ as set # {http://www.w3.org/2001/SMIL20/}set
from pyxb.bundles.opengis.raw._nsgroup_ import animate # {http://www.w3.org/2001/SMIL20/}animate
from pyxb.bundles.opengis.raw._nsgroup_ import STD_ANON_1 # None
from pyxb.bundles.opengis.raw._nsgroup_ import STD_ANON_2 # None
from pyxb.bundles.opengis.raw._nsgroup_ import STD_ANON_3 # None
from pyxb.bundles.opengis.raw._nsgroup_ import animateMotionPrototype # {http://www.w3.org/2001/SMIL20/}animateMotionPrototype
from pyxb.bundles.opengis.raw._nsgroup_ import fillDefaultType # {http://www.w3.org/2001/SMIL20/}fillDefaultType
from pyxb.bundles.opengis.raw._nsgroup_ import restartTimingType # {http://www.w3.org/2001/SMIL20/}restartTimingType
from pyxb.bundles.opengis.raw._nsgroup_ import syncBehaviorDefaultType # {http://www.w3.org/2001/SMIL20/}syncBehaviorDefaultType
from pyxb.bundles.opengis.raw._nsgroup_ import syncBehaviorType # {http://www.w3.org/2001/SMIL20/}syncBehaviorType
from pyxb.bundles.opengis.raw._nsgroup_ import restartDefaultType # {http://www.w3.org/2001/SMIL20/}restartDefaultType
from pyxb.bundles.opengis.raw._nsgroup_ import fillTimingAttrsType # {http://www.w3.org/2001/SMIL20/}fillTimingAttrsType
from pyxb.bundles.opengis.raw._nsgroup_ import STD_ANON_4 # None
from pyxb.bundles.opengis.raw._nsgroup_ import animateColorPrototype # {http://www.w3.org/2001/SMIL20/}animateColorPrototype
from pyxb.bundles.opengis.raw._nsgroup_ import setPrototype # {http://www.w3.org/2001/SMIL20/}setPrototype
from pyxb.bundles.opengis.raw._nsgroup_ import animatePrototype # {http://www.w3.org/2001/SMIL20/}animatePrototype
from pyxb.bundles.opengis.raw._nsgroup_ import nonNegativeDecimalType # {http://www.w3.org/2001/SMIL20/}nonNegativeDecimalType
