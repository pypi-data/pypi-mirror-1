from setuptools import setup, find_packages
import sys, os

version = '1.1.1'
shortdesc = "library providing a result rendering engine"
readme = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
changes = open(os.path.join(os.path.dirname(__file__), 'CHANGES.txt')).read()
longdesc = '%s\n\n%s' % (readme, changes)

setup(name='cornerstone.ui.result',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Framework :: Zope2',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',            
            'License :: OSI Approved :: Zope Public License'
      ], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Robert Niedereiter',
      author_email='rnix@squarewave.at',
      url='',
      license='Zope Public License',
      packages=find_packages(exclude=['ez_setup',]),
      namespace_packages=['cornerstone', 'cornerstone.ui'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',                        
          # -*- Extra requirements: -*
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
      
