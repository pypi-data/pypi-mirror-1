Overview
========

Experimental performance improvements to content creation for Plone. Primarily
this works by trying to ensure that portal factory does not cause writes to the
zodb, via making archetypes content portal factory aware such that they do not
attempt to register themselves in various global catalogs.


This issue is being tracked by Plone at the following URL. 
https://dev.plone.org/plone/ticket/9672

This patch is for intended for existing versions of Plone (2x & 3x) to address 
this issue.
