=============================
 Vice: plone.app.syndication
=============================

This package is the Plone layer of the outbound portion of the Vice 
syndication framework. It runs on Plone 3.0.

This package builds upon vice.outbound, which provides a
non-Plone-specific framework for outbound syndication in Zope. See the
README.txt in that package for general information about extending the
application of the framework.

This package provides three formats: Atom 1.0, RSS 1.0, and RSS 2.0. It 
provides adapters for all the Plone 3.0 AT content types, adapting them
to be feeds or feed entries, as appropriate. It also provides a Plone 
configuration UI - both a configlet that plugs into the control panel
for global configuration and an action that enables per-container configuration
of named feeds. There is no longer any need to go to the ZMI to configure
outbound syndication! All setting are now available directly in Plone and, 
indeed, changing settings on the syndication_tool in the ZMI will have *no* 
effect on Vice. 

Installation is done using GenericSetup - just select 'Outbound Syndication 
(Vice)' when adding a new Plone site from the ZMI, once you have added slugs 
forthis package, vice.outbound, and five.intid in the 
etc/packages-include/ of your Zope instance. This package also includes 
migration for syndication settings in Plone 3.0 and before; however, if you 
currently have a different third-party syndication product installed, results 
of migration are unknown, as the Vice migation hasn't been tested in 
combination with any other third-party products.

Credits

This work was funded both by Google through Plone for the Summer of Code 2007 
and by the Georgia Institute of Technology.