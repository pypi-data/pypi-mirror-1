##########################################################################
#                                                                        #
#              copyright (c) 2004 Belgian Science Policy                 #
#                                 and contributors                       #
#                                                                        #
#     maintainers: David Convent, david.convent@naturalsciences.be       #
#                  Louis Wannijn, louis.wannijn@naturalsciences.be       #
#                                                                        #
##########################################################################

"""BiblioStylesTool class"""

import Products

# Zope stuff
from zope.interface import implements
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder

# CMF stuff
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import getToolByName

# Archetypes stuff
from Products.Archetypes.interfaces import IArchetypeTool

# CMFBibliographyAT stuff
from Products.CMFBibliographyAT.interface import IBibliographyTool

# ATBiblioStyles stuff
from Products.ATBiblioStyles.interface import IBibrefStyle, IBiblioStylesTool
from Products.ATBiblioStyles.styles.minimal import MinimalBibrefStyle
from Products.ATBiblioStyles.styles.chicago import ChicagoBibrefStyle
from Products.ATBiblioStyles.styles.harvard import HarvardBibrefStyle
from Products.ATBiblioStyles.styles.mla import MLABibrefStyle
from Products.ATBiblioStyles.styles.apa import APABibrefStyle
from Products.ATBiblioStyles.styles.ecosciences import EcoSciencesBibrefStyle
from Products.ATBiblioStyles.styles.default import DefaultBibrefStyle

from Products.CMFBibliographyAT.interface import IBibliographicItem

try:
    from bibliograph.core.utils import _decode
except:
    from Products.CMFBibliographyAT.utils import _decode

from Products.PlacelessTranslationService.utility import PTSTranslationDomain

bibliostyles_domain = PTSTranslationDomain('atbibliostyles')



