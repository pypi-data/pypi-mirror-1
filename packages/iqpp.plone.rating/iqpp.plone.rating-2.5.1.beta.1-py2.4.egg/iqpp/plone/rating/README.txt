iqpp.plone.rating is a rating system for Plone.

Features

    * Authenticated and anonymous rating
    * Changeable score cards
    * Star and selection based rating form (adjustable)
    * Global and Local options
    * Portlet: most active rating (daily and always)
    * View: All rated objects
    * View: All ratings for an object
    * Ajax (via KSS with fallback)
    * Pluggable
    
Installation

    1. Extract the tarball and put the iqpp directory in <instance>/lib/python
    2. Put the .zcml files into <instance>/etc/package-includes
    3. Restart Zope
    4. Go to the quickinstaller and install iqpp.plone.rating
    5. Go to "manage portlets" and add a rating and/or most active ratings 
       portlet.
    6. Optionally go to site setup/rating and change your options

Installation via buildout (recommended)

    Alternatively, just add the following lines within the [instance]-section 
    of your buildout

    eggs =
        iqpp.plone.rating 

    zcml =
        iqpp.plone.rating

    After re-run your buildout process steps 3-6 above.

    You can find the egg in the Cheese Shop:
        * http://pypi.python.org/pypi/iqpp.plone.rating
    
Credits

  * Jan Ulrich Hasecke (jan.ulrich@hasecke.com) German translation, ideas and 
    bug hunting)
  * The rating icon is from Mark James' Silk icon set 1.3
    (http://www.famfamfam.com/lab/icons/silk/)
  * The star rating is based on CSS Star Rating Redux
    (http://komodomedia.com/blog/index.php/2007/01/20/css-star-rating-redux/)