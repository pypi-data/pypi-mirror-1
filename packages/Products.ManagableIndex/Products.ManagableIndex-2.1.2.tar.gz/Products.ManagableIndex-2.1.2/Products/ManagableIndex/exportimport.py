"""GenericSetup support"""

from zope.interface import implementsOnly
from zope.component import adapts, getMultiAdapter

from dm.reuse import rebindFunction

from Products.GenericSetup.interfaces import INode, ISetupEnviron
from Products.GenericSetup.utils import NodeAdapterBase, PropertyManagerHelpers
from Products.GenericSetup.OFSP.exportimport import FolderXMLAdapter

from interfaces import IManagableIndex, IPropertyManager

class IndexNodeAdapter(FolderXMLAdapter):
  adapts(IManagableIndex, ISetupEnviron)

  # indicate that we are a real (trustworthy) "INode" adapter
  #  even though we inherited from a class implementing "IBody" (whose "INode"
  #  subinterface often surprises).
  implementsOnly(INode)

  def _exportNode(self):
    node = self._getObjectNode('index')
    # prevent default value provider generation on import
    ec = self._doc.createComment('prevent default value provider generation')
    extra = self._doc.createElement('extra')
    extra.setAttribute('name', 'ValueProviders')
    extra.setAttribute('value', '')
    node.appendChild(ec); node.appendChild(extra)
    node.appendChild(self._extractProperties())
    node.appendChild(self._extractObjects())
    return node

  def _importNode(self, node):
    super(IndexNodeAdapter, self)._importNode(node)
    self.context.clear()

  def _initObjects(self, node):
    return rebindFunction(
      super(IndexNodeAdapter, self)._initObjects,
      Products=_O(meta_types=self.context.all_meta_types()),
      )(self, node)

  node = property(_exportNode, _importNode)


class PropertyManagerNodeAdapter(NodeAdapterBase, PropertyManagerHelpers):
  adapts(IPropertyManager, ISetupEnviron)

  def _exportNode(self):
    node = self._getObjectNode('object')
    node.appendChild(self._extractProperties())
    return node

  def _importNode(self, node):
    if self.environ.shouldPurge():
      self._purgeProperties()
    self._initProperties(node)

  node = property(_exportNode, _importNode)
    
    
class _O(object):
  """Auxiliary object wrapper."""
  def __init__(self, **kw): self.__dict__.update(kw)
