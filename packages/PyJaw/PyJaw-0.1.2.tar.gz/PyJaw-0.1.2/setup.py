from setuptools import setup, find_packages
import sys, os

version = '0.1.2'

setup(name='PyJaw',
      version=version,
      description="A Python implementation of the Rejaw API",
      long_description="""\
PyJaw - Python implementation of the Rejaw API
==============================================

This is a port of the `Ruby API`_ developed by the `Rejaw team`_.

For full details visit the `project home page`_.

The development version is available in `SVN`_ and via ``easy_install PyJaw==dev``

.. _Ruby API:
    http://code.google.com/p/rejaw/source/browse/trunk/api/ruby/api_client.rb
    
.. _Rejaw team:
    http://rejaw.com/help/about
    
.. _project home page:
    http://code.google.com/p/pyjaw/
    
.. _SVN:
    http://pyjaw.googlecode.com/svn/trunk/#egg=PyJaw-dev
""",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Lee McFadden',
      author_email='spleeman@gmail.com',
      url='http://code.google.com/p/pyjaw',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'simplejson',
      ],
      entry_points="""
      """,
      )
