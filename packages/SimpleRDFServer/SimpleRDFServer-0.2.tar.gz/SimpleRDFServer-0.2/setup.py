from setuptools import setup, find_packages
setup(
    name = "SimpleRDFServer",
    version = "0.2",
    packages = find_packages(),
    scripts = ['SimpleRDFServer.py'],
    url = "http://winningham.googlepages.com/simplerdfserver",
    author = "Thomas",
    author_email = "winningham@gmail.com",
description = "Serves RDF (RSS 1.0) indexes of directories over HTTP",
long_description = "An underwhelming overridden version of the standard SimpleHTTPServer.py file from the standard Python modules (version 2.4.2), to produce RDF representations of directory listings. Subdirectories work as expected. Security (of any kind) is not implemented here. Run the test() command found in this file, and you'll start serving RDF of the current working directory over HTTP on port 8000. See the Python documentation for SimpleHTTPServer for the general idea. Work is ongoing! Thanks for downloading!",
    license = "LGPL",
    keywords = "rdf http index file directory server rss triples namespace semantic web",
    classifiers = [
     'Development Status :: 2 - Pre-Alpha',
     'Environment :: Console',
     'Environment :: No Input/Output (Daemon)',
     'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
     'Natural Language :: English',
     'Operating System :: OS Independent',
     'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
     'Topic :: Text Processing :: Markup :: XML'
    ]
)
