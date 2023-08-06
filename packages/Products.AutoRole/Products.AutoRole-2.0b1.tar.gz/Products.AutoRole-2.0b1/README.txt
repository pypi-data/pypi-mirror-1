===================
AutoRole PAS Plugin
===================
------------------------------------------------------------------------
Add roles to (anonymous or logged-in) visitors based on their IP address
------------------------------------------------------------------------

Introduction
============

AutoRole allows you to assign certain roles to users from certain subnets.

There is an extractor and authentication plugin included to enable
additional roles for anonymous users. This is required since PAS does
not support roles (or properties and groups) for anonymous users.
You can disable these interfaces if only logged-in users should get
additional roles.

We also provide a groups plugin interface, to assign groups instead
of roles.

`IPRangePlugin`_ is similar but `logs in` users based on IP address.

.. _IPRangePlugin: http://dev.plone.org/collective/browser/PASPlugins/IPRangePlugin

Upstream Proxies
================

If your Zope server is hosted behind one or more proxies, be sure to list
these in the zope.conf file, using the ``trusted-proxy`` directive. AutoRole
depends on Zope's HTTPRequest to parse out the client IP address, and it in
turn uses the ``trusted-proxy`` directive to filter out proxy IP addresses.

Credits
=======

Copyright 2006 Norwegian Archive, Library and Museum Authority
(http://www.abm-utvikling.no)

Copyright 2009 Jarn AS (http://www.jarn.com)

AutoRole development was sponsored by the Norwegian Archive, Library and
Museum Authority

For technical questions, contact Helge Tesdal at Jarn <info@jarn.com>.

License
=======

AutoRole is licensed under the GNU Lesser Generic Public License,
version 2.1. The complete license text can be found in file LICENSE.txt.

