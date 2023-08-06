Zoner - A DNS zone management UI
================================

Overview
--------

Zoner is a web application to make management of DNS zone files simple and easy.
The authoritative copy of each domain remains in the original zone file,
which Zoner reads & writes as needed, as opposed to storing domain details
in a database.  This means that zone files can still be edited manually
and Zoner will pick up the changes as necessary.

Zoner features:

* Domain details remain in original zone files, not in a database.
* Zoner reads & writes actual zone files, which can also be safely
  modified outside of Zoner.
* Zone serial numbers are incremented automatically when changes are made.
* Zoner can signal bind to reload a zone, via rndc.
* An audit of all zone changes is maintained for each domain.  Any previous
  version of a zone file can be inspected and zones can be rolled back to
  any previous version.

Requirements:

* Zoner is a Python application built with the TurboGears framework.  Both
  Python and TurboGears (version 1.x) are required.
* Zoner requires the easyzone and dnspython Python packages for DNS/zone management.
* Zoner also requires SQLAlchemy, TGBooleanFormWidget and TGExpandingFormWidget Python packages.

(All dependencies should be installed automatically if using setuptools, which will usually be the case for a properly installed TurboGears environment.)


Installation
------------

The easiest way to install Zoner is by using setuptools::

    $ easy_install zoner

Alternatively, install TurboGears then download the Zoner package
from http://pypi.python.org/pypi/zoner/ and install with::

    $ python setup.py install

Create a config file.  A template sample-prod.cfg file is included
with the package (or installed alongside the package).  Example::
    
    $ cp /usr/lib/python2.4/site-packages/zoner-1.3.1-py2.4.egg/config/sample-prod.cfg zoner.cfg

Customise the config file, then initialise the database::

    $ tg-admin sql create

Next, create a user to login to the Zoner application with::

    $ zoner_users -c zoner.cfg add

Finally, start the Zoner application::

    $ zoner zoner.cfg

Point your browser at http://localhost:8080/ (or the appropriate host/port
as per your configuration) and you should be able to login.


Apache Proxy
------------

It is a common requirement to proxy this application behind an Apache
hosted secure address.  For example, let's say this application is
listening locally on http://127.0.0.1:8080/ and Apache needs to
proxy all requests to it from https://my.host.name/zoner/

Here is a sample of the Apache configuration (excluding all the
directives not relevant to this example)::

  <VirtualHost _default_:443>
    #### Proxy Requests to Zoner under /zoner/
    ProxyRequests Off
    ProxyPass /zoner/ http://127.0.0.1:8080/
    ProxyPassReverse /zoner/ http://127.0.0.1:8080/
  </VirtualHost>

In your application config (dev.cfg or prod.cfg) you will want to
add the following::

  [global]
  server.webpath="/zoner"

That should be all that is required.

