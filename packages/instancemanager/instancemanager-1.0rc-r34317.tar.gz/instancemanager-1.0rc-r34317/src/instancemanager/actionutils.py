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

def createInstance(conf, purge=False):
        useZeo = conf.configData['use_zeo']
        python = conf.configData['python']
        instanceDir = conf.instanceDir()
        zeoDir = conf.zeoDir()
        if purge:
            dirs_to_remove = [instanceDir]
            if useZeo:
                dirs_to_remove.append(zeoDir)
            for dir in dirs_to_remove:
                try:
                    trapUsageWithinVolatileDir(dir)
                except InvokedInVolatileDir, error:
                    log.error(error)
                    sys.exit(1)
                if os.path.exists(dir):
                    shutil.rmtree(dir)
                    log.debug("Removed instance/zeo dir '%s'.", dir)
        # Zope server
        mkInstance = os.path.join(conf.zopeDir(),
                                  'bin',
                                  'mkzopeinstance.py')
        params = '-u %s:%s -d %s' % (
            conf.configData['user'],
            conf.configData['password'],
            instanceDir,
            )
        command = ' '.join([python, mkInstance, params])
        os.system(command)
        log.info("Created zope instance in '%s'.", instanceDir)
        handleZopeConf(conf, useZeo=useZeo)
        # Zeo server
        if useZeo:
            mkInstance = os.path.join(conf.zopeDir(),
                                      'bin',
                                      'mkzeoinstance.py')
            params = '%s %s' % (
                zeoDir,
                conf.zeoPort(),
                )
            command = ' '.join([python, mkInstance, params])
            os.system(command)
            log.info("Created zeo instance in '%s'.",
                     conf.zeoDir())
            zeoconfigFile = os.path.join(zeoDir, 'etc', 'zeo.conf')
            premadeZeoconf = conf.zeoconf()
            if os.path.exists(premadeZeoconf):
                source = premadeZeoconf
                target = zeoconfigFile
                log.info("Copying over premade zeo.conf from %s.", source)
                shutil.copy(source, target)
                log.debug("Copied it to %s.", target)
                return
            log.debug("Replacing parts of '%s'.", zeoconfigFile)
            oldFile = open(zeoconfigFile, 'r').readlines()
            newFile = open(zeoconfigFile, 'w')
            textsToChange = config.ZEOCONFIGCHANGES.keys()
            for line in oldFile:
                newLine = line
                for text in textsToChange:
                    if text in line:
                        template = config.ZEOCONFIGCHANGES[text]
                        newLine = template % conf.configData
                        log.debug("Replaced %r", line)
                        log.debug("....with %r", newLine)
                        textsToChange.remove(text)
                newFile.write(newLine)
            newFile.close()
            log.info("Changed the zeo config.")


             
def handleZopeConf(conf, useZeo=False):
    instanceDir = conf.instanceDir()
    zopeConfigFile = os.path.join(instanceDir, 'etc', 'zope.conf')
    ftp_port = conf.configData['ftp_port']
    port = conf.configData['port']
    premadeZopeconf = conf.zopeconf()
    if os.path.exists(premadeZopeconf):
        source = premadeZopeconf
        target = zopeConfigFile
        shutil.copy(source, target)
        log.info("Copied over premade zope.conf from %s.", source)
        log.debug("Copied it to %s.", target)
        return
    log.debug("Replacing parts of '%s'.", zopeConfigFile)
    oldFile = open(zopeConfigFile, 'r').readlines()
    newFile = open(zopeConfigFile, 'w')
    textsToChange = config.CONFIGCHANGES.keys()
    for line in oldFile:
        newLine = line
        for text in textsToChange:
            if text in line:
                template = config.CONFIGCHANGES[text]
                newLine = template % conf.configData

                # Please fix me! I am a dirty hack to allow for
                # automated upgrades to play nice. What I should do is
                # enable the directives e.g. <ftp-server> if a ftp_port
                # is given and comment out the directive if ftp_port is
                # None.
                if '8080' in text and conf.configData['port'] == None:
                    newLine = '# ' + text + '\n'    
                if '8021' in text and ftp_port == None:
                    newLine = '# ' + text + '\n'
                if "<ftp-server>" in line and ftp_port == None:
                    newLine = "#<ftp-server>"
                elif "<ftp-server>" in line and ftp_port != None:
                    newLine = "<ftp-server>"
                if "</ftp-server>" in line and ftp_port == None:
                    newLine = "#</ftp-server>"
                elif "</ftp-server>" in line and ftp_port != None:
                    newLine = "</ftp-server>"
                log.debug("Replaced %r", line)
                log.debug("....with %r", newLine)
                textsToChange.remove(text)
        newFile.write(newLine)
    newFile.close()
    if useZeo:
        oldFile = open(zopeConfigFile, 'r').readlines()
        newFile = open(zopeConfigFile, 'w')
        skip = False
        SKIPSTART = '<zodb_db main>'
        SKIPEND = '</zodb_db>'
        for line in oldFile:
            newLine = line
            if line.startswith(SKIPSTART):
                skip = True
            if not skip:
                newFile.write(newLine)
            if line.startswith(SKIPEND):
                skip = False
        newFile.write(config.ZEOSNIPPET % {
                'zeoport': conf.zeoPort()
                })
    log.info("Changed the zope config.")

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

def adaptListForDevelopment(config, itemList, simple=True):
    """Return a only items that are valid for this machine.

    If simple is True, return only items as strings.
    If simple is False, return dicts if available.
    """
    if config.configData['development_machine']:
        # This is a development machine, so everything goes.
        safeItems = itemList
    else:
        # This is not a development machine, so only return items that
        # are not purely for development.
        safeItems = [item for item in itemList
                     if not isPureDevelopmentItem(item)]
    if simple:
        simpleList = []
        for item in safeItems:
            try:
                name = item.get('source')
            except AttributeError:
                name = item
            simpleList.append(name)
        safeItems = simpleList
    return safeItems

def isPureDevelopmentItem(item):
    """Return True if this item is only meant for development machines.
    """
    # item can be a dict or a string
    try:
        return item.get('develop', False)
    except AttributeError:
        # Not a dict, so no pure development product
        return False
