# -*- coding: utf-8 -*-
"""
This module contains the tool of p
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1.4.1'

long_description = (
    read('README.txt')
    + '\n' +
    read('docs', 'HISTORY.txt')
    + '\n' 
    )

tests_require=['zope.testing']

setup(name='humboldt.cmfbibliographyat',
      version=version,
      description="Humboldt University CMFBibliographyAT extensions",
      long_description=long_description,
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='Plone CMFBibliographyAT Bibliographies Zope',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/humboldt.cmfbibliographyat',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['humboldt', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'collective.monkeypatcher',
                        'collective.monkeypatcherpanel',
                        'Products.basesyndication',
                        'Products.fatsyndication',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'humboldt.cmfbibliographyat.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
