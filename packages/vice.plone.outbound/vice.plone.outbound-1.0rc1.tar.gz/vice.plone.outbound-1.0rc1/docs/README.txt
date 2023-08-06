===================
vice.plone.outbound
===================

.. contents::

What is it?
===========

vice.plone.outbound provides Plone with the ability to syndicate web
feeds (rss, atom, etc). It is configurable by users and extensible by
developers.

Plone requirement: version 3.1

Features
========

vice.plone.outbound gives you outbound syndication for all "out of the
box" Archetype Content Types (ATCT) and subclasses.  Any folder (including
the site root) can be configured with any number of feeds.  This can
be used to provide granular or bulk content feeds in multiple formats.

Any feed can be set as recursive or not.  A recursive feed will
include all the content at the feeds location as well as any
sub-folders content and so on.  A non-recursive feed will only
syndicate the content directly present at the level of the feed.

Auto discover can be set on any feed.  This will enable modern
aggregators and browsers to "sense" the feeds location by simply
providing the URL for the feed folder.  NB only one feed per any
folder (location) should be configured with auto discover on.

Users may also include a "Published URL" on any feed.  This will
enable site managers to easily route all traffic through services like
"feedburner", by first registering the local syndicated feed with
feedburner, and then entering the respective feedburner URL as the
"Published URL" for the feed.

Enabling or disabling feeds can be done for the whole site (see the
add-on product configuration for "Syndication (Outbound)" in the Plone
control panel), on any folder, or each feed itself.

There are global and per folder configuration options for the maximum
number of items to be syndicated from any respective feed as well.
The most recent added or modified date is used to sort all feed
content.

Installation instructions are in INSTALL.txt.
