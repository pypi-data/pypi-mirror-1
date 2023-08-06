# -*- coding: utf-8 -*-
"""
This module contains the tool of aws.minisite
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

from xml.dom import minidom

metadata_file = os.path.join(os.path.dirname(__file__),
                             'aws', 'minisite',
                             'profiles', 'default', 'metadata.xml')
metadata = minidom.parse(metadata_file)
version = metadata.getElementsByTagName("version")[0].childNodes[0].nodeValue
version = str(version).strip()

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    )

tests_require=['zope.testing']

setup(name='aws.minisite',
      version=version,
      description="Minimal sites for Plone",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='Plone MiniSites',
      author='Alter Way Solutions',
      author_email='support@ingeniweb.com',
      url='https://ingeniweb.svn.sourceforge.net/svnroot/ingeniweb/aws.ministe/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['aws', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'collective.phantasy>=1.0',
                        'Products.FCKeditor>=2.6.5.1',
                        'collective.uploadify>=0.9',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'aws.minisite.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
