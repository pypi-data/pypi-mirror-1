import os
from buildit.task import Task
from commands import WorkingEnv
from commands import InFileWriterTree

def taskmaker(message, **defaults):
    """
    front end class for functions that return tasks
    """

    # arguments to override to buildit.task.Task
    defaults['name'] = message
    defaults.setdefault('namespaces', ())
    defaults.setdefault('targets',())
    defaults.setdefault('dependencies',())
    defaults.setdefault('workdir', None)

    def abstractionlayer(f):

        def wrapper(*args, **kwargs):        
            newargs={}
            
            callstack = []

            for i in defaults:
                if kwargs.has_key(i):
                    newargs[i] = kwargs.pop(i)
                else:
                    
                    # allow for callable defaults
                    if hasattr(defaults[i], '__call__'):
                        callstack.append(i)
                    else:
                        newargs[i] = defaults[i]

            for i in callstack:
                newargs[i] = defaults[i](*args, **kwargs)
                    
            newargs['commands'] = f(*args, **kwargs)
                    
            return Task(**newargs)

        return wrapper

    return abstractionlayer

@taskmaker('make a base workingenv')
def mkworkingenv(*args, **kw):
    return WorkingEnv('${deploydir}', args or None, **kw)

@taskmaker('poach eggs from installation requirements')
def poacheggs(*args):
    """
    returns a task that poaches eggs for a package
    """

    if not args:
        args = ( os.path.join('${moduledir}', 'requirements.txt') ,)

    args = ' '.join(args)

    return [ 'poach-eggs %s' % args ]


@taskmaker('copy and flesh out skeleton files')
def copyskeleton(fromdir=None, todir=None, excludes=('*.svn*', '*.pyc')):

    if not fromdir:
        fromdir=os.path.join('${moduledir}', 'skel')

    if not todir:
        todir='${deploydir}'    

    return [ InFileWriterTree(fromdir=fromdir,todir=todir, excludes=excludes) ]

@taskmaker('create directories')
def createdirectories(directories):
    return [ 'mkdir -p %s' % directory for directory in directories ]

# XXX for a root task.  not sure where this goes atm
# XXX but NOT HERE!
def setup_database(database='database', dbuser='dbuser', password='password'):
    sqlstring = """create database <<%s>>;
grant all privileges on <<%s>>.* to <<%s>>@localhost identified by '<<%s>>';
""" % ( database, database, dbuser, password )
    
    
