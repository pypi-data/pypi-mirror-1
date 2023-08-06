Introduction
============

collective.sylvester (Sylvester for short) is a twitter client for Plone. It 
aims to make tweeting and twitter account management available from within a 
Plone site.

Overview
========
Sylvester has a pluggable dashboard. All other views are loaded via ajax into 
the dashboard.

These pages are currently available:
    - The main feed. Eerily similar to the homepage on twitter.com.
    - Friends page. Shows people your are following as tiled portlets.
    - Replies. Shows messages where you are mentioned.

These actions are currently available:
    - Publish to twitter. Tweet about Plone content on twitter. The URL is 
      shortened by tinyurl.com.
    - A "Twitter Dashboard" link appears in your personal bar.

Requirements
============
Plone > 3.1

Installation
============
In your buildout.cfg add 'collective.sylvester' to the eggs and zcml sections.

Then ./bin/buildout -Nv, restart Zope.

Run the collective.sylvester profile in portal_setup.

Architecture
============
Everything is Zope Component Architecture aware. All DOM CSS classes and node 
ids are qualified so theming through Deliverance should be possible.

Twitter authentication information is retrieved in three ways and is extensible 
through the use of adapters.
    - Credentials are stored on the session. The user is challenged with a
      twitter login screen. This method allows people who are not members of 
      the Plone site to use twitter.
    - Credentials are stored in fields on the member called twitterUsername 
      and twitterPassword. These fields must be added through 
      portal_memberdata/manage_propertiesForm.
    - Credentials are stored as remember fields. The expected fieldnames are
      twitterUsername and twitterPassword. for this to work you must enable 
      remember.zcml by removing comments in configure.zcml.

To be expanded
