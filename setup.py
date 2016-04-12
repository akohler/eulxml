"""Setup.py for eulxml package"""
#!/usr/bin/env python
from distutils.command.build_py import build_py
from distutils.core import Command
from distutils.command.clean import clean
import os
import sys
import glob
from setuptools import setup, find_packages
import shutil
import eulxml

class GenerateXmlCatalog(Command):
    '''Setup command to generate fresh catalog and schemas'''
    def run(self):
        # importing this forces ply to generate parsetab/lextab
        from eulxml.catalog import download_schemas, generate_catalog
        download_schemas()
        generate_catalog()


class CleanSchemaData(clean):
    """Custom cleanup command to delete build and schema files"""
    description = "Extended clean command to remove schema files and XML catalog"

    def run(self):
        # remove schema data and then do any other normal cleaning
        try:
            shutil.rmtree('eulxml/schema_data')  # FIXME: should be a variable
        except OSError:
            pass
        clean.run(self)


def grab_xsd_xml():
    """Grab all xml and xsd file in schema_data directory """
    types = ('*.xml', '*.xsd')
    grab_files = []
    for schema_file in types:
        grab_files.extend(glob.glob(schema_file))

    return grab_files


# getting catalog files
def get_catalog_files():
    """Check if the catalog exists and import xml files into data files """
    if not os.path.exists('eulxml/schema_data/catalog.xml'):
        from eulxml.catalog import download_schemas, generate_catalog, XSD_SCHEMAS
        print "There is no catalog. :("
        counter = 0
        for fname in XSD_SCHEMAS:
            if os.path.isfile("eulxml/schema_data/" + fname.split('/')[-1]):
                counter += 1

        print "Do we need to download schemas?"
        if counter != len(XSD_SCHEMAS):
            print "yes, we do. Downloading..."
            download_schemas()

        print "Generating catalog..."
        generate_catalog()
    else:
        print "Found one!"
    return grab_xsd_xml()

schema_files = get_catalog_files()

class build_py_with_ply(build_py):
    '''Use ply to generate parsetab and lextab modules.'''

    def run(self, *args, **kwargs):
        # importing this forces ply to generate parsetab/lextab
        import eulxml.xpath.core
        build_py.run(self, *args, **kwargs)

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Text Processing :: Markup :: XML',
]

LONG_DESCRIPTION = None
try:
    # read the description if it's there
    with open('README.rst') as desc_f:
        LONG_DESCRIPTION = desc_f.read()
except:
    pass

dev_requirements = [
    'sphinx>=1.3.5',
    'coverage',
    'Django<1.9',
    'rdflib>=3.0',
    'mock',
    'nose',
    'tox',
]
# NOTE: dev requirements should be duplicated in pip-dev-req.txt
# for generating documentation on readthedocs.org

# unittest2 should only be included for py2.6
if sys.version_info < (2, 7):
    dev_requirements.append('unittest2')


setup(
    cmdclass={
        'build_py': build_py_with_ply,
        'clean': CleanSchemaData,
        'xmlcatalog': GenerateXmlCatalog
    },

    name='eulxml',
    version=eulxml.__version__,
    author='Emory University Libraries',
    author_email='libsysdev-l@listserv.cc.emory.edu',
    url='https://github.com/emory-libraries/eulxml',
    license='Apache License, Version 2.0',
    packages=find_packages(),

    setup_requires=[
        'ply>=3.8',
    ],
    install_requires=[
        'ply',
        'lxml',
        'six>=1.10',
    ],
    extras_require={
        'django': ['Django<1.9'],
        'rdf': ['rdflib>=3.0'],
        'dev': dev_requirements
    },
    data_files=schema_files,
    description='XPath-based XML data binding, with Django form support',
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
)
