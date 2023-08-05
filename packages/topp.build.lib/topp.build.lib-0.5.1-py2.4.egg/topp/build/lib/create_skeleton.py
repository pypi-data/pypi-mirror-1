import os
import sys
import StringIO
import re
import optparse
import pkg_resources
import subprocess

from buildit.task import Task
from buildit.context import Context
from buildit.context import Software

from topp.utils.modules import module_directory
from utils import appname
from commands import InFileWriterTree


join = os.path.join

def create_skeleton(app_name=None, ignore_exists=False):
    """
    create a skeleton directory for a new app to be deployed
    """

    ### find the application name

    if app_name is None:
        if len(sys.argv[1:]) == 1:
            app_name = sys.argv[1]
        else:
            print "Usage: %s [app]" % sys.argv[0]
            return

    ### make the skeleton directory
    skel_dir = appname(app_name)
    if os.path.exists(skel_dir) and not ignore_exists:
        print "%s already exists" % skel_dir
        return

    ### use a temporary file for the context
    context_string = "[globals]\napp = %s\n" % app_name
    name = StringIO.StringIO(context_string)

    context = Context(name)
    context.globals['deploydir'] = '<<deploydir>>'
    context.globals['app_upper'] = app_name.upper()
    context.globals['args'] = ''

    # variables to interpolate as themselves
    reinterpretables = [ 'user', 'group', 'piddir', 'exec', ]
    for i in reinterpretables:
        context.globals[i] = '<<%s>>' % i
    
    context.globals['builder'] = 'TOPPbuild'
    context.globals['apps'] = "app"
        
    ### 
    task = Task(
        'write the files for the skeleton directory',
        workdir='${cwd}',
        commands = [ 
            InFileWriterTree(fromdir=join(module_directory(appname('lib')),
                                          'skel'), 
                             todir=skel_dir),
            ]
        )
    
    Software(task, context).install()

dist = pkg_resources.get_distribution('topp.build.lib')

parser = optparse.OptionParser(
    usage="%prog APP_NAME",
    version="%s from %s" % (dist, dist.location),
    description="Create a new distribution with the given name")

parser.add_option(
    '--add-to-svn',
    dest="add_to_svn",
    action="store_true",
    help="Add to the topp subversion repository")

TOPP_BASE_SVN = "https://svn.openplans.org/svn/build/"

app_name_re = re.compile(r"^[a-z][a-z0-9_\-.]+$")

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    options, args = parser.parse_args(args)
    if not len(args) == 1:
        parser.print_help()
        sys.exit(2)
    app_name = args[0]
    if not app_name_re.search(app_name):
        print "Not a valid name: %r" % app_name
        sys.exit(3)
    full_name = "topp.build.%s" % app_name
    if options.add_to_svn:
        add_to_svn(full_name)
    create_skeleton(app_name, ignore_exists=options.add_to_svn)
    if options.add_to_svn:
        add_all_to_svn(full_name)

def add_to_svn(build_name):
    base = TOPP_BASE_SVN + build_name
    trunk = base + '/trunk'
    dirs = [
        base,
        trunk,
        base + '/tags',
        base + '/branches']
    for dir in dirs:
        # FIXME: I guess ideally I'd use buildit to do this call?
        command = ['svn', 'mkdir', '-m',
                   'New build', dir]
        print ' '.join(command)
        subprocess.call(command)
    command = ['svn', 'co', trunk, build_name]
    print ' '.join(command)
    subprocess.call(command)

def add_all_to_svn(build_name):
    command = ['svn', 'add'] + [
        os.path.join(build_name, fn)
        for fn in os.listdir(build_name)]
    print ' '.join(command)
    subprocess.call(command)
    
