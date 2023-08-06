Introduction
=============
This Yet-Another-Mechanize implementation aims to give the developper those new
features:

 - It can be proxified
 - It fakes user agent ``by default``
 - It does not handle robots ``by default``

It uses sys.prefix/etc/config.ini with a part [collective.anonymousbrowser] for its settings::

     [collective.anonymousbrowser]
     proxies=

This file is generated at the first run without proxies. It s your own to feed it with some open proxies.

Of course, it can take another configuration file, please see the __init__ method.

TODO
=====
- lxml integration, maybe steal z3c.etestbrowser

