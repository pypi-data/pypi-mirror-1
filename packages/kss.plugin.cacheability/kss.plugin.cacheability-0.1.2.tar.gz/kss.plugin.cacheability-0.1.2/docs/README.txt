
============================================
KSS plugin package "kss.plugin.cacheability"
============================================


Installation and Setup
======================

Read INSTALL.txt

Documentation
=============

This plugin enables to use cacheable (GET) KSS reguests.
This feature will be supported in the future directly
by kss.

Usage::

    css:event {
        action-client: cacheability-serverAction;
        cacheability-serverAction-url: actionName;
    }
 
The future syntax for this will be::
 
    css:event {
        action-server: actionName method(GET);
    }

 
Limitation
----------

Because currently the action runs as a client action in
the eyes of KSS, entire forms cannot be marshalled to the
server action. (kssSubmitForm, etc. does not work.)

