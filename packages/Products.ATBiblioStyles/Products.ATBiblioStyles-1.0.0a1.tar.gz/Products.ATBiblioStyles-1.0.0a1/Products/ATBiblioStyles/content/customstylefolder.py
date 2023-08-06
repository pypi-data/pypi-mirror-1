##########################################################################
#                                                                        #
#              copyright (c) 2004 Belgian Science Policy                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

""" BibrefCustomStyleFolder class
"""

#import string
#from types import StringType

#from DocumentTemplate import sequence

from Products.Archetypes.public import BaseFolderSchema
from Products.Archetypes.public import BaseFolder, registerType

# XXX: Still needed??
#def modify_fti(fti):
#    """ overwrite the default immediate view """
#    fti['immediate_view'] = 'folder_contents'

class BibrefCustomStyleFolder(BaseFolder):
    """ container for custom bibref styles
    """

    schema = BaseFolderSchema

registerType(BibrefCustomStyleFolder)

