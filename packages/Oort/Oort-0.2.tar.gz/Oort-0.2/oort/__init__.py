# -*- coding: UTF-8 -*-
"""
========================================================================
Oort
========================================================================

Oort is a toolkit for creating RDF_-driven WSGI-compliant web applications.

The purpose of this is to make it easy to create web views of RDF Graphs by 
using some declarative python programming.

Oort uses RDFLib_, Paste_ and currently Kid_ for the heaving lifting. Initial 
support for `Template Plugins`_ alá Buffet and TurboGears is included (this
should remove the explicit Kid dependency).

.. _WSGI: http://wsgi.org
.. _RDF: http://www.rdfabout.net
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

How?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A couple of RdfQuerys::

    from oort.rdfview import *
    from myapp.ns import * # your own..

    class Node(RdfQuery):
        title = localized(DC)

    class SiteNode(Node):
        altTitle = localized(DC.alternative)
        relations = collection(SITE) >> Node
        nodeContent = localized_xml(SITE)

    class Person(RdfQuery):
        name = one (FOAF)
        knows = each(FOAF) >> THIS_QUERY

And a web application::

    from oort.sitebase import *
    from myapp import rdfqueries
    from myapp.ns import *

    class ExampleViewer(ResourceViewer):

        resourceBase = "http://example.org/oort/"
        langOrder = 'en', 'sv'

        class PlainWebDisplay(Display):
            name = "main"
            default = True
            outputMethod = 'xhtml'
            outputEncoding  = 'iso-8859-1'
            templateBase = "view/mainweb"
            globalQueries = {'languages': rdfqueries.sitelabels }
            aspects = [
                    Aspect(SITE.SiteNode, "sitenode.kid",
                            {'node': rdfqueries.SiteNode}) ,
                    Aspect(FOAF.Person, "person.kid",
                            {'person': rdfqueries.Person}) ,
                    Aspect(RDFS.Resource, "not_found.kid")
                ]

        class JsonDisplay(Display):
            name = "json"
            contentType = 'application/x-javascript'
            aspects = [
                    JsonAspect(SITE.SiteNode, {'node': sitenode.SiteNode})
                ]

But wait, there's more..

Paste!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Makes WSGI go down smoothly. ResourceViewers take RDFLib ``Graph`` instances in 
their constructors and becomes callables adhering to the spec.

.. TODO:
   To get started quickly, try::
   #
    $ paster create -t oort_app
    $ cd myapp/
    $ vim # edit and test..
    $ chmod u+x webapp.ini
    $ ./webapp.ini

Why?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because RDF is a formidable technology that could revolutionize the way 
information is treated and shared. Python and WSGI are exemplary technologies 
to use when building applications dealing with such data.

Why *Oort*?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* The Oort Cloud is a fascinating, alien phenomenon in a region *less 
  travelled*..
* Imagine all the BNodes in that cloud just waiting for an URI on the Web..
* "Output Of RDF through Templating"..
* a Dutch surname, so the way may be obvious to Oort..

-------------------

Copyright (c) 2006 Niklas Lindström

License: BSD-style <http://opensource.org/licenses/bsd-license>

"""

__docformat__ = 'reStructuredText en'
__author__ = "Niklas Lindström"

