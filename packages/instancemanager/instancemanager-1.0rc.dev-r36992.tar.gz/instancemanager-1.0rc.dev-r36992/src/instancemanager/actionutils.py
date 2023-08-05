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
from compat import sorted, itemgetter
import re
import utils
log = logging.getLogger('actionutils')


class InvokedInVolatileDir(Exception):
    "When Product action invoked in a soon-to-be deleted directory"

class ConfigSyntaxException(Exception):
    """When a flaw is found in the zope.conf syntax"""

def trapUsageWithinVolatileDir(target):
    currentDir = os.getcwd()
    if currentDir.startswith(target):
        log.error("""Removing parent of current directory""")
        raise InvokedInVolatileDir, "Use command outside %s" % target

def runZopectl(conf, command):
    # It only makes sense for *one* zope to be started in the
    # foreground or in debug mode.  Probably for others too, but those
    # are the main ones.
    log.info(command)
    run_for_all_clients = True
    for commandname in ('fg', 'foreground', 'debug', 'test', 'run'):
        if command.startswith(commandname):
            run_for_all_clients = False
    if run_for_all_clients:
        instanceDirs = conf.zeoClientDirs()
    if conf.configData['is_windows']:
        windowsService(conf, command)
    else:
        instanceDirs = (conf.instanceDir(),)
    for instanceDir in instanceDirs:
        zopectlCommand = os.path.join(instanceDir, 
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
    zeoCommand = ' '.join([zeoctlCommand, command])
    log.debug("Calling zeo:")
    log.debug(zeoCommand)
    if os.path.exists(zeoctlCommand):
        logInfoAboutCtl('zeo', conf, zeoCommand)
        os.system(zeoCommand)
        if command == 'status':
            monitor_port = conf.configData['monitor_port']
            if monitor_port is not None:
                log.info('Querying zeo monitor at port %s', monitor_port)
                outfile = 'instancemanager_monitor.txt'
                os.system('wget --tries=1 --output-file=/dev/null --output-document=%s 1 http://localhost:%s && cat %s && rm %s' % (outfile, monitor_port, outfile, outfile))
        else:
            # Be sure that the zeo server started or stopped.
            time.sleep(10)
    else:
        log.error("%s does not exist", zeoctlCommand)

def windowsService(conf, command, options=''):
    zServer = os.path.join(conf.instanceDir(),
                      'bin',
                      'zopeservice.py')
    if 'install' in command:
        # install services in 'automatic startup' mode
        options = '--startup auto'
    commandLine = ' '.join([conf.configData['python'],
                        zServer,
                        options,
                        command])
    log.debug("Calling zope:")
    log.debug(commandLine)
    if os.path.exists(zServer):
        logInfoAboutCtl('zope', conf, command)
        os.system(commandLine)
    else:
        log.warning("%s does not exist", zServer)

def logInfoAboutCtl(what='zope', conf=None, command=None):
    if what == 'zope':
        port = conf.zeoClientPort(conf.instanceDir())
    if what == 'zeo':
        port = conf.zeoPort()
    # Make sure we only have the *last* element: the command itself
    command = command.split(' ', 1)[-1]
    log.info("%s: %s on port %s.",
             what,
             command,
             port)

def createInstance(conf, purge=False):
    useZeo = conf.configData['use_zeo']
    python = conf.configData['python']
    instanceDirs = conf.zeoClientDirs()
    zeoDir = conf.zeoDir()
    if purge:
        if conf.configData['is_windows']:
            # uninstall the service (releases file locks)
            windowsService(conf, 'remove')
        # Copy the instanceDirs list.
        dirs_to_remove = [i for i in instanceDirs]
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
    command = conf.mkZopeInstanceCommand()
    mkInstance = os.path.join(conf.zopeDir(),
                              'bin',
                              command)
    for instanceDir in instanceDirs:
        params = conf.instanceParams()
        command = ' '.join([python, mkInstance, params])
        os.system(command)
        log.info("Created zope instance in '%s'.", instanceDir)
        handleZopeConf(conf, useZeo=useZeo)
        if conf.configData['is_windows']:
            # install zope as a windows service
            windowsService(conf, 'install')

    # Zeo server
    if useZeo:
        command = conf.mkZeoInstanceCommand()
        mkInstance = os.path.join(conf.zopeDir(),
                                  'bin',
                                  command)
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
        monitor_port = conf.configData['monitor_port']
        for line in oldFile:
            newLine = line
            for text in textsToChange:
                if text in line:
                    template = config.ZEOCONFIGCHANGES[text]
                    newLine = template % conf.configData
                    if 'monitor-address' in text and monitor_port == None:
                        newLine = '# ' + text + '\n'    

                    log.debug("Replaced %r", line)
                    log.debug("....with %r", newLine)
                    textsToChange.remove(text)
            newFile.write(newLine)
        newFile.close()
        log.info("Changed the zeo config.")

def handleZopeConf(conf, useZeo=False):
    """
    IFH - this code could be more elegant, but is efficient and has the
    virtue of being 100% compatible with the existing version of IM

    ALGORITHYM: parse the file once, and analyze each line on the fly.
    If we find any <xxx-server> startTag we will 'trap' lines in a list
    until we find a matching endTag, and decide how to process the list
    before writing it to the newFile.  Otherwise: we will drop thru
    and perform text/template substitutions if/where applicable.
    Under windows OS we will disable port 80 and fix the $PRODUCTS bug.
    """
    instanceDir = conf.instanceDir()
    zopeConfigFile = os.path.join(instanceDir, 'etc', 'zope.conf')
    ftp_port = str(conf.configData['ftp_port'])
    port = str(conf.configData['port'])
    use_zeo_client_caches = conf.configData['use_zeo_client_caches']
    if useZeo:
        clientname = os.path.basename(instanceDir)
    else:
        clientname = conf.configData['project']
    # Put the clientname in the configData
    conf.configData['clientname'] = clientname
    premadeZopeconf = conf.zopeconf()
    log.debug('premadeZopeconf: %s' ,premadeZopeconf)
    if os.path.exists(premadeZopeconf):
        source = premadeZopeconf
        target = zopeConfigFile
        shutil.copy(source, target)
        log.info("Copied over premade zope.conf from %s.", source)
        log.debug("Copied it to %s.", target)
        return
    log.info("Replacing parts of '%s'.", zopeConfigFile)
    oldFile = open(zopeConfigFile, 'r').readlines()
    newFile = open(zopeConfigFile, 'w')

    # we need to parse the .conf and trap the following segments:
    segmentTypes = ['server','http-server','ftp-server','webdav-source-server']

    # set up dict of re patterns
    patterns = {}
    # note: each pattern is designed to always extract 3 tokens
    #   [0] is '#' if line is commented, '' if not
    #   [1] is the portNumber, the segmentType or whatever was matched
    #   [2] is extra text (anything not expected) or '' if not
    patterns['openTag'] = re.compile('\s*(#?)\s*<([\w-]*server\s*)>\s*(\S*)')
    patterns['closeTag']  = re.compile('\s*(#?)\s*</([\w-]*server)>\s*(\S*)')
    patterns['address'] = re.compile('\s*(#?)\s*address\s*(\S+)\s*(\S*)')
    trappedLines = []
    isTrapping = False
    startTag = None
    disableThisSegment = False
    configured = []
    for idx, line in enumerate(oldFile):
        lineSaved = False
        for pattern in patterns.keys():
            reMatch = re.match(patterns[pattern],line)
            if reMatch == None:
                # no match, try next match pattern...
                continue
            text = reMatch.groups()[2]
            if text and not text.startswith('#'):
                # found unexpected text, try next match pattern...
                continue
            matchName = str(reMatch.groups()[1])
            isCommented = reMatch.groups()[0] == '#'
            log.debug("Found %s '%s':  (on line %s, commented = %s)",
                    pattern, matchName,  idx+1,  isCommented)

            if pattern == 'openTag' and matchName in segmentTypes:
                trappedLines = [line]   # start a new trap
                isTrapping = True       # start trapping
                lineSaved = True        # done with this line
                startTag = matchName    # store tag name for reference
                break   # get next line

            elif pattern == 'closeTag' and matchName == startTag:
                trappedLines.append(line)   # trap this line
                isTrapping = False          # end trapping
                lineSaved = True            # done with this line
                startTag = None             # reset for next segment
                # write this segment to the newFile
                for thisLine in trappedLines:
                    if disableThisSegment and not thisLine.startswith("#"):
                        thisLine = "# " + thisLine
                    newFile.write(thisLine)
                disableThisSegment = False
                disableThatSegment = False
                break  # get next line

            elif pattern == 'address' and startTag is not None:
                # matchName contains portNumber (or %define var if windows)
                if "http-server" in startTag or startTag == 'server':
                    if matchName in ('8080', '$ZOPE_MANAGEZODB_PORT'):
                        line = line.replace(matchName, port)
                        log.info('...changed %s %s to: %s',
                                pattern, matchName, port)
                    elif matchName in ('80', '$PLONE_WEBSERVER_PORT'):
                        disableThisSegment = True
                        log.info('...disabling: %s %s', pattern, matchName)
                elif 'webdav-source-server' in startTag:
                    # IFH todo - could be handled like the ftp port
                    pass

                # trap this line
                trappedLines.append(line)
                lineSaved = True
                break   # get next line

        if lineSaved:
            continue   # get next line
        elif isTrapping:
            # but not yet saved...
            trappedLines.append(line)
            continue   # now get next line

        # ok... if we get this far, we need to check the line for any of
        # our text substitutions before writing a result line to newFile
        # note: since the 'address' lines should have been trapped above,
        # the 'address' entries in CONFIGCHANGES will not matter
        if conf.configData['is_windows']:
            # we need to find and fix the windows $PRODUCTS bug
            config.CONFIGCHANGES['products $PRODUCTS'] = '# edited by ' + \
                'instance manager:\nproducts $INSTANCE/Products\n'
        textsToChange = config.CONFIGCHANGES.keys()
        newLine = line
        for text in textsToChange:
            if text in line:
                if text in configured:
                    if not text.startswith("#"):
                        newLine = "# " + newLine
                    continue # Already set this line
                else:
                    configured.append(text)
                    log.debug('Changing %s on line %s:',text, 1+idx)
                    template = config.CONFIGCHANGES[text]
                    newLine = template % conf.configData
                    log.debug('%s', newLine)
        newFile.write(newLine)
    newFile.close()

    if useZeo:
        # Add Zeo snippet in the zope.conf for this zeo client.
        oldFile = open(zopeConfigFile, 'r').readlines()
        newFile = open(zopeConfigFile, 'w')
        skip = False

        z2start = '<zodb_db main>'
        z3start = '<zodb>'
        z2end = '</zodb_db>'
        z3end = '</zodb>'
        for line in oldFile:
            newLine = line
            if line.startswith(z2start) or line.startswith(z3start):
                skip = True
            if not skip:
                newFile.write(newLine)
            if line.startswith(z2end) or line.startswith(z3end):
                skip = False
        if use_zeo_client_caches:
            zeo_client_line = 'client %s' % clientname
        else:
            zeo_client_line = '# client zeo1'
        if utils.isZope3(conf):
            snippet = config.Z3ZEOSNIPPET
        else:
            snippet = config.ZEOSNIPPET

        newFile.write(snippet % {
                'zeoport': conf.zeoPort(),
                'zeo_client_line': zeo_client_line,
                })
    log.info("Saved the zope config.")

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
    # We want to clean up old backups automaticly.
    # The number_of_backups var tells us how many full backups we want
    # to keep.
    filenames = os.listdir(targetDir)
    num_backups = conf.numberOfBackups()
    files_modtimes = []
    for filename in filenames:
        mod_time = os.path.getmtime(os.path.join(targetDir, filename))
        file = (filename, mod_time)
        files_modtimes.append(file)
    # we are only interested in full backups 
    fullbackups = [f for f in files_modtimes if f[0].endswith('.fs') ]
    if len(fullbackups) > num_backups and num_backups != 0:
        fullbackups = sorted(fullbackups, key=itemgetter(1))
        last_date_to_keep = fullbackups[(num_backups-1)][1]
        deleted_files = []
        for filename, modtime in files_modtimes:
            if modtime < last_date_to_keep:
                filepath = os.path.join(targetDir, filename)
                os.remove(filepath)
                deleted_files.append(filepath)
        log.info("Removed old backups, the latest %s full backups are kept.",
            str(num_backups))
        log.debug("Delete backup files older than %s.\nfiles deleted:\n%s",
            last_date_to_keep, '\n   '.join(deleted_files))
    
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

def runCommand(conf, instanceDir):
    command = conf.configData['run_command']
    if command!='' and os.path.isfile(command):
        # run command
        log.debug("Starting command '%s'.", command)
        os.system(' '.join([command, instanceDir]))
        log.info("Command finished.")


