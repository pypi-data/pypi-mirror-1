##########################################################################
#                                                                        #
#              copyright (c) 2004 Belgian Science Policy                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

"""BibrefStyle main class"""

from zope.interface import implements
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

from Products.ATBiblioStyles.interface import IBibrefStyle
from Products.ATBiblioStyles.interface import IBiblioStyle as z3IBiblioStyle

class BibrefStyle(SimpleItem, PropertyManager):
    """ Base class for the input formatter of the bibliolist tool.
    """
    __implements__ = (SimpleItem.__implements__,
                      IBibrefStyle,)
    implements(z3IBiblioStyle)

    meta_type = 'Bibref Style'
    
    manage_options = (
        PropertyManager.manage_options +
        SimpleItem.manage_options
    )
    _properties = PropertyManager._properties + (
        {'id':'bibstyle_enabled',
         'type':'boolean',
         'mode':'w',
         },
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title=''):
        """ minimal initialization
        """
        self.id = id
        self.title = title

    def formatDictionary(self, refValues):
        """ renders a formatted bibliography reference based on dictionnary values
        """
        pass # needs to be overwritten by individual styles

    # due to a misprint in former style versions this has to be here for compatibility
    formatDictionnary = formatDictionary
    

# Class instanciation
InitializeClass(BibrefStyle)