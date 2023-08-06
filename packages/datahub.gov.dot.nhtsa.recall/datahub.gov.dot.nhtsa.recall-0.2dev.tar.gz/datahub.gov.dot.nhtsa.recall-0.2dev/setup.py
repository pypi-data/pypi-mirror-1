from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='datahub.gov.dot.nhtsa.recall',
      version=version,
      description="Recall Database from nhtsa",
      long_description="""\
Source: National Highway Traffic Safety Administration(NHTSA) and U.S. Department of Transportation.

How to use it:
==============

1.\  Download the package from pypi or launchpad::
 
 http://pypi.python.org/pypi/datahub.gov.dot.nhtsa.recall/0.1dev

2.\  Unzip it::
 
 tar -xzvf datahub.gov.dot.nhtsa.recall-0.2dev.tar.gz

3.\  Go into the folder and read what needs to be setup::

 cd  cd datahub.gov.dot.nhtsa.recall/datahub/gov/dot/nhtsa/recall/
 #Read Readme.txt.

4.\  After you have installed any necessary packages or programs, and setup your database you are ready to start the process::
 
 sh process.sh

5.\  When you start this script you should see results like::

 Crawling Data
 Done Crawling
 Parsing Data
 Done Parsing Data
 Loading Data
 Done Loading Data

6.\  Now, this package has downloaded the recall files, unzipped it, parsed it and loaded it to a database you specified in load.py in about 5 minutes depending on your speed. Try comparing that to weeks to figure out where, how and what structure this data has. 

[Sample]Here is a website that uses this package to load new recalls every month.<http://lucasmanual.com/recall>

Feedback is always welcomed. If you don't agree with data structure, or would like to make a improvements please send a patch and we will add it in.

Enjoy.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='nhtsa datahub gov dot dot recall',
      author='Lukasz Szybalski',
      author_email='szybalski@gmail.com',
      url='http://www.lucasmanual.com/mywiki/DataHub',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
