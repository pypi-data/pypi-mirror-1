from setuptools import setup, find_packages
import sys, os

version = '0.1a2'

setup(name='Clutch',
      version=version,
      description="A Python Web Framework for GAE",
      long_description="""\
Clutch - Web Framework for Google App Engine
============================================

Clutch is a small web framework for Google App Engine.  It was
designed with similar goals to the TurboGears project; Use existing
best-of-breed tools to create a compelling, easy to use framework.

For full details visit the `project home page`_.

The development version is available at `BitBucket`_ and via ``easy_install Clutch==dev``

.. _project home page:
    http://getclutch.appspot.com/
    
.. _BitBucket:
    http://bitbucket.org/splee/clutch/
""",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules"], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Lee McFadden',
      author_email='spleeman@gmail.com',
      url='http://getclutch.appspot.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Routes',
          'Mako',
      ],
      entry_points="""
      """,
      )
