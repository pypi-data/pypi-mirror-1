AutoRole

Copyright 2006 Norwegian Archive, Library and Museum Authority 
(http://www.abm-utvikling.no)

For technical questions, contact Helge Tesdal at Jarn <info@jarn.com>.

AutoRole enables you to give certain roles to users from certain subnets.

There is a extractor and authentication plugin included to enable
additional roles on Anonymous User. This is required since PAS does
not support roles (or properties and groups) for anonymous users.
You can disable these interfaces if only logged in users should get additional
roles.

The following blocks of IP addresses are allocated for private networks:

    * 10.0.0.0/8  (10.0.0.0 to 10.255.255.255)
    * 172.16.0.0/12  (172.16.0.0 to 172.31.255.255)
    * 192.168.0.0/16  (192.168.0.0 to 192.168.255.255)
    * 169.254.0.0/16  (169.254.0.0 to 169.254.255.255)*

*Note that 169.254.0.0/16 is a block of private IP addresses used for 
random self IP assignment where DHCP servers are not available.

IPRangePlugin is similar - but logs in users based on IP.
https://dev.plone.org/collective/browser/PASPlugins/IPRangePlugin

http://articles.techrepublic.com.com/5100-1035-6089187.html

Upstream proxies

  If your Zope server is hosted behind one or more proxies, be sure to list
  these in the zope.conf file, using the 'trusted-proxy' directive. AutoRole
  depends on Zope's HTTPRequest to parse out the client ip address from the
  request, and it in turn uses the trusted-proxy directives to filter out
  any proxy ip addresses.

Credits

  AutoRole development was sponsored by the Norwegian Archive, Library and
  Museum Authority 

License

  AutoRole is licensed under the GNU Lesser Generic Public License,
  version 2.1. The complete license text can be found in the
  LICENSE.txt file.
