#Gets setuptools
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.7.79'

setup(name='datahub',
      version=version,
      description="Data Hub",
      long_description="""\
DataHub is a tool that allows you to quickly find and create data mining programs that are able to crawl, parse, and load the data source into database or other types of useful forms.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='datahub datamining csv tsv mdb crawl harvest webdata gov public data',
      author='Lukasz Szybalski',
      author_email='szybalski@gmail.com',
      url='http://datahub.sourceforge.net/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "pastescript>=1.0" ,  
        "pastescript!=1.7.2" ,  
        "cheetah>=2.0",   
        # -*- Extra requirements: -*-
      ],
      entry_points="""
        [paste.paster_create_template]
        #datahub = datahub.datahub:FrameworkTemplate
        datahub = datahub:FrameworkTemplate
      """,
      )
