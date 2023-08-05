from setuptools import setup, find_packages
from ConfigParser import ConfigParser

config = ConfigParser()
config.read('setup.cfg')

NAME = config.get('setup', 'name')
VERSION = config.get('setup', 'version')
DESCRIPTION = config.get('setup', 'description')
LONG_DESCRIPTION = '''
zinspect
========

Inspects objects/classes to enforce that they respect the zope.interface
they declare to implement/provide. It works with zope.interfaces.

Examples
--------

the unit tests provided with the source package contain a lot of examples
of how to use the package to validate objects and classes.

Discussion
----------

I have written this package mainly out of a specific need for ensuring that
plugins I load into my application would always implement the interfaces they
declared to implement. This is a way to ensure that the application using the
plugin won't encounter an exception trying to access an attribute that should
be present but is not.

Status
------
The package is in its early infancy and will not detect an attribute
that is created outside the __init__ method or not present directly on the
class itself. This could be added in the future if there is enough demand.
'''
AUTHOR = config.get('setup', 'author')
AUTHOR_EMAIL = config.get('setup', 'author_email')
URL = config.get('setup', 'url')
LICENSE = config.get('setup', 'license')
COPYRIGHT = config.get('setup', 'copyright')
COMPANY = config.get('setup', 'company')

download_url = "http://cheeseshop.python.org/packages/2.5/"
download_url += "z/%(name)s/%(name)s-%(version)s-py2.5.egg" % dict(
    name=NAME, version=VERSION)

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=download_url,
    install_requires=["zope.interface>=3.3.0b1"],
    license=LICENSE,
    zip_safe=False,
    packages=find_packages(exclude=['ez_setup', 'tests']),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite = 'nose.collector',
)

# vim: expandtab tabstop=4 shiftwidth=4:
