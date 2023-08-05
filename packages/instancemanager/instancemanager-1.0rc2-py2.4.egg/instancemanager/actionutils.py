"""Utilities for actions.py

Running zopectl/zeoctl commands, running repozo.
"""

from compat import sorted, itemgetter
from urllib2 import URLError
import config
import logging
import os
import os.path
import re
import shutil
import sys
import time
import utils
import workingenv
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
    if conf.configData['is_windows']:
        # XXX: put this in a spot where it works for multiple zeo
        # clients on Windows.
        windowsService(conf, command)
        return
    if run_for_all_clients:
        instanceDirs = conf.zeoClientDirs()
    else:
        instanceDirs = (conf.instanceDir(),)
    for instanceDir in instanceDirs:
        zopectlCommand = os.path.join(instanceDir,
                                      'bin',
                                      'zopectl')
        instanceCommand = ' '.join([zopectlCommand, command])
        log.debug("Calling zopectl:")
        log.debug(instanceCommand)
        if os.path.exists(zopectlCommand):
            logInfoAboutCtl('zope', conf, instanceCommand, instanceDir)
            os.system(instanceCommand)
        else:
            log.error("%s does not exist [skipping this step]", zopectlCommand)

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
            zeoTimeout = conf.configData['zeo_timeout']
            log.info("Sleeping %s seconds to make sure.",
                     zeoTimeout)
            time.sleep(zeoTimeout)
    else:
        log.error("%s does not exist", zeoctlCommand)

def windowsService(conf, command, options=''):
    zServer = os.path.join(conf.instanceDir(),
                      'bin',
                      'zopeservice.py')
    # win paths must be quoted as literals
    zServerPath = '\"%s\"'%zServer
    if 'install' in command:
        # install services in 'automatic startup' mode
        options = '--startup auto'
    commandLine = ' '.join([conf.configData['python'],
                        zServerPath,
                        options,
                        command])
    log.debug("Calling zope:")
    log.debug(commandLine)
    if os.path.exists(zServer):
        logInfoAboutCtl('zope', conf, command, conf.instanceDir())
        os.system(commandLine)
    else:
        log.warning("%s does not exist", zServer)

def logInfoAboutCtl(what='zope', conf=None, command=None, instanceDir=None):
    if what == 'zope':
        port = conf.zeoClientPort(instanceDir)
    if what == 'zeo':
        port = conf.zeoPort()
    # Make sure we only have the *last* element: the command itself
    command = command.split(' ', 1)[-1]
    log.info("%s: %s on port %s.",
             what,
             command,
             port)

def setUpWorkingenv(conf, instanceDir):
    if conf.configData['use_workingenv']:
        target = instanceDir
        log.info("Setting up workingenv in %s.", target)
        try:
            workingenv.main([
                    '--site-packages', # Include site-wide stuff.
                    '--home', # Needed for zope2.
                    '--no-extra', # No /src dir.
                    target, # Folder serving as workingenv base.
                    ])
        except URLError, e:
            log.error("Workingenv could not be installed because "
                      "of an URLError (%s). Most common cause: "
                      "you don't have a network connection at the "
                      "moment.", e)

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
    # WARNING: windows commands are split at whitespace, even if escaped
    if conf.configData['is_windows']:
        # command parameters that might contain whitespace (paths)
        # must be quoted (as literal strings)
        mkInstance = '\"%s\"'%mkInstance
        log.debug("windows: mkInstance is now [%s]",mkInstance)
    firstInstanceDir = instanceDirs[0]
    for instanceDir in instanceDirs:
        # instancePath will be quoted if is_windows
        instancePath = instanceDir
        if conf.configData['is_windows']:
            # win paths must be quoted (as literal strings)
            instancePath = '\"%s\"'%instanceDir
            log.debug("windows: instancePath is now [%s]",instancePath)
        params = '-u "%s:%s" -d %s' % (
            conf.configData['user'],
            conf.configData['password'],
            instancePath
            )
        if utils.isZope3(conf):
            params = params + ' -m %s' % conf.configData['z3_pw_manager']
        command = ' '.join([python, mkInstance, params])
        child_stdout, child_stdin, child_stderr = os.popen3(command)
        error = child_stderr.readlines()
        if error:
            log.error("Error creating zope instance")
            sys.exit("".join(error))
        log.info("Created zope instance in '%s'.", instanceDir)
        handleZopeConf(conf, instanceDir, useZeo=useZeo)
        if conf.configData['use_workingenv']:
            handleZopeCtlForWorkingenv(instanceDir, firstInstanceDir)
        if conf.configData['is_windows']:
            # install zope as a windows service
            windowsService(conf, 'install')
    # Set up workingenv.
    setUpWorkingenv(conf, firstInstanceDir)

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
        child_stdout, child_stdin, child_stderr = os.popen3(command)
        error = child_stderr.readlines()
        if error:
            log.error("Error creating zeo instance")
            sys.exit("".join(error))
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
        textsToChange = conf.configData['zeoConfigChanges'].keys()
        monitor_port = conf.configData['monitor_port']
        for line in oldFile:
            newLine = line
            for text in textsToChange:
                if text in line:
                    template = conf.configData['zeoConfigChanges'][text]
                    newLine = template % conf.configData
                    if 'monitor-address' in text and monitor_port == None:
                        newLine = '# ' + text + '\n'

                    log.debug("Replaced %r", line)
                    log.debug("....with %r", newLine)
                    textsToChange.remove(text)
            newFile.write(newLine)
        newFile.close()
        log.info("Changed the zeo config.")

