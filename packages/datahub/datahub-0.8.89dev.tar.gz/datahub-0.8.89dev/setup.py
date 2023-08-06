#Gets setuptools
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.8.89'

setup(name='datahub',
      version=version,
      description="Data Hub",
      long_description="""\
DataHub
=======

* Datahub is a tool that allows faster download/crawl, parse, load, and visualize of data. It achieves this by allowing you to divide each step into its own work folders. In each work folder you get a sample files that you can start coding.
* Datahub is for people who found some interesting data source for them, they want to download it, parse it, load it into database, provide some documentation, and visualize it. Datahub will speed up the process by creating folder for each of these actions. You will create all the programs from our base default template and move on to analyzing the data in no time.


6 Rules for Data Privacy
========================

 1. Sensitive, and possibly inaccurate, information may not be used against people in financial, political, employment, and health-care settings.
 2. All information should not forcing anybody to hide or protect them self against improper information use that significantly limits persons ability to exercise his/her right to freedom of association.
 3. Implement a basic form of information accountability by tracking identifying information that identifies a person or corporation and could be used to held that person/corporation accountable for the compliance.
 4. There should be no restriction on use of data unless specified by laws and these privacy rules.
 5. Privacy is protected not by limiting the collection of data, but by placing strict rules on how the data may be used. Data that can be used in financial, political, employment, and health-care settings  cannot be used for marketing and other profiling. Strict penalties should be imposed by for the breach of these use limitations. Actions that involve financial, political, employment, and health-care settings decision must be justified with reference to the specific data on which the decision was based. If the person/corporation discovers that the data is inaccurate, he or she may demand that it be corrected. Stiff financial penalties should be imposed against the agency that does not make the appropriate corrections.
 6. Achieve greater information accountability only by making better use of the information that is collected, retaining the data that is necessary to hold data users responsible for policy compliance. Build the system that encourages compliance, and maximizes the possibility of accountability of violations. Technology should supplant the rules because users are aware of what they are and because they know there will be consequences, after the fact.



Install DataHub
===============

The best way to get started with datahub is to install it in the following way.
Setup virtualenv which will keep the installation in a separate directory::

 virtualenv --no-site-packages datahubENV
 New python executable in datahubENV/bin/python
 Installing setuptools............done.
 
 source datahubENV/bin/activate 




Create DataHub based project
============================

Datahub is a paster template so you run it as follows::

 paster create --list-templates
 paster create -t datahub

You should see something like this::

 paster create -t datahub

Selected and implied templates::

  PasteScript#basic_package  A basic setuptools-enabled package
  datahub#datahub            DataHub is a tool to help you datamine(crawl, parse, and load) any data.

 Enter project name: myproject
 Variables:
   egg:      myproject
   package:  myproject
   project:  myproject
 Enter version (Version (like 0.1)) ['']: 
 Enter description (One-line description of the package) ['']: my project
 Enter long_description (Multi-line description (in reST)) ['']: this is a long description
 Enter keywords (Space-separated keywords/tags) ['']: datahub dataprocess
 Enter author (Author name) ['']: myname
 Enter author_email (Author email) ['']: 
 Enter url (URL of homepage) ['']: 
 Enter license_name (License name) ['']: 
 Enter zip_safe (True/False: if the package can be distributed as a .zip file) [False]: 
 Creating template basic_package
  Creating directory ./myproject
   Recursing into +package+
     Creating ./myproject/myproject/
     Copying __init__.py to ./myproject/myproject/__init__.py
   Copying setup.cfg to ./myproject/setup.cfg
   Copying setup.py_tmpl to ./myproject/setup.py
 Creating template datahub
   Recursing into +package+
     Copying README.txt_tmpl to ./myproject/myproject/README.txt
     Recursing into crawl
       Creating ./myproject/myproject/crawl/
       Copying Readme.txt_tmpl to ./myproject/myproject/crawl/Readme.txt
       Copying __init__.py to ./myproject/myproject/crawl/__init__.py
       Copying download.sh to ./myproject/myproject/crawl/download.sh
       Copying download_list.txt_tmpl to ./myproject/myproject/crawl/download_list.txt
       Copying harvestman-+package+.xml to ./myproject/myproject/crawl/harvestman-myproject.xml
     Recursing into hdf5
       Creating ./myproject/myproject/hdf5/
       Copying READEM_hdf5.txt_tmpl to ./myproject/myproject/hdf5/READEM_hdf5.txt
       Copying __init__.py to ./myproject/myproject/hdf5/__init__.py
     Recursing into load
       Creating ./myproject/myproject/load/
       Copying __init__.py to ./myproject/myproject/load/__init__.py
       Copying model.template to ./myproject/myproject/load/model.template
     Recursing into parse
       Creating ./myproject/myproject/parse/
       Copying __init__.py to ./myproject/myproject/parse/__init__.py
     Recursing into wiki
       Creating ./myproject/myproject/wiki/
       Copying REAME.wiki_tmpl to ./myproject/myproject/wiki/REAME.wiki
 Running /home/lucas/tmp/datahubENV/bin/python setup.py egg_info
 Manually creating paster_plugins.txt (deprecated! pass a paster_plugins keyword to setup() instead)
 Adding datahub to paster_plugins.txt

Go into the myproject folder and start coding.
The folder structure looks like this::

 myproject
 |-- myproject
 |   |-- README.txt
 |   |-- __init__.py
 |   |-- crawl
 |   |   |-- Readme.txt
 |   |   |-- __init__.py
 |   |   |-- download.sh
 |   |   |-- download_list.txt
 |   |   `-- harvestman-myproject.xml
 |   |-- hdf5
 |   |   |-- READEM_hdf5.txt
 |   |   `-- __init__.py
 |   |-- load
 |   |   |-- __init__.py
 |   |   `-- model.template
 |   |-- parse
 |   |   `-- __init__.py
 |   `-- wiki
 |       `-- REAME.wiki
 |-- myproject.egg-info
 |   |-- PKG-INFO
 |   |-- SOURCES.txt
 |   |-- dependency_links.txt
 |   |-- entry_points.txt
 |   |-- not-zip-safe
 |   |-- paster_plugins.txt
 |   `-- top_level.txt
 | -- setup.cfg
 `-- setup.py
 

Get stared with your data project
=================================

crawl
~~~~~

Crawl folder is where you crawl data. You have two choices as far as downloading. For each choice there are pre-build files, so just follow this:
 
harvestman
----------

* You should use harvestman if the size of what you are trying to download is big enough that it would be too much time consuming to list each file in a download_list.txt.
* You can download a partial or the whole website using harvestman. Harvestman can use wild cards, take configuration settings to download what you need. 

Setup the config file like this::

 cd crawl
 harvestman --genconfig
 #save or edit harvestman conf file, and then start downloading using the following command.
 harvestman -C harvestman-myproject.xml

wget
----

With wget you can download the files if the list of files is not big. There is a download_list.txt that will hold the url you want to download. You can specify wild cards like `*.zip`, `*.pdf`, `*.txt` etc. Download.sh is a shell script that holds wget files. By default it will only download files if they are newer then what you downloaded, and it will only download the missing parts. This saves your bandwidth and does not re-download the whole files each time.

The only thing you need to do is edit download_list.txt::

 cd crawl
 #Edit download_list.txt and add url of files you want to download
 vi download_list.txt
 sh download.sh

Enjoy.
""",
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
