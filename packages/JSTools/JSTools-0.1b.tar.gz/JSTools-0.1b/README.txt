=========
 JSTools
=========

'JSTools' is a collection of utilities for managing JavaScript libraries.

Install
=======

Until jstools is released into pypi, we suggest checking out jstools
and installing using either 'python setup.py install' or 'python
setup.py develop' from within your checkout.


Script Install
--------------

$ cd /your/javascript/distribution
$ wget http://github.com/whitmo/jstools/raw/master/install.py
$ python install.py

This will safely turn your distribution folder into a python
environment [#]_ with the jstools scripts installed in
'/your/javascript/distribution/bin'.

$ bin/jsbuild
$ bin/jsmin


Other Install Options
---------------------

You can download jstools in whatever flavor your prefer::

 $ wget http://github.com/whitmo/jstools/tarball/master
 $ svn co http://svn.opengeo.org/jstools/trunk/
 $ git clone git://github.com/whitmo/jstools.git


Global Install
``````````````

Depending on your python install (and setuptools plugins), you could
use any of the urls above and easy_install::

  $ sudo easy_install jstool-url-above

If you've downloaded the code, the following command from inside the
distribution will take care of global installation::

  $ sudo python setup.py install


Scripts
=======

jsbuild
-------

Merges and compresses files according to a configuration file.
jsbuild will walk each root directory specified in configuration,
index all the files ending with .js and then compile an aggregate
source based on the specification in the config file and the
dependencies declared inside the files themselves.


Usage
~~~~~

jsbuild <config_file> [options]

Options
+++++++

Options:
  -h [--help]            show this help message and exit
  -u [--uncompress]      Don't compresses aggregated javascript
  -v [--verbose]         print more info
  -o [--output=] OUTPUT_DIR
                         Output directory
  -r [--resource=] RESOURCE_DIR
                         resource base directory (used for interpolation)
  -s [--single=] SECTION
                         Only create file for this section (see below)

Configuration Format
~~~~~~~~~~~~~~~~~~~~

A config file may have multiple uniquely named output files (ie
multiple sections).

A section is formatted in the following fashion::

[Output.js]
root=path/to/where/files/are
license=path/to/license/for/these/libs
first=        
      3rd/prototype.js
      core/application.js
      core/params.js

last=
     core/api.js

exclude=
      3rd/logger.js
#...


The files listed in the `first` section will be forced to load
*before* all other files (in the order listed). The files in `last`
section will be forced to load *after* all the other files (in the
order listed).

The files list in the `exclude` section will not be imported.

The configuration allows for the interpolation of variables defined in
the config file.  '%(resource-dir)s' may be subsituted for the value
of the -r flag.

Lines commented using '#' will be ignored. 


Dependency Syntax
~~~~~~~~~~~~~~~~~

File merging uses cues inside the candidate javascript files to
determine dependencies.  Two types of dependencies are specified 
with two different comment formats within source files.

To specify that a target files must be included before a given 
source file, include a comment of the following format:

     // @requires <file path>

  e.g.

    // @requires Geo/DataSource.js

To specify that a target file must be included at any place
in the merged build - before or after a given source file - 
include a comment in the source file of the following format:

    // @include <file path>

  e.g.

    // @include Geo/DataSource.js

Note that the "exclude" list in a configuration file will 
override dependencies specified by the @requires and @include
comment directives described above.

jsmin
-----

Compresses an input stream of javascript to an output stream


Usage
~~~~~

jsmin < cat some.js > some-compressed.js


License
~~~~~~~
-- The Software shall be used for Good, not Evil. --

see file for complete copyright


License
=======

Mixed. same as OpenLayers unless otherwhise noted


Buildout Support
================

see jsbuild/bo.txt


Run Tests
=========

if you are using the included env.py::

 python setup.py nosetests

otherwhise, you will need to install 'nose' and run the same command.


Credits
=======

jstools started as a collection of build scripts as part of the
OpenLayers Project[#]_.

Whit Morriss (whit at opengeo.org) repackaged these scripts as jstools
and Tim Schaub (tschaub at opengeo.org) did extensive reworking of tsort.


[1] See 'virtualenv <http://pypi.python.org/pypi/virtualenv>'_ for more
information about the python environment.  You may activate and
deactivate this environment to add the installed scripts to your path,
localize python package installs and other niceties ala::

 $ source bin/activate
 $ deactivate

[2] `OpenLayers Homepage <http://www.openlayers.org>`_ and `the
original scripts <http://svn.openlayers.org/trunk/openlayers/tools/>`_

