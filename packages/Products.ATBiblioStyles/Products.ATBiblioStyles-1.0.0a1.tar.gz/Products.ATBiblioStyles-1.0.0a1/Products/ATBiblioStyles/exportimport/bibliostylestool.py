

from zope.component import adapts
from zope.component import getSiteManager

from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import NodeAdapterBase

from Products.ATBiblioStyles.interface import IBiblioStylesTool
from Products.ATBiblioStyles.interface import IBiblioStyle


class BiblioStylesToolStyleNodeAdapter(NodeAdapterBase,
                                       PropertyManagerHelpers):

    """Node im- and exporter for styles contained in the BiblioStyles tool
    """

    adapts(IBiblioStyle, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        purge = self.environ.shouldPurge()
        if node.getAttribute('purge'):
            purge = self._convertToBoolean(node.getAttribute('purge'))
        if purge:
            self._purgeProperties()

        self._initProperties(node)

    node = property(_exportNode, _importNode)


class BiblioStylesToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                                 PropertyManagerHelpers):

    """XML im- and exporter for the BiblioStyles tool.
    """

    adapts(IBiblioStylesTool, ISetupEnviron)

    _LOGGER_ID = 'bibliostyles'

    name = 'bibliostylestool'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())

        self._logger.info('Bibliostyles tool exported.')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeObjects()

        self._initProperties(node)
        self._initObjects(node)

        self._logger.info('Bibliostyles tool imported.')



def importBiblioStylesTool(context):
    """Import BiblioStyles tool and contained styles definitions from XML
    files.
    """
    sm = getSiteManager(context.getSite())
    tool = getToolByName(sm, 'portal_bibliostyles')

    importObjects(tool, '', context)

def exportBiblioStylesTool(context):
    """Export BiblioStyles tool and contained styles definitions from XML
    files.
    """
    sm = getSiteManager(context.getSite())
    tool = sm.queryUtility(IBiblioStylesTool)
    if tool is None:
        logger = context.getLogger('bibliostyles')
        logger.info('Nothing to export.')
        return
    exportObjects(tool, '', context)
