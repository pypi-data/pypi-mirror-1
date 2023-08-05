"""
utilities for starting/stopping TOPPbuild instances
"""

import os
import subprocess
import StringIO

from topp.utils.filesystem import get_args

# buildit imports
from buildit.task import Task
from buildit.commandlib import InFileWriter

join = os.path.join
piddir = '/var/run'

class StartUp(object):
    """
    poor name for a class designed to handle
    program starting, stopping, and writing utilities
    having to do so (rc scripts, monit scripts, etc.)
    """

    def __init__(self, start_command, stop_command=None, context=None):

        # assign instance variables
        self.start_command = start_command
        self.stop_command = stop_command
        self.context = context
        
    def write_rc_script(self, app_name=None, prefix=None):
        """ write an rc-file and a conf-file from a skeleton """
        # XXX this function is not yet complete
        
        # XXX should context just be required?
        # or maybe this should be reworked just to return tasks?
        if self.context is None:
            raise NotImplementedError

        args = get_args(start_command)
        

        self.context.globals['exec'] = args[0]
        self.context.globals['args'] = ''.join(args[1:])
        
        # fix arguments if they are None
        if prefix is None:
            prefix = self.context.interpolate('${deploydir}', None)
        if app_name is None:
            app_name is args[0]

        tasks = []
        # write the rc script
        'topp.build.lib/topp/build/lib/skel/topp/build/+app+'

        rcfile = join(prefix, 'bin', '%s.rc' % app_name)
        
#        tasks.append(Task('write rc file for %s' % app_name, 
#                          targets=rcfile,
#                          commands = [ 
#                    InFileWriter(infile=
#
        # write the conf script

                          


    def write_monit_script(self, name, filename=None, pidfile=None, 
                           ports=(), rcfile=None):
        if filename is None:
            f = StringIO.StringIO()
        else:
            f = file(filename, 'a')

        if pidfile:
            pfile = pidfile
        else:
            pfile = os.path.join(piddir, name + '.pid')

        print >> f, 'check process %s with pidfile' % (name, pfile)

        indent = '    '
        
        if rcfile:
            
            # assert rc file generates its own PID
            if not pidfile:
                raise NotImplementedError("pidfile must be specified if using an rcfile")

            start = "%s start" % rcfile
            stop = "%s stop" % rcfile
        else:
            start = self.start_command
            stop = self.stop_command
            if stop is None:
                stop = 'kill -s SIGTERM `cat %s`' % pfile
                            
            if not pidfile:
                shell = "/bin/bash"
                start = "%s -c 'echo $$ > %s; exec %s'" % ( shell, pfile,
                                                            start )
                stop = "%s -c '%s; rm %s'" % ( shell, stop, pfile )
                
        # write the start-stop lines
        print >> f, indent, 'start = "%s"' % start
        print >> f, indent, 'stop = "%s"' % stop            

    def start(self):
        """
        starts the process
        """
        if not hasattr(self, 'process'):            
            self.process = subprocess.Popen(get_args(self.start_comamnd))
        else:
            raise RuntimeError("process '%s' already started, pid %s" % (self.start_command, self.process.pid))

    def stop(self):
        
        if hasattr(self, 'process'):
            if self.stop_command is not None:
                subprocess.check_call(get_args(self.stop_command))
                
            for i in 'SIGTERM', 'SIGKILL':
                if self.process.poll() is not None:
                    subprocess.call(getargs("kill -%s %s" % (i, self.process.pid)))
                
            delattr(self, 'process')
            
    def __del__(self):
        if hasattr(self, 'process'):
            # finish the task if it has been started
            self.process.wait()
            
