# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages
# Nasty hack to make e.g. setup.py register read PKG-INFO as utf-8.. {{{
import sys
reload(sys) # setdefaultencoding is deleted in site.py..
sys.setdefaultencoding('utf-8')
# }}}

setup(
    name = "OortPub",
    version = "0.1",
    description = """An Oort-based, WSGI-enabled toolkit for creating RDF-driven web apps.""",
    long_description = """
    %s""" % "".join(open("README.txt")),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
    keywords = "toolkit rdf web wsgi",
    platforms = ["any"],
    author = "Niklas Lindström",
    author_email = "lindstream@gmail.com",
    license = "BSD",
    url = "http://oort.to/",
    #packages = find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    test_suite = 'nose.collector',
    install_requires = ['Oort >= 0.4',
                        'rdflib >= 2.4',
                        'Paste >= 1.0',
                        'PasteScript >= 1.0',
                        'Genshi >= 0.4'
                        'setuptools'],
    entry_points="""
        [paste.paster_create_template]
        oort_app=oort.util.paste_templates:OortAppTemplate
        """
    )

