from buildit.task import Task

linkdeploydir = Task(
    'link the deploy directory to the dated version',
    workdir='${basedir}',
    commands=[
        'if [ -e ${app}-old ]; then unlink ${app}-old; fi',
        'if [ -e ${app} ]; then mv ${app} ${app}-old; fi',
        'ln -s ${deploydir} ${app}'
        ]
    )
    
