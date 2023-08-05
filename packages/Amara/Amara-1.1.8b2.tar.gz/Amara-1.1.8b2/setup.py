#!/bin/env python

#Metadata
kw = {'name': "Amara",
      'version': '1.1.8b2',
      'description': "Amara XML Toolkit: a collection of Python/XML processing tools to complement 4Suite (http://4Suite.org)",
      'long_description': "A collection of Python/XML processing tools to complement 4Suite (http://4Suite.org).  The components are: Bindery--a data binding tool (fancy way of saying it's a very Pythonic XML API); Scimitar--an implementation of the ISO Schematron schema language for XML, which converts Schematron files to Python scripts; domtools--A set of tools to augment Python DOMs; saxtools--A set of tools to make SAX easier to use in Python",
      'url': 'http://uche.ogbuji.net/tech/4suite/amara/',
      'author': 'Uche Ogbuji',
      'author_email': 'uche.ogbuji@fourthought.com',

      #'download_url': 'ftp://ftp.4suite.org/pub/Amara/',
      'classifiers': \
        ['Development Status :: 4 - Beta',
         #'Development Status :: 5 - Production/Stable',
         #'Development Status :: 3 - Alpha',
         'Intended Audience :: Developers',
         'License :: OSI Approved :: Apache Software License',
         'Programming Language :: Python',
         'Topic :: Software Development :: Libraries :: Python Modules',
         'Topic :: Text Processing :: Markup :: XML'],
      }

try:
    from setuptools import setup, find_packages
    setup(package_dir={'amara': 'lib'},
          #packages=find_packages(),
          packages=['amara'],
          scripts=['lib/scimitar.py',
                    'lib/flextyper.py'],
          install_requires=['4Suite>=1.0b4'],
          **kw)

except ImportError:
    import os
    from distutils import core
    execfile(os.path.join('lib', '__version__.py'))
    kw['version'] = __version__

    #Modules
    #kw['py_modules'] = ['anobind', 'domtools', 'tenorsax']
    #kw['package_dir'] = {'amara': 'lib'}
    #kw['packages'] = ['amara']
    #kw['scripts'] = ['lib/scimitar.py', 'lib/flextyper.py']

    #Check for Python 2.3
    #if type(True) == bool:

    #More specific test for distutils features
    if (hasattr(core, 'setup_keywords') and 
        'classifiers' in core.setup_keywords):
        kw['download_url'] = 'ftp://ftp.4suite.org/pub/Amara/'
        kw['classifiers'] = \
            ['Development Status :: 4 - Beta',
             #'Development Status :: 5 - Production/Stable',
             #'Development Status :: 3 - Alpha',
             'Intended Audience :: Developers',
             'License :: OSI Approved :: Apache Software License',
             'Programming Language :: Python',
             'Topic :: Software Development :: Libraries :: Python Modules',
             'Topic :: Text Processing :: Markup :: XML']

    from Ft.Lib.DistExt import PackageManager

    kw.update({
        # our Distribution class
        'distclass': PackageManager.PackageManager,

        # PackageManager specific
        'package_info': PackageManager.LoadPackageDefinitions(['Amara.pkg']),
    })

    del __version__

    core.setup(**kw)

