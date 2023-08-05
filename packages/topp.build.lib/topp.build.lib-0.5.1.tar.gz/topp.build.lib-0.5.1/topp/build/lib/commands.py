"""
buildit commands for topp's build library
"""

import os
import sys
import re
import fnmatch
import subprocess

from buildit.commandlib import Download, ShellCommand
from buildit.commandlib import InFileWriter

from topp.utils.uri import is_url
from topp.utils.wenvutils import activate

join = os.path.join

class WorkingEnv(ShellCommand):
    """ make and activate a workingenv """

    def __init__(self, path, options=None, log_file=None):
        self.path = path
        self.options = options
        self.log_file = log_file

    def represent(self, task):
        return task.interpolate(self.path)

    def check(self, task):
        return self.represent(task)

    def execute(self, task):

        wenv_location = self.represent(task)

        # activate the workingenv
        command = ['workingenv', wenv_location ]

        if self.options:
            for i in self.options:
                command.append(task.interpolate(i))
        if self.log_file:
            command.extend(
                ['--log-file', task.interpolate(self.log_file)])

        process = subprocess.Popen(command)
        process.wait()
        if process.returncode:
            raise OSError(
                "Command %r failed with exit code %s"
                % (command, process.returncode))

        activate(wenv_location)

        return 0

class TarballExtractor(ShellCommand):
    """ expand tarballs """

    def __init__(self, tarfile, path=None):
        self.tarfile = tarfile
        self.path = path

    def represent(self, task):
        return task.interpolate(self.tarfile)

    def check(self, task):
        return self.represent(task)

    def execute(self, task):
        tarfile = self.represent(task)

        # if the tarball is a url, download it
        if is_url(tarfile):
            short_name = tarfile.split('/')[-1]
            download = Download(filename=short_name, 
                                url=self.tarfile)

            if download.check(task):
                download.execute(task)
                tarfile = short_name
        
        if not os.path.exists(tarfile):
            return 1

        # attempt to find the filetype based on extension
        # could also use flags in tar for this
        extdict = { '.tar.gz': 'zcat',
                    '.tgz': 'zcat',
                    '.tar.bz2': 'bunzip2 --stdout',
                    '.tar.Z': 'uncompress -c'
                    }

        # build the command line
        for i in extdict:
            if tarfile.endswith(i):
                cmdline = extdict[i].split()
                cmdline.append(tarfile)
                decompress = subprocess.Popen(cmdline,
                                              stdout=subprocess.PIPE)
                stdin = decompress.stdout
                break
        else:
            cat = subproces.Popen(['cat', tarfile], 
                                  stdout=subprocess.PIPE)
            stdin = cat.stdout
        
        cmdline = ['tar', 'xv']
        if self.path:
            cmdline += ['-C', self.path]

        untar = subprocess.Popen(cmdline, stdin=stdin, 
                                 stdout=subprocess.PIPE)

        self.output = untar.communicate()[0] # keep stdout

        print self.output

        return untar.poll()
            
class DistUtilInstaller(TarballExtractor):
    """ 
    installs software from a tarball with a setup.py in a subdirectory 
    """

    def execute(self, task):
        code = TarballExtractor.execute(self, task)
        if code: 
            return code

        for i in self.output.split('\n'):
            j = i.split(os.path.sep)
            if len(j) == 2:
                if j[-1] == 'setup.py':
                    pwd = os.getcwd()
                    os.chdir(j[0]);
                    install = subprocess.Popen(('python', j[-1], 'install'))
                    install.communicate()
                    os.chdir(pwd)
                    break
        else:
            print('no setup.py files found')
            return 1

        return 0

class EasyInstall(ShellCommand):
    """
    easy_install python software
    """
    
    def __init__(self, package, options=None, version=None):
        if options:
            opts = ['--%s=%s'%(opt, val) 
                    for opt, val in options.items()]
            self.options = ' '.join(opts)
            if options.get('editable', False):
                self.version='dev'

        else:
            self.options = ''

        self.package = package
        self.version = version

    def represent(self, task):
        cmd = 'easy_install %s %s' %(self.options, self.package)
        if self.version:
            cmd = '%s==%s' %(cmd, self.version)
        return cmd

    check = represent

