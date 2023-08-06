beyondskins.pythonbrasil.site
=============================

Overview
--------

This product is a installable Plone 3 Theme developed by `Simples
Consultoria <http://www.simplesconsultoria.com.br/>`_ for use in  `Python Brasil 
[5] <http://www.pythonbrasil.org.br/>`_ Conference web site.

Python Brasil is the new name of PyConBrasil -- The Brazilian Python Conference.
 
Requirements
------------        

    - Plone 3.3.x (http://plone.org/products/plone)

    - Plone 3.2.x (http://plone.org/products/plone)

Installation
------------

This skin was developed to be installed on `Python Brasil [5] 
<http://www.pythonbrasil.org.br/>`_ web site, so there are hard-coded stuff 
that should be cleaned up prior to this skin be usable on another Plone site.

To use this skin, on a buildout based installation:

    1. Unpack beyondskins.pythonbrasil.site package to src/ folder of your 
    buildout
    2. Edit your buildout.cfg and add the following information::

        [buildout]
        ...
        eggs = 
            beyondskins.pythonbrasil.site

        [instance]
        zcml = 
            ...
            beyondskins.pythonbrasil.site
    
    The last line tells buildout to generate a zcml snippet that tells
    Zope to configure beyondskins.pythonbrasil.site.

    If another package depends on the beyondskins.pythonbrasil.site egg or 
    includes its zcml directly you do not need to specify anything in the 
    buildout configuration: buildout will detect this automatically.

    After updating the configuration you need to run the ''bin/buildout'',
    which will take care of updating your system.

Go to the 'Site Setup' page in the Plone interface and click on the
'Add/Remove Products' link.

Choose the product (check its checkbox) and click the 'Install' button.

Uninstall -- This can be done from the same management screen, but only
if you installed it from the quick installer.

Note: You may have to empty your browser cache to see the effects of the
product installation.

Browsers and OS's
-----------------
    
    * Internet Explorer 8.0 (WinXP/Vista)
    
    * Internet Explorer 7.0 (WinXP/Vista)
    
    * Firefox 3.5 (Vista/MacOSX/Linux)
    
    * Firefox 3 (WinXP/Vista/MacOSX/Linux)
    
    * Safari 4 (WinXP/Vista/MacOSX)

    * Safari 3 (WinXP/Vista/MacOSX)

Credits
-------
    
    * APyB (Associacao Python Brasil) and Python Brasil [5] Staff.

    * Andre Nogueira (andre at simplesconsultoria dot com dot br) - Design
    
    * Thiago Tamosauskas (thiago at simplesconsultoria dot com dot br) - 
      Implementation, CSS Magic and IE fixes

    * Simples Consultoria (products at simplesconsultoria dot com dot br) 
      Packaging
