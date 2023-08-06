from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='ootools',
      version=version,
      description="Python and OpenOffice connectivity, and conversion tools.",
      long_description="""\
Open Office Tools is a set of program that allows you to easly connect to OpenOffice via Python Uno module. It provides interface to starting Open office for you, stoping it, and connecting. Other conversion tools like ods2csv, or xls2csv are being included as soon as you send me a link to them.

Installing ootools
------------------

You install ootools via you system package manger or via easy_install::

 easy_install ootools

Starting OpenOffice
-------------------

Start openoffice via this set of commands::

 import ootools
 oor=ootools.OORunner()
 oor.start()

Connecting to OpenOffice
------------------------

To connect to open office you just issue a connect statement::

 import ootools
 oor=ootools.OORunner()
 oor.start()
 desktop=oor.connect()
 #Do something with the "Desktop" aka OpenOffice main document module.

Stopping OpenOffice
-------------------

You stop OpenOffice via a stop statement::

  oor.stop()

Tools
-----

We are waiting for people to send us patches or links to tools like ods2csv, xls2csv, etc...

For the latest changes see the `readme file
<http://bazaar.launchpad.net/~szybalski/ootools/trunk/annotate/head%3A/Readme.txt>`_.

""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ootools, openoffice, python, pyuno, ods2csv, xls2csv',
      author='Lukasz Szybalski',
      author_email='szybalski@gmail.com',
      url='http://www.lucasmanual.com/mywiki/ootools',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            #"uno",
            # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
