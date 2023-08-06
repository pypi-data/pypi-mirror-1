:mod:`repoze.dvselect` Documentation
====================================

This package provides middleware whic uses :mod:`repoze.urispace` to select
`Deliverance <http://www.coactivate.org/projects/deliverance/introduction>`_
themes and rules based on the URI of the request.


.. toctree::
   :maxdepth: 2


Configuring :mod:`repoze.dvselect` via Paste
--------------------------------------------

:mod:`repoze.dvselect` provides a component which serves as
`WSGI <http://www.wsgi.org/>`_ middleware:  it sets values into the
WSGI environment which influence the selection of the theme and rules
used by deliverance.  To configure the middleware via a :mod:`Paste`
config file, specify it as a filter.  You also need to configure the
:mod:`repoze.urispace` middleware as a filter, supplying the filename of the
XML file defining the `URISpace`_ rules.  E.g.::

  [filter:urispace]
  use = egg:repoze.urispace#urispace
  urispace = %(here)/urispace.xml

  [filter:dvselect]
  use = egg:repoze.dvselect#main

Because it tweaks the WSGI environment on ingress, the :mod:`repoze.dvselect`
middleware must be configured "upstream" (nearer to the server) of the
Deliverance middleware / proxy.  Because it reads the assertions created by
the :mod:`repoze.urispace` middleware, the :mod:`repoze.dvselect` middleware
must be configured "downstream" (nearer to the application) of the
:mod:`repoze.urispace` middleware.  E.g.::

  [app:deliverance]
  use = egg:Deliverance#proxy
  wrap_ref = http://example.com/
  theme_uri = http://dv.example.com/simple.html
  rule_uri = http://dv.example.com/rules.xml

  [pipeline:main]
  pipeline = 
    urispace
    dvselect
    deliverance


.. _URISpace: http://www.w3.org/TR/urispace.html
