##########################################################################
#                                                                        #
#              copyright (c) 2004 Belgian Science Policy                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

""" package installer for ATBiblioStyles """

from Products.CMFCore.permissions import AddPortalContent

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

PROJECTNAME = 'ATBiblioStyles'
GLOBALS = globals()
skin_names = ('bibliography_styles',)

ADD_CONTENT_PERMISSION = AddPortalContent

registerDirectory('skins', GLOBALS)

import content
from tool import bibliostyles

def initialize(context):

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    tools = (bibliostyles.BiblioStylesTool,)

    utils.ToolInit(
        'BiblioStyles Tool',
        tools=tools,
        icon='bib_tool.gif',
        ).initialize(context)

    styles.initialize(context)

import modulealiases
