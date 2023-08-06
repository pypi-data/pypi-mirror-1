Description

  This product is an add-on to Raphael Ritz's CMFBibliographyAT.
  
  It is used by ATBiblioList and ATBiblioTopic to format the display of
  bibliography references listings (biblio smart folders and biblio lists
  contents) in pre formatted ways, or by using custom designed styles created
  by portal users.

  It should not be too difficult for a python programmer to write its own
  file system based bibliography styles. If you do so, please share your
  interesting bibliography styles with the community.


What It Does

  * Installs the 'portal_bibliostyles' tool which performs.

  * Installs some FS based Bibref Styles in the 'portal_bibliostyles' tool:

    - Minimal: Default minimal bibliography style.

    - APA: American Psychological Association bibliography style.
    
    - MLA: Modern Language Association style.

    - Chicago and Harvard styles.

  * Installs a few Archetypes based content types for handling custom styles
    and style sets: 'Bibref Custom Style', 'Bibref Custom Style Set', and
    'Bibref Custom Style Folder'.


Requirements

  * Plone 3.0+
  
  * CMFBibliographyAT (1.0 or svn/trunk)


Installation

  - First, add the product to Zope:

    * extract the product from its archive and move it to the Products
      directory of your Zope Instance.

  - Then, install the product in Plone:

    * From the Plone interface, log in as manager and go to 'Site Setup' >
      'Add-on Products'.
      Check 'ATBiblioStyles' and click Install.


Upgrade

  - If you upgrade from earlier version, you may have to reinstall the product
    with the portal_quickinstaller.


Licence

  see LICENCE.txt


Contact

  David Convent - david.convent(at)naturalsciences(dot)be

  Mailing list for topics about CMFBibliographyAT, its add-on products and
  bibliography reference management with Plone in general:
  plone-biblio(at)zaubberer(dot)net.
  
  Mailing list registration at:
  https://zaubberer.net/mailman/listinfo/plone-biblio


To Do

  * Write more unit tests !!

  * Export formatted lists in rtf.

  * More Bibref Styles to come: We'll have to write more specific styles in
    order to meet the needs of our scientific staff.


