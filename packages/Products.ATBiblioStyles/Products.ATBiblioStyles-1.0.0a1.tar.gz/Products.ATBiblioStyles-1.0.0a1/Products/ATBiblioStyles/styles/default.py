##########################################################################
#                                                                        #
#    copyright (c) 2004 Royal Belgian Institute for Natural Sciences     #
#                       and contributors                                 #
#                                                                        #
##########################################################################

""" DefaultBibrefStyle class
    default bibliography style (as in CMFBibliographyAT
"""

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog
from Products.CMFCore.utils import getToolByName

# CMFBibliographyAT stuff
from Products.CMFBibliographyAT.config import REFERENCE_TYPES

# Bibliolist stuff
from base import BibrefStyle
from Products.ATBiblioStyles.interface import IBiblioStylesTool


class DefaultBibrefStyle(BibrefStyle):
    """ specific formatter to process input in minimal format
    """

    meta_type = "Default Bibref Style"

    def __init__(self, id = 'Default',
                 title = "Default bibliography reference style"):
        """ initializes only id and title
        """
        self.id = id
        self.title = title

    def formatDictionary(self, refValues):
        """ formats a bibref dictionary
        """
        formatted_entry = ''

        entry_type = refValues.get('meta_type')
        if not entry_type:
            entry_type = str(refValues.get('ref_type'))+'Reference'

        if entry_type in REFERENCE_TYPES:
            #authors
	    formatted_entry += '<p class="body">' 
	    
	    authors = refValues.get('authors')
	    if authors == []:
                pass
	    elif len(authors) == 1:
	        formatted_entry += '%s' % self.formatAuthor(authors[0])
	    else:
	        formatted_entry += '%s' % self.formatAuthor(authors[0])
	        for author in authors[1:-1]:
	            formatted_entry += ', %s' % self.formatAuthor(author)
	        
		formatted_entry += ', and %s' % self.formatAuthor(authors[-1])
	    
            # editor flag
            if refValues.get('editor_flag'):
                formatted_entry += ' (ed.)'
            # publication year
            if refValues.get('publication_year'):
                formatted_entry += ' (%s).<br />' % refValues.get('publication_year')

            # title
            title_link = refValues.get('title_link')
            title = refValues.get('title')
            if title and title[-1] not in '.?!': title += '.'
            description = refValues.get('description')
            if len(description) >= 75:
                description = description.strip()[:75] + '...'
            if title_link:
                title = ' <a href="%s"><b>%s</b></a>' % (title_link, title)
            else: 
	        title = '<b>' + title + '</b>'
	    formatted_entry = formatted_entry + title + '<br />'

            #source
            formatted_entry += '%s' % refValues.get('source')
            formatted_entry += '</p>'
	    
        return formatted_entry

    def formatAuthor(self, author):
        """ formats a single author for this format """
        bs_tool = getToolByName(self, 'portal_bibliostyles')
        last = author.get('lastname')
        initials = bs_tool.getGivenNameInitials(author, dot_after_initials=False, keep_hyphens=False)
        if initials and last:
            result = '%s&nbsp;%s' % (last, initials)
        elif last:
            result = '%s' % last
        else:
            return ''
            
        url = author.get('homepage')
        if url:
          result = '<a href="%s">%s</a>' %(url, result)
        return result

# Class instanciation
InitializeClass(DefaultBibrefStyle)

   
def manage_addDefaultBibrefStyle(self, REQUEST=None):
    """ """
    try:
        self._setObject('Default', DefaultBibrefStyle())
    except:
        return MessageDialog(
            title='BiblioList tool warning message',
            message='The bibref style you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
