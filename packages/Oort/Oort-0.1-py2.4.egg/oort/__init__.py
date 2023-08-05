# -*- coding: UTF-8 -*-
"""
========================================================================
Oort
========================================================================

A WSGI_-enabled toolkit for creating RDF-driven web apps.

The purpose of this toolkit is to make it easy to create web views of 
RDF Graphs by using some declarative python programming.

Oort Uses RDFLib_, Paste_ and currently Kid_ for the heaving lifting. Initial 
support for `Template Plugins`_ alá Buffet and TurboGears is included (this
should remove the Kid dependency).

.. _WSGI: http://wsgi.org
.. _RDF: http://rdfabout.org
.. _RDFLib: http://rdflib.net
.. _Paste: http://pythonpaste.org
.. _Kid: http://kid-templating.org
.. _`Template Plugins`: http://www.turbogears.org/docs/plugins/template.html

Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are the main packages:

``oort.sitebase``
    Contains classes used for declarative definitions of *displays*, used for 
    matching resources and rendering a particular output (html, json etc.). By 
    defining *aspects*, the type (or super-type) of a selected resource is 
    mapped to a particular RdfQuery and an associated template.

    One or more displays are put in the context of a *resource viewer*, which 
    becomes a WSGI application ready to mount in your WSGI environment.

``oort.rdfview``
    Contains classes and functions used for defining RDF queries and selectors, 
    i.e. declarations used to pick properties and associated sub-queries from a
    chosen resource (similar to how many ORM-toolkits work).

Why?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because RDF is a formidable technology that could revolutionize the way 
information is treated and shared. Python and WSGI are exemplary technologies 
to use when building applications dealing with such data.

Why *Oort*?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* The Oort Cloud is a fascinating, alien phenomenon..
* Imagine all the BNodes in that cloud just waiting for an URI on the Web..
* OORT - "Output Of RDF through Templating"..

-------------------

Copyright (c) 2006 Niklas Lindström

License: BSD-style <http://opensource.org/licenses/bsd-license>

"""

__docformat__ = 'reStructuredText en'
__author__ = "Niklas Lindström"

