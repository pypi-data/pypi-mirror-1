""" 
tasks for checking and setting port availability
"""

from topp.utils.filesystem import which
from buildit.task import Task

# nmapport = Task(
#     'checking port availability via nmap',
#     commands = [ 'nmap localhost -p ${port} | grep "${port}.*closed"' ],
#     )

# checkport = Task(
#     'checking port availability via ports file',
#     workdir='${basedir}',
#     commands = [
#         'touch ${portsfile}',
#         '! grep -v "^${port}[[:space:]]${app}$" ${portsfile} | grep "^${port}[[:space:]]"'
#         ]
#     )

# setport = Task(
#     'setting port number',
#     workdir='${basedir}',
#     commands = [
#         'cp ${portsfile} ${portsfile}.TMP',
#         'echo "${port} ${app}" >> ${portsfile}.TMP',
#         'sort -g ${portsfile}.TMP | uniq > ${portsfile}',
#         'rm ${portsfile}.TMP'
#         ],
#     dependencies=(checkport,)
#     )

def getporttasks(variables, portsfile=True):
    nmap = which('nmap')

    retval = []

    for i in variables:
        if nmap:
            retval.append(Task(
                    'checking port availability via nmap',
                    commands = [ 'nmap localhost -p ${%s} | grep "${%s}.*closed"' % ( i, i) ],
                    ))

        if portsfile:
            app = ''.join([ j.strip('_') for j in i.split('port') ])
            if not app:
                app = '${app}'
                
                retval.append(Task(
                        'checking port availability via ports file',
                        workdir='${basedir}',
                        commands = [
                            'touch ${portsfile}',
                            '! grep -v "^${%s}[[:space:]]%s$" ${portsfile} | grep "^${%s}[[:space:]]"' % (i, app, i)
                            ]))
                
                retval.append(Task(
                        'setting port number',
                        workdir='${basedir}',
                        commands = [
                            'cp ${portsfile} ${portsfile}.TMP',
                            'echo "${%s} %s" >> ${portsfile}.TMP' % (i,app),
                            'sort -g ${portsfile}.TMP | uniq > ${portsfile}',
                            'rm ${portsfile}.TMP'
                            ],
                        dependencies=(retval[len(retval) -1],)
                        ))
        
    return retval
                    
    
