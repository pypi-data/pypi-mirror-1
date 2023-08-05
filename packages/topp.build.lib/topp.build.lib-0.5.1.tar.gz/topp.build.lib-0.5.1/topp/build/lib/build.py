# global imports

import os
import sys
import shutil
import pkg_resources
import socket
import optparse
import StringIO
import glob

import workingenv

# buildit imports

import buildit.resolver
from buildit.task import Task
from buildit.context import select_one
from buildit.context import Context
from buildit.context import Software
from buildit.commandlib import InFileWriter

# topp.utils imports

from topp.utils.filesystem import abspath, makedir
from topp.utils.modules import module_directory
from topp.utils.ip import get_ip
from topp.utils.error import error

# local imports

import checkport
import deploy
import taskfuncs
import startup
from utils import appname

# shorthand
join = os.path.join

# XXX data should be moved into the class or elsewhere

# staging directory where all deployments go
stagingdir = join('${basedir}', '${deploy}')  

# additional directories for deployment
dirs = { 'logdir': '${basedir}/var/log/${app}',
         'datadir': '${basedir}/var/lib/${app}',
         'piddir': '${basedir}/var/run/${app}',
         'initdir': '${basedir}/etc/init.d',
         'confdir': '${basedir}/etc/conf.d',
         'monitdir': '${basedir}/etc/monit.d' }

def get_deployname(deploydir, app):
    """
    return a dated name for the deploy directory
    """

    import time

    prefix = '%s-' % app + '%04d%02d%02d-' % time.localtime()[:3]

    ctr = 1
    while os.path.exists(join(deploydir, prefix + str(ctr))):
        ctr += 1

    retval = join(deploydir, prefix + str(ctr))
    return retval    

