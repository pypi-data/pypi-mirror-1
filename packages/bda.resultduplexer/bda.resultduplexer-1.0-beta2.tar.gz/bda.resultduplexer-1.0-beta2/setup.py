import os
from setuptools import setup, find_packages

version = '1.0-beta2'
shortdesc = "module providing duplexing of search results in plone."
readme = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
changes = open(os.path.join(os.path.dirname(__file__), 'CHANGES.txt')).read()
longdesc = '%s\n\n%s' % (readme, changes)

setup(name='bda.resultduplexer',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Zope2',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Robert Niedereiter',
      author_email='rnix@squarewave.at',
      url='',
      license='General Public Licence',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bda'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'bda.contentproxy',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
