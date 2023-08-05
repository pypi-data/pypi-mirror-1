Introduction
************

The Open Shakespeare package provides a full open set of shakespeare's works
(often in multiple versions) along with ancillary material, a variety of tools
and a python API.

Specifically in addition to the works themselves (often in multiple versions)
there is an introduction, a chronology, explanatory notes, a concordance and
search facilities.

All material is open source/open knowledge so that anyone can use, redistribute
and reuse these materials freely. For exact details of the license under which
this package is made available please see COPYING.txt.

Open Shakespeare has been developed under the aegis of the Open Knowledge
Foundation (http://www.okfn.org/).

Contact the Project
*******************

Please mail shakespeare-info@okfn.org or join the okfn-discuss mailing list:

  http://lists.okfn.org/listinfo/okfn-discuss


Installation
************

1. Install the code
===================

1.1: (EITHER) Install using setup.py (preferred)
------------------------------------------------

1. Install setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall#installation-instructions
(download http://peak.telecommunity.com/dist/ez_setup.py and run it).

2. $ python setup.py install

1.2 (OR) Get the code straight from subversion
------------------------------------------------

1. Check out the subversion trunk
2. Add the path/to/src to your PYTHONPATH
3. Make sure you have all required dependencies:
  1. For the domain model:
    * sqlobject >= 0.6
  2. For the web interface:
    * cherrypy >= 2.2
    * kid templating language >= 0.9 (layout templates)

2. Cache Directory
==================

Create a cache directory where texts and other material can be stored

This directory needs to be semi-permanent so do *not* put under a location such
as /tmp. 

4. Create a configuration file
==============================

1. copy the template at etc/shakespeare.conf.new to a suitable new location
   (suggestion: etc/shakespeare.conf)

2. edit to reflect your setup (see comments in file)

3. make sure the config file can be found:
  1. EITHER: it must be located at etc/shakespeare.conf relative to the
       directory from which you run scripts
  
  2. OR: set the SHAKESPEARECONF environment variable to contain the path to
       the configuration file

4. Initialize the system
========================

Run: $ bin/shakespeare-admin init

This may take some time to run so be patient

TIP: using sqlite building the concordance really **does** seem to run forever
so recommend using postgresql or mysql if you are going to build the
concordance. 


Getting Started
***************

As a user:
==========

Start up the web interface by running the webserver:

  $ bin/shakespeare-admin runserver

Then visit http://localhost:8080/ using your favourite web browser.

As a developer:
===============

1. Check out the administrative commands: $ bin/shakespeare-admin help.

2. Run the tests: $ py.test
   
Note that:
   
  * The tests use [py.test] so you will need to have installed this

  * To run the website tests (site_test etc) you will need to install [twill]
    and have the webserver running

[py.test]: http://codespeak.net/py/current/doc/getting-started.html
[twill]: http://twill.idyll.org/

