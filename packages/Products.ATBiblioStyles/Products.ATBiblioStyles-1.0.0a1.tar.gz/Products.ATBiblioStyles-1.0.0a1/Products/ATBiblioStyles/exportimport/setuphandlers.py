from StringIO import StringIO

def resetObsoleteSettings(context):
    """Remove portal_bibiolist tool if is exists."""
    site = context.getSite()
    logger = context.getLogger('bibliostyles')
    out = StringIO()
    if hasattr(site, 'portal_bibliolist'):
        site.manage_delObjects(['portal_bibliolist'])
        print >> out, "Deleted old tool formerly belonging to ATBiblioList."
    else:
        print >> out, "Old tool not found."
    logger.info(out.getvalue())

    return 'Old settings from ATBiblioList reset.'
