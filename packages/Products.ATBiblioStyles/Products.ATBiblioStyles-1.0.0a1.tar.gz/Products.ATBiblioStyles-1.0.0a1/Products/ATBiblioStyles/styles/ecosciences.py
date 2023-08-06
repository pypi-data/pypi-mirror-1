##########################################################################
#                                                                        #
#    copyright (c) 2004 Ecology Center, Kiel Universitzy Germany         #
#                       and contributors                                 #
#                                                                        #
##########################################################################

""" EcosciencesBibrefStyle class
"""
import string

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog
from Products.CMFCore.utils import getToolByName

# CMFBibliographyAT stuff
from Products.CMFBibliographyAT.interface import IBibliographyTool

# Bibliolist stuff
from base import BibrefStyle
from Products.ATBiblioStyles.interface import IBiblioStylesTool


class EcoSciencesBibrefStyle(BibrefStyle):
    """ specific formatter to process input in ecosciences format
    """

    meta_type = "EcoSciences Bibref Style"

    def __init__(self, id = 'EcoSciences',
                 title = "EcoSciences bibliography reference style"):
        """ initializes only id and title
        """
        self.id = id
        self.title = title

    def formatDictionary(self, refValues):
        """ formats a bibref dictionnary
        """
        bibtool = getToolByName(self, 'portal_bibliography')
        bs_tool = getToolByName(self, 'portal_bibliostyles')
        formatted_entry = ''
	publication_url = ''
	
        entry_type = refValues.get('meta_type')
        if not entry_type:
            entry_type = str(refValues.get('ref_type'))+'Reference'

        if entry_type in bibtool.getReferenceTypes():
            #authors
            authors = self.getRefValuesFailSafe(refValues, 'authors')
	    editor_flag = self.getRefValuesFailSafe(refValues, 'editor_flag', False)
	    formatted_entry += '<div style="padding-bottom: 4pt;text-align:justify;text-indent:-2em; padding-left: 2em;"><span style="font-variant:small-caps;">'
            if authors == []:
                pass
            elif len(authors) == 1:
                formatted_entry += '%s ' % self.formatAuthor(authors[0])
            else:
                formatted_entry += '%s' % self.formatAuthor(authors[0])
                if len(authors[1:-1]):
                    for author in authors[1:-1]:
                        formatted_entry += ', %s' % self.formatAuthor(author)
                formatted_entry += ' & %s' % self.formatAuthor(authors[-1])
                formatted_entry += ' '
	    formatted_entry += '</span>'
            
            # editor flag
	    if editor_flag:
		formatted_entry += ' (ed.)'

            # publication year
            if self.getRefValuesFailSafe(refValues, 'publication_year', ''):
                formatted_entry += ' (%s):' % self.getRefValuesFailSafe(refValues, 'publication_year')

            # title
            title_link = self.getRefValuesFailSafe(refValues, 'title_link', False)
            title_state_class = self.getRefValuesFailSafe(refValues, 'review_state', 'published')
            title = self.getRefValuesFailSafe(refValues, 'title', 'No Title')
	    if title and title[-1] not in '.?!': title += '.'
	    came_from = self.getRefValuesFailSafe(refValues, 'came_from', '') or ''
            came_from_title = self.getRefValuesFailSafe(refValues, 'came_from_title', '') or ''
            came_from_description = self.getRefValuesFailSafe(refValues, 'came_from_description', '') or ''
            description = self.getRefValuesFailSafe(refValues, 'description', '')
            if len(description) >= 75:
                description = description.strip()[:75] + '...'
            if title_link:
                title = ' <a class="link-silent state-%s" title="%s" href="%s?came_from=%s&came_from_title=%s&came_from_description=%s">%s</a>' % (title_state_class, description, title_link, came_from, came_from_title, came_from_description, title)
            formatted_entry += ' ' + title 

	    source = ''
    	    ##
	    ## ArticleRefernce
	    ##
	    if entry_type in ('ArticleReference',):
		journal = self.getRefValuesFailSafe(refValues, 'journal', '')
		volume = self.getRefValuesFailSafe(refValues, 'volume', '')
		number = self.getRefValuesFailSafe(refValues, 'number', '')
		pages = self.getRefValuesFailSafe(refValues, 'pages', '')
		source += '<i>%s</i>' % journal
		if volume:
		    source += ', <b>%s</b>' % volume
		    if number:
		        source += '(%s)' % number
		if pages:
		    source += ':%s' % pages

            ##
	    ## BookReference
	    ##
	    elif entry_type in ('BookReference',):
		publisher = self.getRefValuesFailSafe(refValues, 'publisher', '')
		address = self.getRefValuesFailSafe(refValues, 'address', '')
		edition = self.getRefValuesFailSafe(refValues, 'edition', '')
		volume = self.getRefValuesFailSafe(refValues, 'volume', '')
		number = self.getRefValuesFailSafe(refValues, 'number', '')
		series = self.getRefValuesFailSafe(refValues, 'series', '')

		source += publisher
		if address: source += ', %s' % address
		if edition: source += ', %s' % bs_tool.formatEdition(edition)
		if volume:
		    source += ', vol. <b>%s</b>' % volume
		    if number: source += '(%s)' % number
		if source and (source[-1] not in '!?.'): source += '.'
		if series: source += ' %s' % series
		if source and (source[-1] not in '!?.'): source += '.'
		
	    ##
	    ## InbookReference
	    ## InproceedingsReference
	    ## IncollectionReference
	    ##
	    elif entry_type in ('InbookReference', 'InproceedingsReference', 'IncollectionReference','Conference'):
		booktitle = self.getRefValuesFailSafe(refValues, 'booktitle', '')
		volume = self.getRefValuesFailSafe(refValues, 'volume', '')
		number = self.getRefValuesFailSafe(refValues, 'number', '')
		editor = self.getRefValuesFailSafe(refValues, 'editor', '')
		publication_type = self.getRefValuesFailSafe(refValues, 'publication_type', '')
		organization = self.getRefValuesFailSafe(refValues, 'organization', '')
		publisher = self.getRefValuesFailSafe(refValues, 'publisher', '')
		address = self.getRefValuesFailSafe(refValues, 'address', '')
		edition = self.getRefValuesFailSafe(refValues, 'edition', '')
		series = self.getRefValuesFailSafe(refValues, 'series', '')
		pages = self.getRefValuesFailSafe(refValues, 'pages', '')
	
		if editor: source += 'In: <span style="font-variant:small-caps;">%s</span> (ed.):' % editor
		if booktitle: source += ' %s' % booktitle
		if volume: 
		    source += ', Vol. <b>%s</b>' % volume
		    if number: source += '(%s)' % number
		if pages: source += ', pp. %s' % pages
		if publication_type: source += ', %' % publication_type
		if organization: source += ', %s' % organization
		if publisher: source += ', %s' % publisher
		if address: source += ', %s' % address
		if edition: source += ', %s' % self.formatEdition(edition)
		if series: source += '. %s' % series

            ##
	    ## MasterthesisReference
            ## PhdthesisReference
	    ## 
	    elif entry_type in ('MasterthesisReference','PhdthesisReference'):
                publication_type = self.getRefValuesFailSafe(refValues, 'publication_type', '')
		school = self.getRefValuesFailSafe(refValues, 'school', '')
		address = self.getRefValuesFailSafe(refValues, 'address', '') 
		publication_url = self.getRefValuesFailSafe(refValues, 'publication_url', '')
		
                if publication_type:
                    source = publication_type
                else:
		    if entry_type == 'MasterthesisReference':
                	source = 'Master thesis'
		    else:
			source = 'PhD thesis'

        	if school: source += ', %s' % school
        	if address: source += ', %s' % address
	
            ##
	    ## ManualReference
	    ## 
	    elif entry_type in ('ManualReference',):
		address = self.getRefValuesFailSafe(refValues, 'address', '') 
                edition = self.getRefValuesFailSafe(refValues, 'edition', '')
		publication_url = self.getRefValuesFailSafe(refValues, 'publication_url', '')
		
	        if address: 
		    source += '%s' % address
		    if edition: source += ', '
	        if edition: source += '%s ed.' % edition
	
            ##
	    ## TechreportReference
	    ## 
	    elif entry_type in ('TechreportReference',):
		publication_type = self.getRefValuesFailSafe(refValues, 'publication_type', '')
		address = self.getRefValuesFailSafe(refValues, 'address', '') 
                institution = self.getRefValuesFailSafe(refValues, 'institution', '')
                number = self.getRefValuesFailSafe(refValues, 'number', '')

		source = institution		
                if publication_type:
                    source += ', %s' % publication_type
                    if number: source += '(%s)' % number
                if address: source += ', %s' % address
	
	    ##
	    ## ProceedingsReference
	    ## 
	    elif entry_type in ('ProceedingsReference',):
		volume = self.getRefValuesFailSafe(refValues, 'volume', '')
		number = self.getRefValuesFailSafe(refValues, 'number', '')
		address = self.getRefValuesFailSafe(refValues, 'address', '')
		publisher = self.getRefValuesFailSafe(refValues, 'publisher', '')
		organization = self.getRefValuesFailSafe(refValues, 'organization', '')
		series = self.getRefValuesFailSafe(refValues, 'series', '')
		if series: source += ' %s' % series
		if volume: 
		    source += ', Vol. <b>%s</b>' % volume
		    if number: source += '(%s)' % number
		if organization: source += ', %s' % organization
		if publisher: source += ', %s' % publisher
		if address: source += ', %s' % address

            ##
	    ## WebpublishedReference
	    ## 
	    elif entry_type in ('WebpublishedReference',):
		publication_url = self.getRefValuesFailSafe(refValues, 'publication_url', '')
                
	    else:
		source += ' - %s' % refValues.get('source')
	    
    	    if source and (source[-1] not in '.!?'):
		source += '.'

            ## add the gathered source information to formatted_entry...
            if source:
	        formatted_entry += ' ' + source

            # add the note
            note = self.getRefValuesFailSafe(refValues, 'note', '')
	    if note: formatted_entry += ' - %s' % note
	    if formatted_entry[-1] not in '!?.': formatted_entry += '.'

            # add the publication_url if set somewhere above
	    if publication_url: formatted_entry += ' - <a class="link-silent" href="%s" target="_new">%s</a>' % (publication_url, publication_url, )
	    if formatted_entry[-1] not in '!?.': formatted_entry += '.'
	    
	    formatted_entry += '</div>'
	
        return formatted_entry
    
    # due to a misprint in former style versions this has to be here for compatibility
    formatDictionnary = formatDictionary

    def getRefValuesFailSafe(self, refValues, field, default=None):
    
	try: 
	    return refValues.get(field)
	except TypeError:
	    return default    

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
          result = '<a class="link-silent" href="%s">%s</a>' %(url, result)
        return result

# Class instanciation
InitializeClass(EcoSciencesBibrefStyle)
   
def manage_addEcoSciencesBibrefStyle(self, REQUEST=None):
    """ """
    try:
        self._setObject('EcoSciences', EcoSciencesBibrefStyle())
    except:
        return MessageDialog(
            title='BiblioList tool warning message',
            message='The bibref style you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
