=============================
beyondskins.ploneday.site2009 
=============================

Overview
--------

This product is an installable Plone 3 Theme developed by `Simples
Consultoria <http://www.simplesconsultoria.com.br/>`_ for the World Plone Day 
2009 initiative, promoted by Plone Foundation.

Requirements
------------
    - Plone 3.3 (http://plone.org/products/plone)

    - Plone 3.2.x (http://plone.org/products/plone)
    
    - Plone 3.1.x (http://plone.org/products/plone)
    
    - Plone 3.0.x (http://plone.org/products/plone)

Installation
------------
    
To use this skin, on a buildout based installation:

    1. Unpack beyondskins.ploneday.site2009 package to src/ folder of your 
    buildout
    2. Edit your buildout.cfg and add the following information::

        [buildout]
        ...
        eggs = 
            beyondskins.ploneday.site2009

        [instance]
        zcml = 
            ...
            beyondskins.ploneday.site2009
    
    The last line tells buildout to generate a zcml snippet that tells
    Zope to configure beyondskins.ploneday.site2009.

    If another package depends on the beyondskins.ploneday.site2009 egg or 
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
    
    * Firefox 3 (WinXP/Vista/MacOSX)
    
    * Safari 3 (WinXP/Vista/MacOSX)

Credits
-------

    * Andre Nogueira (andre at simplesconsultoria dot com dot br) - Design
    
    * Thiago Tamosauskas (thiago at simplesconsultoria dot com dot br) - 
      Implementation, CSS Magic and IE fixes
    
    * Simples Consultoria (products at simplesconsultoria dot com dot br) - 
      Packaging