def handleZopeConf(conf, instanceDir, useZeo=False):
    """
    IFH - this code could be more elegant, but is efficient and has the
    virtue of being 100% compatible with the existing version of IM

    ALGORITHM: parse the file once, and analyze each line on the fly.
    If we find any <xxx-server> startTag we will 'trap' lines in a list
    until we find a matching endTag, and decide how to process the list
    before writing it to the newFile.  Otherwise: we will drop thru
    and perform text/template substitutions if/where applicable.
    Under windows OS we will disable port 80 and fix the $PRODUCTS bug.
    """
    zopeConfigFile = os.path.join(instanceDir, 'etc', 'zope.conf')
    ftp_port = str(conf.configData['ftp_port'])
    port = str(conf.zeoClientPort(instanceDir))
    use_zeo_client_caches = conf.configData['use_zeo_client_caches']
    if useZeo:
        clientname = os.path.basename(instanceDir)
    else:
        clientname = conf.configData['project']
    # Put the clientname in the configData - a bit of a kludge
    conf.configData['clientname'] = clientname
    conf._processReplacements()

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

    openTagPatterns = []
    closeTagPatterns = []
    for segmentId in config.CONFSNIPPETS.keys():
        # note: each pattern is designed to always extract 3 tokens
        #   [0] is '#' if line is commented, '' if not
        #   [1] is the portNumber, the segmentType or whatever was matched
        #   [2] is extra text (anything not expected) or '' if not
        openTagPatterns.append(
            re.compile('\s*(#?)\s*<(%s)\s*>\s*(\S*)' % segmentId))
        closeTagPatterns.append(
            re.compile('\s*(#?)\s*</(%s)>\s*(\S*)'% segmentId))
        # TODO: rewrite them as verbose regexps
    trappedLines = []
    isTrapping = False
    startTag = None
    disableThisSegment = False
    configured = []
    for idx, line in enumerate(oldFile):
        lineSaved = False
        # try pattern match
        for pattern in openTagPatterns:
            reMatch = re.match(pattern, line)
            if reMatch == None:
                # no match, try next match pattern...
                continue
            matchName = str(reMatch.groups()[1])
            text = reMatch.groups()[2]
            if text and not text.startswith('#'):
                # found unexpected text, try next match pattern...
                continue
            log.debug("Opening tag pattern %r matched: %r.",
                      matchName, line)
            trappedLines = []   # start a new trap
            #trappedLines = [line]   # start a new trap
            isTrapping = True       # start trapping
            lineSaved = True        # done with this line
            startTag = matchName    # store tag name for reference
            break # Break "for" loop, get next line
        for pattern in closeTagPatterns:
            reMatch = re.match(pattern, line)
            if reMatch == None:
                # no match, try next match pattern...
                continue
            matchName = str(reMatch.groups()[1])
            if not matchName == startTag:
                log.debug("The close tag (%s) doesn't match the "
                          "opening tag (%s): %r.", startTag,
                          matchName, line)
                continue
            text = reMatch.groups()[2]
            isCommented = reMatch.groups()[0] == '#'
            if text and not text.startswith('#'):
                # found unexpected text, try next match pattern...
                continue
            log.debug("Closing tag pattern %r matched: %r.",
                      matchName, line)
            #trappedLines.append(line)   # trap this line
            # Special windows check to disable port 80
            addressPattern = re.compile('\s*(#?)\s*address\s*(\S+)\s*(\S*)')
            for thisLine in trappedLines:
                reMatch = re.match(pattern, thisLine)
                if "http-server" in startTag or startTag == 'server':
                    if matchName in ('80', '$PLONE_WEBSERVER_PORT'):
                        disableThisSegment = True
                        log.info('...disabling: %s %s', pattern,
                                 matchName)
            # Check whether to include this part.
            checkThis = config.SNIPPETCONDITIONS[matchName]
            if conf.configData[checkThis]:
                log.debug("The section %s can be included.",
                          matchName)
            else:
                log.debug("The section %s wil be excluded.",
                          matchName)
                disableThisSegment = True
            # write this segment to the newFile
            if disableThisSegment:
                newFile.write('# <%s>\n' % matchName)
                for thisLine in trappedLines:
                    newFile.write(thisLine)
                newFile.write('# </%s>\n' % matchName)
            else:
                newFile.write('<%s>\n' % matchName)
                for thisLine in trappedLines:
                    newLine = thisLine
                    for (searchThis,
                         replacement) in \
                         config.CONFSNIPPETS[matchName].items():
                        if searchThis in thisLine:
                            newLine = replacement % conf.configData
                            if newLine[-1] != '\n':
                                newLine += '\n'
                            log.debug("Replaced %r with %r.",
                                      thisLine, newLine)
                            break # Break for loop.
                    newFile.write(newLine)
                newFile.write('</%s>\n' % matchName)
            # finished.
            disableThisSegment = False
            disableThatSegment = False
            isTrapping = False          # end trapping
            lineSaved = True            # done with this line
            startTag = None             # reset for next segment
            break # Break "for" loop, get next line

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
            conf.configData['zopeConfigChanges']['products $PRODUCTS'] = '# edited by ' + \
                'instance manager:\nproducts $INSTANCE/Products\n'
        textsToChange = conf.configData['zopeConfigChanges'].keys()
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
                    template = conf.configData['zopeConfigChanges'][text]
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

