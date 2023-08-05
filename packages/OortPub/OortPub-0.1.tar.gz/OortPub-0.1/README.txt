========================================================================
OortPub
========================================================================

OortPub is a toolkit for creating RDF_-driven WSGI_-compliant web applications.

The purpose of this is to make it easy to create web views of RDF Graphs by 
using some declarative python programming.

OortPub uses RDFLib_, Paste_ and Genshi_ for the heaving lifting.

.. _RDF: http://www.rdfabout.net
.. _WSGI: http://wsgi.org
.. _RDFLib: http://rdflib.net
.. _Paste: http://pythonpaste.org
.. _Genshi: http://genshi.edgewall.org/

The RDF-to-objects facility comes from the Oort_ core package, released 
separately.

.. _Oort: http://www.python.org/pypi/Oort/

Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main package is:

``oort.sitebase``
    Contains classes used for declarative definitions of *displays*, used for 
    matching resources and rendering a particular output (html, json etc.). By 
    defining *aspects*, the type (or super-type) of a selected resource is 
    mapped to a particular RdfQuery and an associated template.

    One or more displays are put in the context of a *resource viewer*, which 
    becomes a WSGI application ready to mount in your WSGI environment.

How?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Loads of RDF data like::

    <site/main> a :SiteNode;
        dc:title "Main Page"@en, "Huvudsida"@sv;
        dc:altTitle "Main", "Hem"@sv;
        :relations (
            <site/faq>
            <site/about>
        );
        :nodeContent '''<h1 xml:lang="en">Welcome</h1>'''^^rdfs:XMLLiteral,
                     '''<h1 xml:lang="sv">V&#195;&#164;lkommen</h1>'''^^rdfs:XMLLiteral .

    <persons/someone> a foaf:Person;
        foaf:name "Some One";
        foaf:knows <otherone> .

A couple of RdfQuerys::

    from oort.rdfview import *
    SITE = Namespace("http://example.org/ns/2007/website#")

    class Titled(RdfQuery):
        title = localized(DC)
        altTitle = localized(DC.alternative)

    class SiteNode(Titled):
        relations = collection(SITE) >> Titled
        nodeContent = localized_xml(SITE)

    class Person(RdfQuery):
        name = one(FOAF)
        knows = each(FOAF) >> 'Person'

And a web application::

    from oort.sitebase import *
    from myapp import queries
    from myapp.ns import SITE

    class ExampleViewer(ResourceViewer):

        resourceBase = "http://example.org/oort/"
        langOrder = 'en', 'sv'

        class PlainWebDisplay(Display):
            name = "main"
            default = True
            outputMethod = 'xhtml'
            outputEncoding  = 'iso-8859-1'
            templateBase = "view/mainweb"
            globalQueries = {'languages': queries.sitelabels }
            aspects = [
                    Aspect(SITE.SiteNode, "sitenode.xhtml",
                            {'node': queries.SiteNode}) ,
                    Aspect(FOAF.Person, "person.xhtml",
                            {'person': queries.Person}) ,
                    Aspect(RDFS.Resource, "not_found.xhtml")
                ]

        class JsonDisplay(Display):
            name = "json"
            contentType = 'application/x-javascript'
            aspects = [
                    JsonAspect(SITE.SiteNode, {'node': queries.SiteNode})
                ]

But wait, there's more..

Paste!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Makes WSGI go down smoothly. ResourceViewers take RDFLib ``Graph`` instances in 
their constructors and become callables adhering to the spec.

To get started quickly, run::

    $ paster create -t oort_app
    ... fill in desired values in the dialogue
    $ cd myapp/
    $ vim # edit and test..
    $ chmod u+x webapp.ini
    $ ./webapp.ini

Why?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because RDF is a formidable technology that could revolutionize the way 
information is treated and shared. Python and WSGI are exemplary technologies 
to use when building applications dealing with such data.

