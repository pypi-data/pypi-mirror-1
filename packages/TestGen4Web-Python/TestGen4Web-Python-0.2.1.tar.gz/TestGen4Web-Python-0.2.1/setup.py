import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

setup(name="TestGen4Web-Python",
    version="0.2.1",
    description="A pure-python set of translators for TestGen4Web",
    author="Matt Harrison",
    author_email="mharrison@spikesource.com",
    maintainer="Duncan McGreggor",
    maintainer_email="oubiwann@adytum.us",
    url="http://dev.zenoss.org/trac/wiki/TestGen4Web-Python",
    license="MIT License",
    long_description="""TestGen4Web is a tool for recording user actions
        in a FireFox web browser, saving those actions to an XML file, 
        and playing them back.

        This package provides a means of translating
        TestGen4Web's recorded web browser sessions from XML to python. The
        package includes means for running tests as unit tests or simply
        generating python output that can be used in scripts, etc. 

        The work in this package is based on that originally done by Matt
        Harrison. However, all bugs and issues are new and solely the
        responsibility of the current maintainer.

        Release Information:
            http://dev.zenoss.org/trac/wiki/TestGen4Web-PythonReleaseNotes
        """,
    packages=[
        'testgen',
    ],
    install_requires = [
        "elementtree",
        "PDIS-XPath",
        "mechanize",
        "ClientCookie",
        #"ZopeTestbrowser", -- this cannot currently be run as an indpendent
        # package without throwing errors. To use support for zope.testbrowser,
        # you should have a recent Zope installed (>= 2.9.4) and have that
        # Zope's lib/python in your python path.
        "twill",
    ],
    scripts = ['bin/testgen-convert'],
    classifiers = [f.strip() for f in """
        Development Status :: 4 - Beta
        Environment :: Web Environment :: Mozilla
        Intended Audience :: Developers
        License :: OSI Approved :: MIT License
        Natural Language :: English
        Operating System :: OS Independent
        Programming Language :: Python
        Topic :: Internet :: WWW/HTTP :: Browsers
        Topic :: Software Development :: Testing
        Topic :: Software Development :: User Interfaces
        """.splitlines() if f.strip()],

)
