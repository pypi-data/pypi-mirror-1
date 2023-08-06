Introduction
============

    GeoXml content stores kml (Keyhole Markup Language), the view renders the
    file in a Google Map (as EGeoXml object from egeoxml library).

    To work with Plone I have used the egeoxml.js library that permits to
    download kml file from any location (GGeoXml works only with file hosted
    on a publicly accessible web server)

    GeoXml depends on Maps for the configuration of Google apikey (but you can
    modify the view.pt file to use a static apikey and remove Maps)

Installation
============

    Create a Plone site with GeoXml and Maps profile or import these profiles
    from portal_setup.

Dependencies
============

    Plone 3.1.x
    Maps (http://svn.plone.org/svn/collective/Products.Maps/trunk)


Credits
=======

    egeoxml.js by Mike Williams, http://econym.googlepages.com/egeoxml.htm
    Maps by Jarn, http://plone.org/products/maps
