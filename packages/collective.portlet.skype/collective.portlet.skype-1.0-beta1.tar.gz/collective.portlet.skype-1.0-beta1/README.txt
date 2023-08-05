========================
collective.portlet.skype
========================

Introduction
============

A Plone 3 style portlet to show skype contacts with an status icon. By default
skype names are fetched from the user-profiles of available users. We assume a 
property 'skype' here. This module does not provide it. 

State
=====

BETA At this time its all code in progress, it works, but bugs might be left. 
Also a sane caching is not implemented now.

Usage
=====

This is a python module made with zopes component architecture and using plones 
infrastructure. 

You need to include it in you buildouts eggs and zcml sections. To make it 
available in Plone you need to assign it to a portlet-manager. This is usally
done in your profiles *portlets.xml* file. consult the Plone documentation for 
details. In your profile also add 
*++resource++collective.portlet.skype.javascript* to portal_javascript registry.

By default the portlet takes all available users and check if they have one of 
the properties: skype, skypeid, skype_id. You can overrule this behaviour by 
writing an own class implementing ISkypeNameFetcher and register it for your 
needs.

Once registered and setup for your site jsut go to your portlet-manager and add 
a sykpe portlet.

Feedback, Bugreports, ...
=========================

If you like to give the author feedback about this product just write a mail
to <dev@bluedynamics.com>.

If you have access to the *plone.org* *collective* you might want to commit 
bug-fixes direct to trunk or do enhancements on a branch. Anyway, the author 
would be happy to get a short mail about those changes.

-- Jens Klein, IRC: jensens, skype:yenzenz, mail <jens@bluedynamics.com>