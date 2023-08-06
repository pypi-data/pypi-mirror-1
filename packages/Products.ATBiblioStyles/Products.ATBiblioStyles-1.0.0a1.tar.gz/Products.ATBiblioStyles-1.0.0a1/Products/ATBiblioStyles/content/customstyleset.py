##########################################################################
#                                                                        #
#              copyright (c) 2004 Belgian Science Policy                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

""" BibrefCustomStyleSet: combining multiple BibrefCustomStyles to allow 
    each type of reference to have its own presentation format.
"""
__old_name__ = 'Products.ATBiblioList.BibrefCustomstyleSet'

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName

from Products.CMFCore import permissions

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import BaseContent, registerType
from Products.Archetypes.Widget import SelectionWidget

from Products.CMFBibliographyAT.config import REFERENCE_TYPES
from Products.ATBiblioStyles.interface import IBibrefStyle
from Products.ATBiblioStyles.interface import IBiblioStylesTool

schema = BaseSchema + Schema((
    StringField('DefaultStyle',
#                 multiValued=0,
                 vocabulary="vocabCustomStyleSel",
                 relationship='has CustomStyleSel',
                 default='stl_default',
#                 enforce_vocabulary=1,
                 widget=SelectionWidget(label="Default Presentation Style",
                                        label_msgid="label_styleset_default",
                                        description_msgid="help_styleset_default",
                                        description="Select the default bibliographic style you want to present your list with.",
                                        i18n_domain="plone",
                                        format="select",
                                        ),
                   ),
                              ))

def buildStyleSetSchema():
    """ Dynamic schema building
    """
    
    presentation_set_schema = []
    for reftype in REFERENCE_TYPES:
        reftype = reftype.replace('Reference', ' Reference')+' Style'
        elem = StringField(reftype,
                           vocabulary = "vocabCustomStyleDef",
                           default = 'Default',
                           widget = SelectionWidget(label=reftype.replace('Reference Style', 'Reference'),
                                                    label_msgid="",
                                                    description_msgid="help_styleset_list",
                                                    description="Select the bibliographic style how you want to present your list for this type of reference.",
                                                    i18n_domain="plone",
                                                    format='pulldown',
                                                    ),
                           )
        presentation_set_schema.append(elem)

    return Schema(presentation_set_schema) 
    
class BibrefCustomStyleSet(BaseContent):
    """ Specific Bibliographical Styles 
    """
    __implements__ = (IBibrefStyle ,)

    schema = schema + buildStyleSetSchema()

    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'vocabCustomStyleSel')
    def vocabCustomStyleSel(self):
        """ values for the default bibref style """
        return self.buildVocab()

    security.declareProtected(permissions.View, 'vocabCustomStyleDef')
    def vocabCustomStyleDef(self):
        """ values for each specific bibtex type's style """
        return self.buildVocab(('Default','Default'))

    security.declarePrivate('buildVocab')
    def buildVocab(self, default_value=None):
        """ build a DisplayList based on existing styles """
        if default_value:
            vocab = [default_value,]
        else:
            vocab = []
        bstool = getToolByName(self, 'portal_bibliostyles')
        styles = bstool.findBibrefStyles()
        for style in styles:
            vocab.append(style)
        return DisplayList(tuple(vocab))

    security.declarePrivate('formatDictionary')
    def formatDictionary(self, refValues):
        """ formats a bibref dictionnary
        """
        field = self.getField('%s Style' %refValues['meta_type'].replace('Reference', ' Reference'))
        style = getattr(self, field.accessor)()
        if style.lower() == 'default':
            style = self.getDefaultStyle()
        bstool = getToolByName(self, 'portal_bibliostyles')
        return bstool.formatDicoRef(refValues, style)

    security.declarePrivate('formatDictionnary')
    formatDictionnary = formatDictionary

    security.declareProtected(permissions.View, 'formatDummyList')
    def formatDummyList(self):
        """ renders a formatted bibref dummy list
            only used for display in custom style view
        """
        bstool = getToolByName(self, 'portal_bibliostyles')
        formatted_list = []
        for ref in self.dummy_refs():
            field = self.getField('%s Reference Style' %ref['ref_type'])
            style = getattr(self, field.accessor)()
            if style.lower() == 'default':
                style = self.getDefaultStyle()
            result = bstool.formatDicoRef(ref, style)
            formatted_list.append(
                {'type':ref['ref_type']+' Reference', 'result':result}
                                  )
        return formatted_list

registerType(BibrefCustomStyleSet)
