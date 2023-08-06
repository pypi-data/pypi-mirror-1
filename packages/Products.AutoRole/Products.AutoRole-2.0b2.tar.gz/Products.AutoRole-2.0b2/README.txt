===================
AutoRole PAS Plugin
===================
------------------------------------------------------------------------
Add roles to (anonymous or logged-in) visitors based on their IP address
------------------------------------------------------------------------

Introduction
============

The AutoRole plugin allows to assign roles to users from certain subnets.

There is an extraction and authentication plugin included, to enable
additional roles for anonymous users. This is required since PAS does
not support roles (or properties or groups) for anonymous users.
You can disable these interfaces if only logged-in users should get
additional roles.

AutoRole furthermore provides a groups plugin interface, allowing you to
assign groups instead of roles.

`IPRangePlugin`_ is similar but `logs in` users based on IP address.

.. _IPRangePlugin: http://dev.plone.org/collective/browser/PASPlugins/IPRangePlugin

Configuration
=============

The plugin is configured by editing the **IP filter and roles** property on
the plugins's Properties screen. Each line represent a mapping from IP
network to roles. The format is as follows:

``ip-address[/mask]: role[, role ...]``

If ``mask`` bits are omitted, 32 is assumed.

Proxies
=======

If your Zope server is hosted behind one or more proxies, be sure to list
them in the zope.conf file using the ``trusted-proxy`` directive. AutoRole
depends on Zope's HTTPRequest to extract the client IP address, and it, in
turn, uses the ``trusted-proxy`` directive to filter out proxy IP addresses.

Credits
=======

Copyright 2006 Norwegian Archive, Library and Museum Authority
(http://www.abm-utvikling.no)

Copyright 2008-2009 Jarn AS (http://www.jarn.com)

AutoRole 1.0 development was sponsored by the Norwegian Archive, Library and
Museum Authority

For technical questions contact Helge Tesdal at Jarn <info@jarn.com>.

License
=======

AutoRole is licensed under the GNU Lesser Generic Public License,
version 2.1. The complete license text can be found in file LICENSE.txt.
