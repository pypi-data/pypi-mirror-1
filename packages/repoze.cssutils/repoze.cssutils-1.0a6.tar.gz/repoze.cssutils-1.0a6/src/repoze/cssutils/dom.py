"""
CSS DOM Support

Primary Classes:

    * CSSDOMElementInterface
        Implementation of css.CSSElementInterfaceBase

"""

from repoze.cssutils import css


class CSSDOMElementInterface(css.CSSElementInterfaceBase):
    """An implementation of css.CSSElementInterfaceBase for xml.dom Element Nodes"""

    style = None

    _pseudoStateHandlerLookup = {
        'first-child': 
            lambda self: not bool(self.getPreviousSibling()),
        'not-first-child': 
            lambda self: bool(self.getPreviousSibling()),

        'last-child': 
            lambda self: not bool(self.getNextSibling()),
        'not-last-child': 
            lambda self: bool(self.getNextSibling()),

        'middle-child': 
            lambda self: not bool(self.getPreviousSibling()) and not bool(self.getNextSibling()),
        'not-middle-child': 
            lambda self: bool(self.getPreviousSibling()) or bool(self.getNextSibling()),
        }

    def __init__(self, domElement):
        self.domElement = domElement

    def matchesNode(self, (namespace, tagName)):
        if tagName not in ('*', self.domElement.tagName):
            return False
        if namespace in (None, '', '*'):
            # matches any namespace
            return True
        else: # full compare
            return namespace == self.domElement.namespaceURI

    def getAttr(self, name, default=NotImplemented):
        attrValue = self.domElement.attributes.get(name)
        if attrValue is not None:
            return attrValue.value
        else:
            return default

    def inPseudoState(self, name, params=()):
        handler = self._pseudoStateHandlerLookup.get(name, lambda self: False)
        return handler(self)

    def iterXMLParents(self, includeSelf=False):
        klass = self.__class__
        current = self.domElement
        if not includeSelf: 
            current = current.parentNode
        while (current is not None) and (current.nodeType == current.ELEMENT_NODE):
            yield klass(current)
            current = current.parentNode

    def getPreviousSibling(self):
        sibling = self.domElement.previousSibling
        while sibling:
            if sibling.nodeType == sibling.ELEMENT_NODE:
                return sibling
            else:
                sibling = sibling.previousSibling
        return None
    def getNextSibling(self):
        sibling = self.domElement.nextSibling
        while sibling:
            if sibling.nodeType == sibling.ELEMENT_NODE:
                return sibling
            else:
                sibling = sibling.nextSibling
        return None


class CSSDOMCascadeStrategy(css.CSSCascadeStrategy):
    def _normalizeCSSElement(self, element):
        if not isinstance(elemnet, CSSDOMElementInterface):
            return 