class TOPPbuild(object):
    """
    master class for TOPP build library
    """

    ### class variables
    auto = 'auto'

    def __init__(self, app, use_workingenv=True,
                 workingenv_opts=(),
                 workingenv_log_file='${deploydir}/workingenv.log',
                 inifiles=None, 
                 distributions=(), help='', 
                 buildoutdir=None,
                 deploydir=None):
        """
        app : name of the application

        workingenv_opts:  command-line options to pass to workingenv

        inifiles: list of .ini files to write.  if None, all .ini files
        found (save in the skel directory) will be copied

        distributions:  indicates a list of files that a distribution
        is chosen from.  

        help: help string to print from command-line
        """
        
        # instance variables
        self.app = app
        self.tasks = []  # buildit tasks
        self.root_tasks = [] # shell commands
        self.use_workingenv = use_workingenv
        self.workingenv_opts = workingenv_opts
        self.workingenv_log_file = workingenv_log_file
        self.inifiles = inifiles
        self.vars = []
        self.context_options = []
        self.auto_variables = []
        self.help = help
        self.distributions = distributions
        self.directories = [ 'deploydir', 'srcdir' ] # directories to expand
        self.passwords = []

        # set where software is build, where to put .ini files
        if buildoutdir:
            self.buildoutdir = buildoutdir
        else:
            self.buildoutdir = os.getcwd()

        # create empty context for app being built
        self.context = Context(StringIO.StringIO(), 
                               buildoutdir=self.buildoutdir)

        version = str(pkg_resources.get_distribution(appname(self.app)))
        
        # add command line options
        self.parser = optparse.OptionParser(version=version)
        self.add_option("--write-config", action="store_true",
                        dest="write_config", default=False,
                        help="write configuration (.ini) files")
        self.add_option("--keep-config", action="store_true",
                        dest="keep_config", default=False,
                        help="keep a copy of configuration (.ini) files locally after build")

        if self.use_workingenv:
            self.add_option("--in-place", action="store_true",
                            dest="in_place", default=False,
                            help="use current workingenv for installation")

        self.add_option("--use-last", action="store_true",
                        dest="use_last", default=False,
                        help="use the last build as a starting point, if it exists"
                        )
        self.add_option("--no-link", action="store_false",
                        dest="link", default=True,
                        help="don't link the deploy directory to the temporary")
        self.add_option("--checkports", action="store_true",
                        dest="checkports", default=False,
                        help="check port availability")
        self.add_option('--deploydir', 
                        directory=True,
                        help='directory to deploy the software in',
                        default=deploydir)        
        self.add_option('--conf',
                        directory=True,
                        help='configuration overrides',
                        )

        # add command line options linked to context variables
        self.add_context_option('--srcdir',
                                directory=True,
                                help='where all the source packages will be downloaded and compiled (FULL PATH)')
        
        if self.distributions: 

            # the first given is the default
            default = self.distributions[0]

            if len(self.distributions) > 1:
                self.add_context_option('--dist',
                                        help="The distribution to use (default '%s').  Choose from: %s" % (default, self.distributions),
                                        metavar="distribution",
                                        default=default)


    ### front-end functions dealing with variables/options

    def set_variable(self, var, value):
        """ 
        add a variable programmatically to be interpolated via Context
        """
        self.vars.append((var, value))

    def add_auto_variable(self, var, callback):
        """
        add variables that can be given a specific value or are automatically
        filled in.  if the value is self.auto (== 'auto'), then call
        the callback function
        """
        # XXX this should respect namespaces
        # XXX currently, only global variables can be used
        self.auto_variables.append((var, callback))

    def add_option(self, *args, **kwargs):
        """add an option to the parser"""
        
        # the option is a directory that should be expanded
        directory = kwargs.pop('directory', False)

        option = optparse.make_option(*args, **kwargs)

        if directory:
            self.directories.append(option.dest)

        self.parser.add_option(option)

    def add_context_option(self, option, dest=None, namespace=None, 
                           directory=False, **kwargs):
        """ add an option to the parser and to the context globals """

        option = option.lstrip('-')

        if not dest:
            dest = option

        self.context_options.append(dict(option=dest, 
                                         namespace=namespace,
                                         ))

        kwargs['dest'] = dest
        self.add_option('--' + option, directory=directory, **kwargs)

    def add_password(self, name='password', **kwargs):
        if name in self.passwords:
            return 
        self.passwords.append(name)
        self.add_context_option(name, **kwargs)

    ###

    def check_passwords(self):
        for name in self.passwords:
            password = getattr(self.options, name)
            if not password:                                
                # if the password is not specified, err out
                error('%s: password must be supplied (use --%s)' % (name,
                                                                    name))

    def parse_args(self, args=None):
        """parse the command line arguments"""

        if args is None:
            args = sys.argv[1:]

        self.options, self.args = self.parser.parse_args(args)

        # expand the directories if not context options
        directories = [ d for d in self.directories 
                        if d not in [ option['option'] for option in 
                                      self.context_options ] ]
        for i in directories:
            d = getattr(self.options, i)
            if d:
                setattr(self.options, i, abspath(d))

        # check the passwords if you're doing a full install
        if not self.options.write_config:
            self.check_passwords()

        # ensure that the parsed distribution is a choice
        dist = getattr(self.options, 'dist', None)
        if (dist is not None) and (dist not in self.distributions):
            error("'%s' distribtion not found.\nChoices:  %s" % (dist, 
                                                                 self.distributions)
                  )
            

        # check for options that are explicitly set/unset
        # XXX is this needed?
        for i in self.tasks:
            if i['name']:
                i['perform'] = getattr(self.options, i['name'])

        return self.args # return remaining args

    ### functions for dealing with tasks

    def add_task(self, task, name=None, prepend=False, perform=True, **kwargs):
        """
        add a single task
        """

        taskdict = {'task': task, 'name': name, 'perform': perform}

        if name:
            # add a task that can be turned on/off from the CLI
            if perform:
                kwargs['action'] = "store_false"
                kwargs['default'] = True
                argname = '--no-' + name
            else:
                kwargs['action'] = "store_true"
                kwargs['default'] = False
                argname = '--' + name
            kwargs['dest'] = name
            self.add_option(argname, **kwargs)

        if prepend:
            self.tasks[:0] = [ taskdict ]
        else:
            self.tasks.append(taskdict)

    ### operators

    def __iadd__(self, other):
        """ add a task or a few.  names not currently supported """

        try:
            iter(other)
        except TypeError:
            self.add_task(other)
        else:
            for i in other:
                self.add_task(i)
        return self

    def __getitem__(self, item):
        return self.context.globals[item]

    ### functions dealing with .ini files
    
    def find_ini_files(self, app, excluded_directories=('skel',),
                       local_excludes=('.svn',)):
        """ find all .ini files associated with the app """
        
        retval = []

        # directory to search under
        directory = module_directory(appname(app))

        # walk through the path
        for root, dirs, files in os.walk(directory):

            # get the furtherer path
            dirname = root.split(directory, 1)[-1].lstrip(os.path.sep)

            # remove excluded directories
            for d in dirs[:]:
                if join(dirname, d) in excluded_directories:
                    dirs.remove(d)
                elif d in local_excludes:
                    dirs.remove(d)

            # extend the list
            retval.extend([ join(dirname, fname) for fname in files
                            if fname.endswith('.ini') ])

        return retval

    def copy_ini_files(self, app=None, files=None, outdir=None, **kwargs):
        """
        copy the .ini files from the egg directories to buildoutdir
        return a list of files copied.
        """

        if app is None:
            app = self.app

        # directory to write to
        if outdir is None:
            outdir = self.buildoutdir

        # list of files given 
        if files is None:
            files = self.find_ini_files(app)
    
        # whether to overwite the files
        overwrite = kwargs.get('overwrite', False)

        # get the Context for the InFileWriter
        context = kwargs.get('context', None)
        if not context:
            context = Context(StringIO.StringIO())

        ### copy the files 

        retval = []

        directory = module_directory(appname(app))
        for inifile in files:
            f = join(directory, inifile)
            g = join(outdir, inifile)
            retval.append(inifile)

            if os.path.exists(g) and overwrite:
                os.remove(g)

            # make the directory if it doesn't exist
            dirname = os.path.split(inifile)[0]
            tmpoutdir = join(outdir, dirname)
            if dirname and (not os.path.exists(tmpoutdir)):
                os.makedirs(tmpoutdir)

            # write the file with variable interpolation
            write = Task(
                'write %s' % inifile,
                targets=g,
                commands = [ InFileWriter(infile=f, outfile=g) ],
                )
            context.run(write)                                

        # return the list of .ini files
        return retval

    def get_ini_files(self):
        """
        get (find,copy) the .ini files associated with the app
        """

        # find the inifiles
        all_ini_files = self.find_ini_files(self.app)

        # if .ini files are specified then use them
        if self.inifiles:
            set_ini_files = set(list(self.inifiles) + 
                                [ i + '.ini' for i in self.distributions ])

            # make sure you find specified .ini files
            if not set_ini_files.issubset(all_ini_files):
                difference=', '.join([str(i) for i in 
                                      set_ini_files.difference(all_ini_files)])
                
                error("Specified .ini files not found in %s: %s" % (
                        appname(self.app), difference))            
            
            # use only the .ini files specified
            all_ini_files = list(set_ini_files)
        
        # use the chosen distribution -- 
        # don't write/use the other .ini files
        # [ note: they must be in the top-level directory ]
        for i in self.distributions:
            if self.options.dist != i:
                all_ini_files.remove(i + '.ini')

        return all_ini_files        

    def update_context(self, filename, buildoutdir=None):
        """
        update the instance's context with a new filename
        """
        assert filename is not None
        context = self.context # change this line to genericize
        
        tmpcontext = Context(filename, 
                             buildoutdir=buildoutdir,
                             global_variables=context.globals)

        # use the 'universal' namespace from the --conf file
        conf = self.options.conf
        if conf:
            try:
                select_one(conf, 'universal')
                tmpcontext.set_file('universal', conf, 'universal')
            except ValueError:
                pass

        # update the context from the temporary
        context.globals.update(dict([ (i, j) 
                                      for i, j in tmpcontext.globals.items() 
                                      if i not in context.globals ]))
        context.namespace_selections.extend(tmpcontext.namespace_selections)

    def get_context(self, overwrite):
        """ copy the .ini files and get the buildit context """

        inifiles = self.get_ini_files()

        # add variables we'll be using
        self.context.globals['moduledir'] = module_directory(appname(self.app))
        self.context.globals['ipaddress'] = get_ip()
        self.context.globals['hostname'] = socket.gethostname()
        self.context.globals['platform'] = sys.platform + '-' + os.uname()[-1]
        self.context.globals['uname'] = ' '.join(os.uname())
        self.context.globals['python'] = sys.executable
        self.context.globals['python_version'] = sys.version

        # preliminary interpolation
        self.interpolate_variables()

        # parse overrides
        self.parse_overrides()

        # copy the .ini files
        self.inifiles = []
        self.inifiles.extend(self.copy_ini_files('lib', 
                                            overwrite=overwrite,
                                            context=self.context))
        self.inifiles.extend(self.copy_ini_files(files=inifiles, 
                                                 overwrite=overwrite,
                                                 context=self.context))

        # no need to continue if all you care about are the .ini files
        if self.options.write_config:
            return

        # join the globals and namespaces from other .ini files
        for j in self.inifiles:            
            if not os.path.split(j)[0]: # only read top-level .ini files
                self.update_context(join(self.buildoutdir, j), 
                                    buildoutdir=self.buildoutdir)

        # add variables that depend on ${app} (expected in the .ini files)
        self.context.globals['app_upper'] = self.interpolate('${app}').upper()

    def parse_overrides(self):
         """parse overrides"""
         if self.options.conf:            
            if not os.path.exists(self.options.conf):
                error('%s not found' % self.options.conf)
            self.update_context(self.options.conf, 
                                self.buildoutdir)

    def set_deploydir(self, deploydir):
        """
        sets context variables dependent on a deploydir
        """

        if not self.system_install:
            self.context.globals['basedir'] = deploydir

        self.context.globals['deploydir'] = deploydir
        self.context.globals['prefix'] = deploydir  # for autoconf
        self.context.globals['srcdir'] = join(deploydir, 'src')

        # additional directories
        for i in dirs:
            self.context.globals[i] = self.interpolate(dirs[i])

    def setupDeploymentStructure(self):
        """ 
        sets variables directly related to deployment --
        deploydir, --in-place, etc
        """

        # whether the installation is system-wide 
        self.system_install = True 

        if self.options.use_last:
            # get the last used directory for the new deployment directory            
            olddeploydir, appname = os.path.split(self.context.globals['deploydir'])
            appname = appname.split('-',1)[0]
            
            cases = [ os.path.split(i)[-1] for i in 
                      glob.glob(os.path.join(olddeploydir, 
                                             '%s*' % appname)) ]
            if cases:

                def sort_key(case):
                    (appname, thedate, build) = case.rsplit('-', 2)
                    return thedate, build

                cases.sort(key=sort_key)
                self.set_deploydir(join(olddeploydir, cases[-1]))

        if self.use_workingenv:
            self.setup_workingenv()

        # options.deploydir overrides other options
        if self.options.deploydir:
            deploydir = os.path.normpath(self.options.deploydir)
            if not os.path.isabs(deploydir):
                deploydir = join(self.interpolate('${cwd}'), deploydir)
            self.system_install = False
            self.set_deploydir(deploydir)  # set the deploydir-based variables

        else: # system-wide deployment

            # set the deploydir-based variables
            deploydir = get_deployname(self.interpolate(stagingdir), 
                                       self.interpolate('${app}'))
            self.set_deploydir(deploydir)


    ### core installation functions

    def setup_workingenv(self):
        if self.options.in_place:
            self.system_install = False

            # check if you're in a workingenv
            if not os.environ.has_key('WORKING_ENV'):
                error('You must be in a workingenv to use --in-place')

            # set the deploydir-based variables
            self.set_deploydir(os.environ['WORKING_ENV'])

            # parse the workingenv options
            (wenvoptions, args) = workingenv.parser.parse_args(list(self.workingenv_opts))
            requirements = ()
            if hasattr(wenvoptions, 'requirements'):
                requirements = wenvoptions.requirements

            # install the requirements
            if requirements:
                self.add_task(taskfuncs.poacheggs(*requirements), 
                              prepend=True)

        else:
            print 'log file', self.workingenv_log_file

            # make a workingenv for the software
            kw = dict(log_file=self.workingenv_log_file)
            kw['targets'] = '${deploydir}/bin/activate'
            self.add_task(
                taskfuncs.mkworkingenv(*self.workingenv_opts, **kw),
                prepend=True)
        
    def interpolate(self, string):
        return self.context.interpolate(string, None)

    def interpolate_variables(self):
        """ 
        interpolates variables set both programmatically 
        and passed on the command line
        """

        def interpolate_self_vars():
            for i in self.vars[:]:
                try:
                    ival = self.interpolate(i[1])
                except buildit.resolver.MissingDependencyError:
                    continue
                self.context.globals[i[0]] = ival
                self.vars.remove(i)            

        # add and interpolate given variables
        interpolate_self_vars()
        
        # use command given context CLI options
        for i in self.context_options:
            val = getattr(self.options, i['option'])
            if val is not None:
                try:
                    ival = self.interpolate(val)
                except buildit.resolver.MissingDependencyError:
                    continue

                if i['option'] in self.directories:
                    ival = abspath(ival)

                if i['namespace']:
                    self.context.set_override(i['namespace'], 
                                              i['option'],
                                              ival)
                else:
                    self.context.globals[i['option']] = ival
                
        # make sure all given variables get interpreted
        interpolate_self_vars()

    ### functions related to tasks

    def get_ports(self):
        """ gets the ports that will be active for the process """
        
        return [ i for i in self.context.globals
                 if i.endswith('_port') or i == 'port' ]

    def add_final_tasks(self):
        """ add tasks to the end of the install process """

        # create non-existent directories
        self += taskfuncs.createdirectories(dirs.values())

        # check and set the port if specified
        if self.options.checkports:
            self += checkport.getporttasks(self.get_ports(),
                                           self.system_install)

        # link the deploy directory to the temporary
        if self.system_install and self.options.link:
            self.add_task(deploy.linkdeploydir)

    def do(self, task):
        """ perform a single task """

        # check to see if the task is to be performed
        if isinstance(task, dict):
            if task['perform']:
               task = task['task']
            else:
                return 

        if isinstance(task, Task):
            # if its a buildit task, install it
            Software(task, self.context).install()
        else:
            # if its a python task, eval it
            print 'Executing python: "%s"' % task
            exec(task)
        
    def perform_tasks(self, tasks=None):
        """ do a list of tasks """

        if not tasks:
            tasks = self.tasks
        
        for i in tasks:
            self.do(i)

    def install(self):
        """ master function to do the install """

        ### parse the command line
        if not hasattr(self, 'options'):
            self.parse_args()
        if self.args:
            error('Unrecognized arguments: %s' % ' '.join(self.args),
                  self.parser)

        # get the context
        self.get_context(overwrite=self.options.write_config)
        
        if self.options.write_config:
            # you are done
            return
        
        # setup directory structure depending on type of deployment
        # (--deploydir, --in-place, --use-last, etc.)
        self.setupDeploymentStructure()

        # ensure that all the namespaces get resolved
        # non-global namespaces should not be touched before this point
        self.context._resolved = None
        self.context.resolve()

        # interpolate programmatically set variables 
        self.interpolate_variables()

        # interpolate auto variables:
        # variables with callbacks triggered by values of 'auto'
        for variable, function in self.auto_variables: 
            if self.context.globals.get(variable, 'auto') == 'auto':
                self.context.globals[variable] = function(self)

        ### add tasks for end of install process
        self.add_final_tasks()
        
        # execute the tasks (i.e. install)
        self.perform_tasks()

        # do post install stuff
        self.post_install(self.system_install)

    ### functions related to post-install

    def move_inifiles(self):
        """ 
        move the inifiles to:
        a. cleanup cruft 
        b. keep a log of the build
        """
        
        # TODO: make this directory earlier ?
        dest = self.interpolate(join('${deploydir}', 'etc', 'build'))
        makedir(dest)
        
        directories = set()
        # move the files:
        # assumes you're in the right directory
        if self.options.keep_config:
            relocate = shutil.copy
        else:
            relocate = shutil.move
        for i in self.inifiles:
            dirname = os.path.split(i)[0]
            if dirname:
                makedir(join(dest, dirname))
                directories.add(dirname)            
            relocate(i, join(dest, i))


        # delete the stale directories
        if not self.options.keep_config:
            for i in directories:
                os.removedirs(i)

    def set_operating_data(self, start, stop=None, pidfile=None):
        """
        sets data to start and stop the built appllication
        this should be called before parsing if you
        want the start option
        """

        instance_vars = ['start', 'stop', 'pidfile']
        for name in instance_vars:
            var = locals()[name]
            setattr(self, name, var)

        self.add_option('--start', dest='start',
                        action="store_true", default=False,
                        help="start %s" % self.app)

    def post_install(self, system_install):
        """ do all post-install stuff """
        
        #  post-install message
        message = self.write_final_message()
        print message

        if hasattr(self, 'start'):
            # do startup stuff
            s = startup.StartUp(self.start, self.stop, self.context)

        # script for root to execute
        if system_install:
            self.write_root_tasks()

        # move the .ini files
        self.move_inifiles()

        # start the software, if told to do so
        if hasattr(self, 'start') and getattr(self.options, 'start'):
             print "Starting %s" % self.app
             s.start()

    def set_final_message(self, message):
        """
        add a message to be displayed post-installation.
        the message can be a string or a filename to be interpolated
        """
        
        self.final_message = message

    def write_final_message(self):

        # default message
        if not hasattr(self, 'final_message'):
            self.final_message = '%s successfully installed in %s' % (
                self.app, '${deploydir}')
            
        # interpolate the message
        message = self.context.interpolate(self.final_message, None)

        if os.path.exists(message):
            # message is a file

            destination = self.interpolate(join('${deploydir}', 
                                                os.path.split(message)[-1]))

            task = Task('display final message',
                        targets=destination,
                        commands = [
                    InFileWriter(infile=message, outfile=destination),
                    ]
                        
                        )
            Software(task, self.context).install()

            message = file(destination, 'r').read() + '-- This file may be viewed at %s --' % destination
            return message
                
        else:
            # message is a string
            return message
        

    ### functions to deal with tasks to be done as root

    def add_root_task(self, string):
        self.root_tasks.append(string)

    def add_rc_file(self, rcfile, conffile=None):
        """ 
        add a task to deal with rc files
        """

        filename = 'openplans-%s' % self.app

        newrcfile = join('${initdir}', filename)
        self.root_tasks.append('cp %s %s' % (rcfile, newrcfile))
        self.root_tasks.append('chmod u+x %s' % newrcfile)
        
        if conffile:
            newconffile = join('${confdir}', filename)
            self.root_tasks.append('cp %s %s' % (conffile, newconffile))

    def add_monit_file(self, monitfile):
        self.root_tasks.append('cp %s %s' % (monitfile,
                                             self['monitdir']))

    def write_root_tasks(self, outputfile=None, mkdirs=True):
        """ 
        write the root tasks to a file:
        rc-update add newscript default
        """
        
        if self.root_tasks:
        ### print the tasks to the file
            
            if outputfile:
                f = outputfile
            else:
                rootsetup = self.interpolate(join('${deploydir}', 'bin', 'root-setup'))
                f = file(rootsetup, 'w')        

            for i in self.root_tasks:
                print >> f, self.interpolate(i)

            if not outputfile:
                print "!-> to complete installation, as root please run '/bin/bash %s'" % rootsetup