class InstallRequirements(ShellCommand):
    """
    easy_install python software using a requirements.txt file
    in the manner of and using workingenv
    """

    def __init__(self, *requirements, **kw):
        self.requirements = requirements
        if 'log_file' in kw:
            self.log_file = kw.pop('log_file')
        else:
            self.log_file = None
        if kw:
            raise TypeError(
                "Unexpected keyword arguments: %r" % kw)

    def represent(self, task):
        return 'easy_install <- ' + str(self.targets(task))

    def targets(self, task):
        return [ task.interpolate(i) for i in self.requirements ]

    def execute(self, task):
        
        # interpolate the requirements
        requirements = self.targets(task)
        
        # parse the requirements files with workingenv
        # (some of this is borrowed from PoachEggs)
        import workingenv
        logger = workingenv.Logger([(1, sys.stdout)])
        if self.log_file:
            log_file = task.interpolate(self.log_file)
            log_dir = os.path.dirname(os.path.abspath(log_file))
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            f = open(log_file, 'a')
            logger.consumers.append((logger.LEVELS[0], f))
        settings = workingenv.Settings()        
        requirements_lines = workingenv.read_requirements(logger, 
                                                          requirements)
        plan = workingenv.parse_requirements(logger, requirement_lines, 
                                             settings)

        # build the command line
        cmdline = [ 'easy_install' ]
        if settings.find_links:
            cmdline.append('-f')
            cmdline += settings.find_links
            cmdline += plan

        # easy_install the software
        install = subprocess.Popen(cmdline)
        return install.poll()
        
                    
class InFileWriterTree(ShellCommand):
    """
    install a tree of files with substitution
    """

    def __init__(self, fromdir=None, todir=None, excludes=('*.svn*', '*.pyc',), ext='.in'):
        self.fromdir = fromdir
        self.todir = todir
        self.excludes = excludes
        self.ext = ext

    def represent(self, task):
        return "Writing files: %s; and directories: %s" % tuple([ str(i) for i in self.targets(task) ])

    def check(self, task):
        fromdir, todir = [ task.interpolate(i) 
                           for i in self.fromdir, self.todir ]

        for i in fromdir, todir:
            if not os.path.exists(fromdir):
                return False

        return self.represent(task)

    def included(self, target):
        for exclude in self.excludes:
            if fnmatch.fnmatch(target, exclude):
                return False
        return True

    def targets(self, task):
        ret_files = []
        ret_dirs = []
        
        def process(lst):
            for f in lst:
                if not self.included(f):
                    lst.remove(f)
            return [ os.path.join(directory, j) for j in lst ]
        
        directories = []
        fromdir = task.interpolate(self.fromdir)
        for root, dirs, files in os.walk(fromdir):
            directory = root.split(fromdir,1)[-1].lstrip(os.path.sep)
            ret_files.extend(process(files))
            ret_dirs.extend(process(dirs))

        return ret_files, ret_dirs

    def makedirs(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def execute(self, task):
        fromdir, todir = [ task.interpolate(i) 
                           for i in self.fromdir, self.todir ]
        
        # regular expressions for file replacement
        fileregex = re.compile('\+[^+]*\+')
        def filenamesubstitutor(rematch):
            match = rematch.group()[1:-1] # ignore the +s
            return task.interpolate('${' + match + '}')

        targets, directories = self.targets(task)

        for i in directories:
            dest = re.subn(fileregex, filenamesubstitutor, i)[0]
            self.makedirs(join(todir, i))

        for i in targets:
            
            # substitute variables in outfiles
            outfile = re.subn(fileregex, filenamesubstitutor, i)[0]
            if outfile.endswith(self.ext):
                outfile = outfile[:-len(self.ext)]
            
            # write the file
            filewriter = InFileWriter(infile=join(fromdir, i),
                                      outfile=join(todir, outfile))
            if filewriter.check(task):
                filewriter.execute(task)

        return 0
                
