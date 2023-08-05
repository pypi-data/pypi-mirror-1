import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

VERSION='0.2'
DESCRIPTION='Wrapper for www.nestoria.co.uk API'
LONG_DESCRIPTION='This module implements functions for harvesting data from www.nestoria.co.uk through the public API'

CLASSIFIERS = filter(None, map(str.strip,
"""
Intended Audience :: Developers
Programming Language :: Python
Topic :: Internet :: WWW/HTTP
""".splitlines()))

setup(
    name="nestoria",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license="GPL",
    classifiers=CLASSIFIERS,
    author="Nando Quintana",
    author_email="fquintana@codesyntax.com",
    url="http://www.nestoria.co.uk/help/api-tech",
    packages =['nestoria'],
    entry_points="""
    [nestoria.plugins]
    nestoria = nestoria.nestoria:Nestoria
    """,
    scripts = ['ez_setup.py'],
    platforms=['any'],
    install_requires="simplejson"
)
