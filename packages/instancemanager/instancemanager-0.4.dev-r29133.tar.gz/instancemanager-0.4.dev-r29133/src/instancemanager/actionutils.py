"""Utilities for actions.py

Running zopectl/zeoctl commands, running repozo.
"""

import config
import sys
import os
import os.path
import logging
import shutil
import time
log = logging.getLogger('actionutils')

class InvokedInVolatileDir(Exception):
    "When Product action invoked in a soon-to-be deleted directory"

def trapUsageWithinVolatileDir(target):
    currentDir = os.getcwd()
    if currentDir.startswith(target):
        log.error("""Removing parent of current directory""")
        raise InvokedInVolatileDir, "Use command outside %s" % target

def runZopectl(conf, command):
    zopectlCommand = os.path.join(conf.instanceDir(), 
                                  'bin',
                                  'zopectl')
    command = ' '.join([zopectlCommand, command])
    log.debug("Calling zope:")
    log.debug(command)
    if os.path.exists(zopectlCommand):
        logInfoAboutCtl('zope', conf, command)
        os.system(command)
    else:
        log.error("%s does not exist", zopectlCommand)

def runZeoctl(conf, command):
    if not conf.configData['use_zeo']:
        # We don't have any business here, return
        return
    zeoctlCommand = os.path.join(conf.zeoDir(), 
                                  'bin',
                                  'zeoctl')
    command = ' '.join([zeoctlCommand, command])
    log.debug("Calling zeo:")
    log.debug(command)
    if os.path.exists(zeoctlCommand):
        logInfoAboutCtl('zeo', conf, command)
        os.system(command)
        # Be sure that the zeo server started or stopped.
        time.sleep(10)
    else:
        log.error("%s does not exist", zeoctlCommand)

def logInfoAboutCtl(what='zope', conf=None, command=None):
    if what == 'zope':
        port = conf.configData['port']
    if what == 'zeo':
        port = conf.zeoPort()
    # Make sure we only have the second part if it is a long command.
    command = command.split(' ')[1]
    log.info("%s: %s on port %s.",
             what,
             command,
             port)

def backup(conf=None,
           sourceDatafs=None, 
           targetDir=None,
           full=False,
           ):
    # if the backup directory doesn't exist, create it.
    if not os.path.exists(targetDir):
        log.info("%s does not exists, creating it now.",
                 targetDir)
        os.makedirs(targetDir)
    arguments = []
    arguments.append('--backup')
    arguments.append('--file=%s' % sourceDatafs)
    arguments.append('--repository=%s' % targetDir)
    if full:
        arguments.append('--full')
        # By default, there's an incremental backup, if possible.
    python = conf.configData['python']
    repozo = os.path.join(conf.zopeDir(), 'bin','repozo.py' )
    # Make sure our software home is in the PYTHONPATH
    env={}
    env['PYTHONPATH']="%s/lib/python" % conf.zopeDir()
    os.environ.update(env)
    command = ' '.join([python, repozo] + arguments)
    log.info("Backing up database file: %s to %s",
             sourceDatafs, targetDir)
    log.debug("Command used: %s",
              command)
    os.system(command)


def restore(conf=None,
            sourceDir=None,
            fromTime=None,
            ):
    # Lets make sure zope is stopped
    useZeo = conf.configData['use_zeo']
    if useZeo:
        runZopectl(conf, 'stop')
        runZeoctl(conf, 'stop')
    else:
        runZopectl(conf, 'stop')
    targetDatafs = conf.databasePath()
    arguments = []
    arguments.append('--recover')
    arguments.append('--output=%s' % targetDatafs)
    arguments.append('--repository=%s' % sourceDir)
    if fromTime:
        arguments.append('--date=%s' % fromTime)
    # Now we have to remove the temp files, if they exist
    for fileName in config.DATABASE_TEMPFILES:
        file = os.path.join(conf.databaseBaseDir(), fileName)
        if os.path.exists(file):
            log.debug("Removing temporary database file: %s" % file)
            os.remove(file)
    python = conf.configData['python']
    repozo = os.path.join(conf.zopeDir(), 'bin','repozo.py' )
    # make sure our software home is in the PYTHONPATH
    env={}
    env['PYTHONPATH']="%s/lib/python" % conf.zopeDir()
    os.environ.update(env)
    command = ' '.join([python, repozo] + arguments)
    log.info("Restoring database file %s from %s.",
             targetDatafs, sourceDir)
    log.debug("Command used: %s",
              command)
    os.system(command)