class BiblioStylesTool(UniqueObject, Folder):
    """ Tool for managing format rendering for references 
        contained in ATBiblioList and ATBiblioTopic.
    """

    implements(IBiblioStylesTool)

    id = 'portal_bibliostyles'
    meta_type = 'BiblioStyles Tool'

    security = ClassSecurityInfo()

    manage_options = (
        (Folder.manage_options[0],)
        + Folder.manage_options[2:]
        )

    index_html = None

    def all_meta_types(self):
        product_infos = Products.meta_types
        possibles = []
        for p in product_infos:
            try:
                if IBibrefStyle in p.get('interfaces', []):
                    possibles.append(p)
            except TypeError:
                pass
        definites = map(lambda x: x.meta_type, self.objectValues())
        return filter(lambda x,y=definites: x['name'] not in y, possibles)

    security.declarePrivate('getBibrefStyleNames')
    def getBibrefStyleNames(self):
        """ returns a list with the names of the available bibref styles
        """
        # get FormatName()??? not working for default styles (Plone 3.3)
        return [bibrefStyle.getFormatName()
                for bibrefStyle in self.objectValues()]

    security.declareProtected(permissions.View, 'formatList')
    def formatList(self, refs, style, instance=None, title_link=None, title_link_only_if_owner=False, brains_object=False, sort=True):
        """ renders BibliographyList / BibliographyTopic referenced objects in the specified style
        """
        # (added ajung)
        # allow 'refs' being a single bibliographic item
        if IBibliographicItem.providedBy(refs):
            objs = [refs]
        else:
            if brains_object:
                objs = [ ref.getObject() for ref in refs ]
            else:
                objs = [ ref.getTargetObject() for ref in refs ]
        uflist = [self.getEntryDict(obj, instance=instance, title_link=title_link, title_link_only_if_owner=title_link_only_if_owner) for obj in objs]
        if sort:
            formatted_list = [self.formatDicoRef(obj, style)
                              for obj in self.sortBibrefDictList(uflist)]
        else:
            formatted_list = [self.formatDicoRef(obj, style)
                              for obj in uflist] 
        return tuple(formatted_list)

    security.declarePrivate('formatDicoRef')
    def formatDicoRef(self, refValues, style):
        """ returns a Bibliography Reference
            rendered in the specified style
            refValues must be a python dictionnary
        """
        bibrefStyle = self.getBibrefStyle(style)
        if bibrefStyle:
            return bibrefStyle.formatDictionary(refValues)
        return 'The Selected Bibref Style could not be found.'

    security.declarePrivate('getBibrefStyle')
    def getBibrefStyle(self, style):
        """ returns the formatter for the specified style
        """
        if style[:4] == 'stl_':
            for bibrefStyle in self.objectValues():
                if style[4:].lower() == bibrefStyle.getId().lower():
                    return bibrefStyle
        else:
            at_tool = getToolByName(self, 'archetype_tool')
            try:
                bibrefStyle = at_tool.lookupObject(style)
                return bibrefStyle
            except: 
                return None

    security.declarePublic('findBibrefStyles')
    def findBibrefStyles(self):
        """ Builds style selection vocabulary
        """
        styles = []
        # portal_bibliostyles styles
        for style in self.objectValues():
            styles.append(('stl_'+style.getId().lower(),style.getId()))
        # custom styles and sets
        catalog = getToolByName(self, 'portal_catalog')
        cstyles = catalog(portal_type=('BibrefCustomStyle','BibrefCustomStyleSet'))
        for cstyle in cstyles:
            obj = cstyle.getObject()
            if cstyle.meta_type == 'BibrefCustomStyle':
                styles.append((obj.UID(),obj.title_or_id()+' (Custom Style)'))
            if cstyle.meta_type == 'BibrefCustomStyleSet':
                styles.append((obj.UID(),obj.title_or_id()+' (Custom Style Set)'))
        return tuple(styles)

    security.declarePrivate('getEntryDict')
    def getEntryDict(self, entry, instance=None, title_link=False, title_link_only_if_owner=False):
        """ transform a BiblioRef Object into python dictionnary, this method has moved to CMFBAT's bibliography tool
        """
        bib_tool = getToolByName(self, 'portal_bibliography')
        return bib_tool.getEntryDict(entry, instance=instance, title_link=title_link, title_link_only_if_owner=title_link_only_if_owner)

    def formatEdition(self, edition, abbreviate=False):

        if abbreviate:
            _edition = bibliostyles_domain.translate('format_edition_abbreviated.', default='ed.')
        else: 
            _edition = bibliostyles_domain.translate('format_edition', default='edition')
        try:
            test = int(edition)
            if edition[-1] == '1':
                result = '%sst %s' % (edition, _edition)
            elif edition[-1] == '2':
                result = '%snd %s' % (edition, _edition)
            elif edition[-1] == '3':
                result = '%srd %s' % (edition, _edition)
            else:
                result = '%sth %s' % (edition, _edition)
        except ValueError:
            if len(''.join([ char for char in edition if char in 'ivxlmcIVXLMC' ])) == len(edition):
                result = '%s. %s' % (edition, _edition)
            else:
                result = '%s %s' % (edition, _edition)

        return result

    def getGivenNameInitials(self, author, dot_after_initials=True, keep_hyphens=True):

        GIVENNAME_SEPARATORS = (' ', '-')
        HYPHEN = '-'
        # we assume that there are more than one name hidden in each field
        firstnames = author.get('firstname', '')
        middlenames = author.get('middlename', '')

        given_name = (firstnames + ' ' + middlenames).strip()

        if given_name:
            initials = given_name[0]
            if dot_after_initials: initials += '.'
            for i in range(len(given_name[1:])):
                if given_name[i-1] in GIVENNAME_SEPARATORS:
                    if (given_name[i-1] == HYPHEN) and keep_hyphens:
                        initials += HYPHEN
                    initials += given_name[i]
                    if dot_after_initials: initials += '.'

            return initials

        return ''

InitializeClass(BiblioStylesTool)
registerToolInterface('portal_bibliostyles', IBiblioStylesTool)
