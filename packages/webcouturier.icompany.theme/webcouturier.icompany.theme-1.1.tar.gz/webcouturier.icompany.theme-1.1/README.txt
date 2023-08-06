webcouturier.icompany.theme Package Readme
=========================

Overview
--------

"Web Couturier iCompany Theme" for online Plone themes' shop Web Couturier

Installation

    Web Couturier advises to use buildout for your projects, built with Plone
    3.x.
    
    The buildout way:
    
        1. Unpack webcouturier.icompany.theme package to src/ folder of your buildout
        2. Edit your buildout.cfg and add the following information::
    
            [buildout]
            ...
            eggs = 
                webcouturier.icompany.theme
    
            [instance]
            zcml = 
                ...
                webcouturier.icompany.theme
        
        The last line tells buildout to generate a zcml snippet that tells
        Zope to configure webcouturier.icompany.theme.
    
        If another package depends on the webcouturier.icompany.theme egg or includes
        its zcml directly you do not need to specify anything in the buildout
        configuration: buildout will detect this automatically.

        After updating the configuration you need to run the ''bin/buildout'',
        which will take care of updating your system.

    Go to the 'Site Setup' page in the Plone interface and click on the
    'Add/Remove Products' link.
    
    Choose the product (check its checkbox) and click the 'Install' button.
    
    Uninstall -- This can be done from the same management screen, but only
    if you installed it from the quick installer.

    Note: You may have to empty your browser cache to see the effects of the
    product installation.

Credits

    Andrey Lyashenko [drey.dex@gmail.com] - design
    
    Michael Krishtopa [theo@sed.lg.ua] - Plone theme for Plone 2.5
    
    Denys Mishunov [denys@jarn.com] - Plone theme for Plone 3.x
    
    Jarn AS [http://jarn.com] - wished to pay for this theme to be publicly available
