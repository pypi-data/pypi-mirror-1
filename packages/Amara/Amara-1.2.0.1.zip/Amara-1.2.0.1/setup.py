#!/usr/bin/env python
import os
try:
    # Allow Ft.Lib.DistExt to be used even in setuptools is installed.
    if 'AMARA_FTSETUP' in os.environ:
        raise ImportError
    from setuptools import setup, find_packages
    kw = {
          'install_requires': ['4Suite-XML>=1.0.2', 'python-dateutil'],
           'entry_points': {
               'console_scripts': [
                  'scimitar = amara.scimitar:main',
                  'flextyper = amara.flextyper:main',
                  'trimxml = amara.trimxml:main',
                  ],
               },
          }
except ImportError:
    from Ft.Lib.DistExt import *
    kw = {'download_url': 'ftp://ftp.4suite.org/pub/Amara/',
          'license_file': 'COPYING',
          'scripts': [Script('scimitar', 'amara.scimitar', function='main'),
                      Script('flextyper', 'amara.flextyper', function='main'),
                      Script('trimxml', 'amara.trimxml', function='main'),
                      ],
          'doc_files': [File('ACKNOWLEDGEMENTS'),
                        File('CHANGES'),
                        File('COPYING'),
                        File('TODO'),
                        File('docs/quickref.txt'),
                        Document('docs/manual.xml', 'docbook', title='Users Manual'),
                        ],
          'devel_files': [FileList('tests/bindery', ['test/bindery'], recursive=True),
                          FileList('tests/domtools', ['test/domtools'], recursive=True),
                          FileList('tests/scimitar', ['test/scimitar'], recursive=True),
                          ],
          'config_module': 'amara.__config__',
          'manifest_templates': ['include demo/README',
                                 'recursive-include demo *.py *.xml *.rdf *.rng *.conf',
                                 'recursive-include test *.py',
                                 ],
          'validate_templates': ['prune Amara.egg-info',
                                 'exclude MANIFEST.in',
                                 ],

          }

setup(name='Amara',
      version='1.2.0.1',
      description="Amara XML Toolkit: a collection of Python/XML processing tools to complement 4Suite (http://4Suite.org)",
      long_description="A collection of Python/XML processing tools to complement 4Suite (http://4Suite.org).  The components are: Bindery--a data binding tool (fancy way of saying it's a very Pythonic XML API); Scimitar--an implementation of the ISO Schematron schema language for XML, which converts Schematron files to Python scripts; domtools--A set of tools to augment Python DOMs; saxtools--A set of tools to make SAX easier to use in Python",
      url='http://uche.ogbuji.net/tech/4suite/amara/',
      author='Uche Ogbuji',
      author_email='uche.ogbuji@fourthought.com',
      classifiers=[
         #'Development Status :: 4 - Beta',
         'Development Status :: 5 - Production/Stable',
         #'Development Status :: 3 - Alpha',
         'Intended Audience :: Developers',
         'License :: OSI Approved :: Apache Software License',
         'Programming Language :: Python',
         'Topic :: Software Development :: Libraries :: Python Modules',
         'Topic :: Text Processing :: Markup :: XML',
         ],
      package_dir={'amara': 'lib'},
      packages=['amara'],
      **kw)

