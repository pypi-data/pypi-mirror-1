from setuptools import setup, find_packages
import sys, os

version = '1.0'
shortdesc ="CSS Variables Support for Zope."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.txt')).read()
entry_points=""""""

setup(name='cornerstone.cssvar',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Framework :: Zope3',
            'Environment :: Web Environment',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='css variables resource',
      author='Jens Klein',
      author_email='jens@bluedynamics.com',
      url='',
      license='BSD License derivative',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['cornerstone',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'zope.component',
        'zope.app.publisher',
        'zope.configuration',
      ],
      extras_require={
        'test': [
            'interlude',
            'zope.testing',
        ]
      },
      entry_points=entry_points,
      )
      
