from Interface import Interface

class IBibrefStyle(Interface):
    """ Interface for the format 
        renderers of the bibliolist tool.
    """
    def formatDictionary():
        """ returns the rendered bib ref
            refValues must be a dictionnary holding all values
        """
    # due to a misprint in former style versions this has to be here for compatibility
    formatDictionnary = formatDictionary


from zope.interface import Interface

class IBiblioStylesTool(Interface):
    
    """Marker interface for the bibliostyles tool
    """

class IBiblioStyle(Interface):
    
    """Marker interface for bibliographic styles
    """

