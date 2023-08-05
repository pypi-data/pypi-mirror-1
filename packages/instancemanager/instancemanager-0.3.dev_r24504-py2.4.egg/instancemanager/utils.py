import config
import logging
import os
import os.path
import sys

log = logging.getLogger('utils')

def makeDir(directoryName):
    log.debug("Checking presence of directory '%s'.", directoryName)
    if not os.path.exists(directoryName):
        os.mkdir(directoryName)
        log.info("Created directory '%s'.", directoryName)

def initLog():
    """Initialise the logger.
    """

    log = logging.getLogger()
    userDir = os.path.expanduser('~')
    configDir = os.path.join(userDir, config.CONFIGDIR)
    if os.path.exists(configDir):
        # Don't litter the place in logfiles, put them in the config
        # directory.
        filename = os.path.join(configDir, config.LOGFILE)
    else:
        # Doesn't exist yet, put the logfile in the current directory
        # for this one time.
        filename = config.LOGFILE
    hdlr = logging.FileHandler(filename, 'w')
    formatter = logging.Formatter('%(name)-10s %(levelname)-5s %(message)s')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)

def addConsoleLogging():
    """Add logging to the console.
    """

    log = logging.getLogger()
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)-5s %(message)s')
    hdlr.setLevel(logging.INFO)
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
