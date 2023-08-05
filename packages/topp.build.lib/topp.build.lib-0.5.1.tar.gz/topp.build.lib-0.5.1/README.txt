Utilizing topp.build.lib
========================

[ Note:  as a big believer in coding == documentation, I hesitantly write
  this document.  It needs to be written, but as with all READMEs, it may
  be out of date. On with it. ]

topp.build.lib is TOPP's build library, designed to make deploying software
essential to TOPP easy and configurable in a unified manner.  topp.build.lib
uses and interacts with buildit for its build process.  See:

http://agendaless.com/Members/chrism/software/buildit

buildit should automatically be installed with the library, as well
as workingenv:  http://cheeseshop.python.org/pypi/workingenv.py

Once the library is installed, there should be a script called 
"create-deployment".  This script can be run to create a skeleton topp.build
project for the argument given on the command line.  So if you run

create-deployment foo

you should get a directory, topp.build.foo, with a minimal skeleton
illustrating the minimum you need for the build process.  It is a good way
to see how things are structured.

The philosophy of topp.build.lib is to have anything reusable live at the
library level.  So if you have a task or data that is or may be needed for 
more than one project, please add it at the library level.  New commands 
(in the buildit sense) should almost always live with the library in
topp.build.lib/topp/build/lib/commands.py

TOPPbuild
---------

The core functionality of topp.build.lib lives in the TOPPbuild class
in topp.build.lib/topp/build/lib/__init__.py.  It is initiated like:

def __init__(self, app, workingenv_opts=(), inifiles=None, 
                 distributions=(), help=''): 

The parameters for this class are as follows:

        app : name of the application [string]

        workingenv_opts:  command-line options to pass to workingenv [tuple]

        inifiles: list of .ini files to write.  if None, all .ini files
        found (save in the skel directory) will be copied

        distributions:  indicates a list of files that a distribution
        is chosen from.  A distribution is specified by an .ini file and
	is intended to cover different needs of deployment.  For example,
	topp.build.opencore has 'local' and 'live' distribution, 
	accompanied by 'local.ini' and 'live.ini' files.
	Distributions may be chosen from the command line via (for instance)

	build-opencore --dist=local

	If no distribution is specified, the default is used -- that is,
	the first one specified in the argument to TOPPbuild.__init__

Configuring the Builds
----------------------

The builds are configured through .ini files.  If you just run 

build-foo

assuming the build succeeds, you'll never see these .ini files, though
they will be moved to ${deploydir}/etc/build for the record

If you need to do any configuration, run 

build-foo --write-config

These will write the .ini files to the current working directory.  Any
edits you make will be reflected in the build process.

Variables
---------

topp.build.lib provides several buildit-style variables available to
help write .ini files:

${name} : [ default value ] -- where it lives

${basedir} :  [ /usr/local/topp ] -- base.ini

${datadir} : [ /var/lib/${app} ]
where to put application data.  this should be independent of builds

${deploydir} : 
the directory to deploy to.  basically, where
you want to put everything

${logdir} : [ /var/log/${app} ] 
where to put the log

${moduledir} : 
the on-disc location of the installed library of the app
you are working in.  For instance, if your app is 'opencore' (i.e. 
topp.build.opencore), then the ${moduledir} might expand to 
/home/jhammel/tmp.opencore/lib/python2.4/topp.build.opencore-0.1.1dev_r4214-py2.4.egg/topp/build/opencore/

${piddir} : [ /var/run/${app} ]
where to put process id information

${srcdir} : [ ${deploydir}/src ]
where to put source files for the installation.  

Skeleton Files
--------------

By convention, a project may have a 'skel' directory (for instance in 
topp.build.foo/topp/build/foo/skel).  The purpose of this directory
is to keep files that will be read and copied using variable subsitution
with <<variable>> syntax from one place to another.

Bug Reports
-----------

Please send env/lib/python/disutils/disutils.cfg