def handleZopeCtlForWorkingenv(instanceDir, firstInstanceDir):
    """Add a conditional workingenv call to zopectl.
    """

    for name in ['zopectl', 'runzope']:
        fileLocation = os.path.join(instanceDir, 'bin', name)
        original = open(fileLocation, 'r').readlines()
        new = open(fileLocation, 'w')
        for line in original:
            new.write(line)
            if 'export' in line:
                new.write('if test -a %s/bin/activate; then\n'\
                          % firstInstanceDir)
                new.write('    . %s/bin/activate\n'\
                          % firstInstanceDir)
                new.write('fi\n')
        new.close()
    log.info("Modified zopectl and runzope for workingenv support.")

def backup(conf=None,
           sourceDatafs=None,
           targetDir=None,
           full=False,
           ):
    # if the backup directory doesn't exist, create it.
    if not os.path.exists(targetDir):
        log.info("%s does not exist, creating it now.",
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
    repozo = os.path.join(conf.zopeDir(), 'bin', 'repozo.py' )
    # Make sure our software home is in the PYTHONPATH
    env={}
    env['PYTHONPATH'] = "%s/lib/python" % conf.zopeDir()
    os.environ.update(env)
    command = ' '.join([python, repozo] + arguments)
    log.info("Backing up database file: %s to %s",
             sourceDatafs, targetDir)
    log.debug("Command used: %s", command)
    os.system(command)
    # We want to clean up old backups automaticly.
    # The number_of_backups var tells us how many full backups we want
    # to keep.
    log.debug("Trying to clean up old backups.")
    filenames = os.listdir(targetDir)
    log.debug("Looked up filenames in the target dir: %s found. %r.",
              len(filenames), filenames)
    num_backups = conf.numberOfBackups()
    log.debug("Max number of backups: %s.", num_backups)
    files_modtimes = []
    for filename in filenames:
        mod_time = os.path.getmtime(os.path.join(targetDir, filename))
        file_ = (filename, mod_time)
        files_modtimes.append(file_)
    # we are only interested in full backups
    fullbackups = [f for f in files_modtimes if f[0].endswith('.fs')]
    log.debug("Filtered out full backups (*.fs): %r.",
              [f[0] for f in fullbackups])
    if len(fullbackups) > num_backups and num_backups != 0:
        log.debug("There are older backups that we can remove.")
        fullbackups = sorted(fullbackups, key=itemgetter(1))
        fullbackups.reverse()
        log.debug("Full backups, sorted by date, newest first: %r.",
                  [f[0] for f in fullbackups])
        oldest_backup_to_keep = fullbackups[(num_backups-1)]
        log.debug("Oldest backup to keep: %s", oldest_backup_to_keep[0])
        last_date_to_keep = oldest_backup_to_keep[1]
        log.debug("The oldest backup we get to keep is from %s.",
                  last_date_to_keep)
        for filename, modtime in files_modtimes:
            if modtime < last_date_to_keep:
                filepath = os.path.join(targetDir, filename)
                os.remove(filepath)
                log.debug("Deleted %s.", filepath)
        log.info("Removed old backups, the latest %s full backups have "
                 "been kept.", str(num_backups))
    else:
        log.debug("Not removing backups.")
        if len(fullbackups) <= num_backups:
            log.debug("Reason: #backups (%s) <= than max (%s).",
                      len(fullbackups), num_backups)
        if num_backups == 0:
            log.debug("Reason: max # of backups is 0, so that is a "
                      "sign to us to not remove backups.")


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

    >>> item = {'develop': True}
    >>> isPureDevelopmentItem(item)
    True

    >>> item = {'develop': False}
    >>> isPureDevelopmentItem(item)
    False

    >>> item = 'develop'
    >>> isPureDevelopmentItem(item)
    False

    """
    # item can be a dict or a string
    try:
        return item.get('develop', False)
    except AttributeError:
        # Not a dict, so no pure development product
        return False

def runCommand(conf, instanceDir):
    command = conf.configData['run_command']
    if command!='':
        # run command
        log.debug("Starting command '%s'.", command)
        os.system(' '.join([command, instanceDir]))
        log.info("Command finished.")


