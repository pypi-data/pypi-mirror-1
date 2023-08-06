:mod:`repoze.dvselect` Documentation
====================================

Overview
--------

:mod:`repoze.dvselect` provides a `WSGI`_ middleware component which reads
assertions set by :mod:`repoze.urispace` into the WSGI environment, and
uses them to select themes and rules for `Deliverance`_ based on the URI of
the request.

Because it reads the assertions created by the :mod:`repoze.urispace`
middleware, the :mod:`repoze.dvselect` middleware must be configured
"downstream" from the :mod:`repoze.urispace` middleware (i.e., nearer to
the application);  otherwise there will be no assertions to use.

Because it tweaks the WSGI environment, the :mod:`repoze.dvselect`
middleware must be configured "upstream" from the `Deliverance`_ middleware
/ proxy (i.e., nearer to the server);  otherwise Deliverance will have
already selected the theme / rules to use.

.. toctree::
   :maxdepth: 2

Example:  Using different theme / rules for sections of a site
--------------------------------------------------------------

This example assumes that the site being themed is something like a
newspaper site, where different "sections" have different layouts.

.. literalinclude:: etc/dv_news.xml
   :linenos:
   :language: xml

The purpose of this file is to compute two values (called "assertions" by
the `URISpace`_ spec) based on the request URI:

- the ``theme`` assertion is the URI to be used by `Deliverance`_ as the
  theme for this request.  It should be a URI for a static HTML page.  This
  example assumes that the theme pages are served from a separate
  server than the main application;  see the `Deliverance`_ docs for
  details about serving the theme from within the main application.

- the ``rules`` assertion is the URI to be used by `Deliverance`_ as the
  rules mapping the content onto the theme for this request.  It should be
  a URI for an XML document.  This example assumes that the rules are
  served from a separate server than the main application;  see the
  `Deliverance`_ docs for details about serving the theme from within the
  main application.


Prolog
++++++

- Line 1 is the stock XML prolog.

- Lines 2 - 5 define the root element (its element name is irrelevant to
  `URISpace`_) and the namespaces used in the document.  

- The ``uri:`` namespace defined in line 3 is the stock namespace for
  `URISpace`_.

- The ``uriext:`` namespace in line 4 is used for extensions defined
  by :mod:`repoze.urispce`:  this document uses the ``uriext:pathlast``
  extension element.

For details of the syntax of this file, please see the
`repoze.urispace docs <http://packages.python.org/repoze.urispace/>`_.

Default Assertions
++++++++++++++++++

Liens 9 and 10 define the default theme and rule assertions:  they will
be used if no other rule matches the request URI.

Assertions for Sections
+++++++++++++++++++++++

- Lines 11 - 22 are conditioned by a match on ``news`` as the first
  element of the path in the URI.
- Line 12 overrides the theme for requests in the ``news`` section.

- Lines 13 - 15 override the theme further, for items which are in the
  ``news/world`` subsection.  Likewise, lines 16 - 18 override it for the
  ``news/national`` subsection, and lines 19 - 21 for the ``news/local``
  subsection.

- Lines 24 - 26 are conditioned by a match on ``lifestye`` as the first
  element of the URI path;  they override the theme accordingly. 

- Lines 28 - 30 are conditioned by a match on ``sports`` as the first
  element of the URI path;  they override the theme accordingly. 

Note that none of these `URISpace`_ assertions override the ``rules``
assertion, which means that the default assertion applies.

Assertions for Pages
++++++++++++++++++++

- Lines 33 - 35 match URIs whose **last** path element matches the glob,
  ``*.html``:  they override the ``rules`` assertion, likely because the
  layout of the content resource is substantially different for stories.

- Lines 37 - 39 re-override the ``rules`` assertion for the pages whose
  last path element is ``index.html`` (the "section front").

Note that these last two matches vary the ``rules`` assertion independently
from the ``theme`` assertion, which will have been set by the earlier,
section-based matches.


Configuring :mod:`repoze.dvselect` via Paste
--------------------------------------------

To configure the middleware via a :mod:`Paste` config file, you can just
add it as a filter to the WSGI pipeline:  it doesn't require any separate
configuration.

You also need to configure the :mod:`repoze.urispace` middleware as a
filter, supplying the filename of the XML file defining the `URISpace`_
rules.  E.g., assuming we put the `URISpace`_ configuration from the example
above into the same directory as our Paste config file, and call it
``urispace.xml``, the filter configuration would be::

  [filter:urispace]
  use = egg:repoze.urispace#urispace
  urispace = %(here)/urispace.xml

Assuming that our Paste configuration defines a setup where the
`Deliverance`_ proxy is the application, we would configure it as::

  [app:deliverance]
  use = egg:Deliverance#proxy
  wrap_ref = http://example.com/
  theme_uri = http://static.example.com/themes/default.html
  rule_uri = http://static.example.com/rules/default.xml

We would then set up the pipline with the :mod:`repoze.urispace` filter
first in line, followed byt eh :mod:`repoze.dvselect` filter, followed by
the proxy::

  [pipeline:main]
  pipeline = 
    urispace
    egg:repoze.urispace#urispace
    deliverance


Configuring :mod:`repoze.dvselect` via Python
---------------------------------------------

Defining the same middleware via impertive python code would look something
like the following:

.. code-block:: python

   from deliverance.proxyapp import ProxyDeliveranceApp
   from repoze.dvselect import DeliveranceSelect
   from repoze.urispace.middleware import URISpaceMiddleware

   proxy = ProxyDeliveranceApp(
            theme_uri = 'http://static.example.com/themes/default.html',
            rule_uri = 'http://static.example.com/rules/default.xml',
            proxy = 'http://example.com/',
           )
   dvselect = DeliveranceSelect(proxy)
   urispace = URISpaceMiddleware(dvselect, 'file://etc/urispace.xml')

   application = urispace

This example builds the `WSGI`_ pipeline by composing the application
and the filters together via their constructors.


.. _WSGI: http://www.wsgi.org/
.. _URISpace: http://www.w3.org/TR/urispace.html
.. _Deliverance: http://www.coactivate.org/projects/deliverance/introduction
