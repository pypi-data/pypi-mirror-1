webcouturier.hosting.theme Package Readme
=========================

Overview
--------

"Web Couturier Hosting Theme" for online Plone themes' shop Web Couturier

Installation

    Web Couturier advises to use buildout for your projects, built with Plone
    3.x.
    
    The buildout way:
    
        1. Unpack webcouturier.theme3 package to src/ folder of your buildout
        2. Edit your buildout.cfg and add the following information::
    
            [buildout]
            ...
            develop =
                src/webcouturier.theme3
    
            [instance]
            eggs = 
                ...
                webcouturier.theme3
            zcml = 
                ...
                webcouturier.theme3
        
        The last line tells buildout to generate a zcml snippet that tells
        Zope to configure webcouturier.theme3.
    
        If another package depends on the webcouturier.theme3 egg or includes
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
    
    
Features

    1. Contains new set of actions in portal_actions (called top_navigation)
    to have one more set of navigation items at the most top of the site
    
    2. Contains special table class for Kupu editor - ''orangeTable''.
    Produces tables with orange headers.
    
    3. Contains special <A> class for Kupu editor - ''moreButton''. Produces
    linka as the orange button.
    
    4. To translate your new top_navigation items in multi-language sites you
    can use **takeaction** product - http://plone.org/products/takeaction


Use cases

    1. Change actions at the top of site ('Test Link #1', 'Test Link #2' and
    so on):
    
     - go to portal_actions/top_navigation and find actions you want to change
     
     - change Title and id fields for appropriate actions - change
     URL(Expression) field to link to your target destination.
    
    For example to change 'Test Link #1' to 'About Us' page, placed in site's
    root make the following changes to 'Test Link #1' action:
    
     Title: About Us 
     
     id: about_us URL: 
     
     string:${portal_url}/about-us
    
    2. To get links to look like orange buttons. In kupu, select text you want
    to be a link and assign either internal or external URL for your link.
    Once the link is set up, keep the text selected and choose **Orange
    button** in styles dropdown menu in the kupu toolbar. This will give you
    the orange button, linked to the destination you have chosen.
    
    3. To add a table with orange headers to your page, just add a regular
    table in kupu with "Table with orange headers" style.


Credits

    Andrey Lyashenko [drey.dex@gmail.com] - design
    
    Michael Krishtopa [theo@sed.lg.ua] - Plone theme for Plone 2.5
    
    Denys Mishunov [denys@jarn.com] - Plone theme for Plone 3.x
    
    Jarn AS [http://jarn.com] - wished to pay for this theme to be publicly available

