Zest emailhider
===============

This document describes the zest.emailhider package.


Dependencies
------------

This package depends on kss.plugin.cacheability to use GET requests instead of
POST.


Overview
--------

This package provides a mechanism to hide email addresses with KSS. Objects 
display a placeholder link with a 'hidden-email' class and a 'uid' kss 
attribute set to the UID of a user; a KSS click action is bound to the link 
which replaces it with a 'mailto' link directed at the email address of the 
user. Using this mechanism the email address isn't visible in the initial page 
load, and it requires JavaScript to be seen - so it's much harder for spammers
to harvest.

Object are marked with the IMailable interface - this states that they can 
provide uid and email attributes. The 'emailhider' view is provided to 
generate the placeholder link.

Note: For publicly viewable email address, KSS must be made publicly 
accessible.
