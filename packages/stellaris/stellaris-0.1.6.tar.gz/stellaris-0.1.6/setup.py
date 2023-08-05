# Install stellaris
# -*- coding: latin-1 -*-

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import os.path

from stellaris import __version__, __date__

setup(
    name = "stellaris",
    version = __version__,
    include_package_data = True,
    description = "Stellaris is a metadata management service.",
    author = "Mikael Hoegqvist",
    author_email = "hoegqvist@zib.de",
    maintainer = "Mikael Hoegqvist",
    maintainer_email = "hoegqvist@zib.de",
    url = "http://stellaris.zib.de/",
    scripts = [os.path.join("utils", "stellaris")],
    dependency_links = ["http://bitworking.org/projects/httplib2/dist/", "http://rdflib.net/rdflib-2.4.0.tar.gz"],
    install_requires = [
        "rdflib >= 2.4.0", 
        "simplejson >= 1.4", 
        "httplib2 >= 0.3.0", 
        "selector >= 0.8.11", 
        "kid >= 0.9.4", 
        "M2Crypto >= 0.17",
        "benri >= 0.0.1"
        ],
#    package_data = {'':['etc/*.cfg']},
    #exclude_package_data = {'test':['data/*', 'benchmark/*', 'cert/*']},
    
    package_data = {'etc':['*.cfg'], 'templates': ['*.html'], 'static': ['*.js', '*.xsl', '*.css', '*.html']},
    platforms = ["any"],
    classifiers = ["Programming Language :: Python", 
                   "Development Status :: 4 - Beta", 
                   "Operating System :: POSIX", "Topic :: Database :: Database Engines/Servers", 
                   "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"],
    long_description = """Stellaris is a metadata management service developed within the AstroGrid-D project. Our focus is to provide a flexible way to store and query metadata relevant for e-science and grid-computing. This can range from resource description of grid resources (compute clusters, robotic telescopes, etc.) to application specific job metadata or dataset annotations. We use common web-standards such as RDF to describe metadata and the accompanying query language SPARQL. Some features of the software include:

    * A simple but powerful management interface for RDF-graphs
    * Different backends for persistence through the use of RDFLib and Virtuoso
    * Authorization and authentication based on X.509-certificates
    * Supports different ways of VO-based authorization such as VOMRS
    * SPARQL-protocol implementation with both XML/JSON result formats
""",
    zip_safe = False,
    packages = find_packages(),
)
