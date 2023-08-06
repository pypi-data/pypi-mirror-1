# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.splashdancing
"""
import os
from setuptools import setup, find_packages
from xml.dom.minidom import parse


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def readversion():
    mdfile = os.path.join(os.path.dirname(__file__), 'collective', 'splashdancing', 
          'profiles', 'default', 'metadata.xml')
    metadata = parse(mdfile)
    assert metadata.documentElement.tagName == "metadata"
    return metadata.getElementsByTagName("version")[0].childNodes[0].data

# get version from metadata file
version=readversion().strip()

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('collective', 'splashdancing', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

tests_require=['zope.testing']

setup(name='collective.splashdancing',
      version=version,
      description="Adds pictures to newsitems in singing and dancing newsletters",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='news dancing pictures singing plone python newsletter',
      author='David Bain',
      author_email='david.bain@alteroo.com',
      url='http://themes.alteroo.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        'collective.dancing',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'collective.splashdancing.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      [distutils.setup_keywords]
      #paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
#      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
#      paster_plugins = ["ZopeSkel"],
      )
