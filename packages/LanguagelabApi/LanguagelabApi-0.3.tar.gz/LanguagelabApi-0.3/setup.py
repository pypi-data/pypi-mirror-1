from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='LanguagelabApi',
      version=version,
      description="A Python implementation of the Languagelab API",
      long_description="""\
LanguagelabApi - Python client for the Languagelab Partner API
==============================================================

This is a client implementation of the `Languagelab Partner API`_.

For full details visit the `project home page`_.

The development version is available via `Mercurial`_ and via ``easy_install LanguagelabApi==dev``

.. _Languagelab Partner API:
    http://testpartner-api.languagelab.com/
    
.. _project home page:
    http://www.bitbucket.org/splee/languagelabapi/
    
.. _Mercurial:
    http://www.bitbucket.org/splee/languagelabapi/get/tip.zip#egg=LanguagelabApi-dev
""",
      classifiers=[
        "Development Status :: 4 - Beta",
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
      url='http://www.bitbucket.org/Splee/languagelabapi/',
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
