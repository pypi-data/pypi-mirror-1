from setuptools import setup, find_packages
import sys, os

version = '0.9'

setup(name='restlib',
      version=version,
      description="Extensions for the standard urllib2 to support RESTful client applications",
      long_description=open("README.txt").read() + "\n" +
                             open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[ # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Topic :: Internet',
      ],
      keywords='HTTP REST',
      author='Eemeli Kantola',
      author_email='eemeli.kantola@iki.fi',
      url='http://asibsync.sourceforge.net',
      license='BSD',
      py_modules=['restlib'],
      include_package_data=True, # process MANIFEST.in
      zip_safe=True,
      dependency_links = [

      ],
      install_requires=[

      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
