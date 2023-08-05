import config
import logging
import os
import os.path
import sys
import popen2

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

def addConsoleLogging(level=logging.INFO):
    """Add logging to the console.
    """

    log = logging.getLogger()
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)-5s %(message)s')
    hdlr.setLevel(level)
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    
def adaptiveUnarchive(source):
    """Untar or unzip a file to the current directory.
       TODO: is using "not in gzip format" an i18n issue?
       NOTE: using extensions to decide whether a file is tar or tgz format 
         is very unreliable for Plone product archives.
       We do not test for or return overall success. 
       The next step in the operation will look for unpacked items.
    """
    tryAgain=False
    
    if source.endswith('zip'):
        os.system("unzip -qq %s" % source)
    else:
        #assume it's a gzipped tar
        r,w=popen2.popen4("tar -xzf %s" % source)
        for l in r.readlines():
            if 'not in gzip format' in l:
                tryAgain=True
                break;
        r.close(); w.close()
        if tryAgain:
            #let's see if it was just a plain tar
            os.system("tar -xf %s" % source)

def symlink(source, target, conf):
    useSvnExport = conf.configData['use_svn_export']
    if not useSvnExport:
        # Normal behaviour.
        log.debug("Symlinking %s -> %s.", source, target)
        os.symlink(source, target)
    else:
        # Svn export is needed
        command = ' '.join(['svn export', '-q', source, target])
        log.debug("Svn exporting: %s.", command)
        os.system(command)
